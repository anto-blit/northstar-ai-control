"""Authority and the harmless mailbox effect share a SQLite transaction.

Workers receive opaque claims, never a database handle through the HTTP API.
The host account and filesystem remain trusted; this is not OS isolation.
"""
from contextlib import closing, contextmanager
from hashlib import sha256
import json
from pathlib import Path
import secrets
import sqlite3


MODES = ("cooperative_cancel", "transactional_cancel", "epoch_fence")
MAX_OUTSTANDING = 128
MAX_ROOT_OUTSTANDING = 64
MAX_ROOT_SCOPES = 64


class Rejected(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason
        super().__init__(reason)


def digest(token):
    return sha256(token.encode("utf-8")).hexdigest()


def identifier():
    return secrets.token_hex(16)


def fields(body, required):
    if not isinstance(body, dict) or set(body) != set(required):
        raise Rejected(400, "Unexpected or missing fields")
    if any(not isinstance(v, str) or not v or len(v) > 2048 for v in body.values()):
        raise Rejected(400, "Fields must be nonempty bounded strings")


class Store:
    def __init__(self, database, mode):
        if mode not in MODES:
            raise ValueError("Unknown control mode")
        self.database, self.mode = str(Path(database).resolve()), mode
        with closing(self.connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.executescript("""
                CREATE TABLE IF NOT EXISTS metadata (mode TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS scopes (
                    id TEXT PRIMARY KEY, parent TEXT REFERENCES scopes(id),
                    epoch INTEGER NOT NULL, active INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS grants (
                    hash TEXT PRIMARY KEY, scope TEXT NOT NULL REFERENCES scopes(id),
                    epoch INTEGER NOT NULL, active INTEGER NOT NULL);
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY, scope TEXT NOT NULL REFERENCES scopes(id),
                    epoch INTEGER NOT NULL, grant_hash TEXT NOT NULL,
                    request_key TEXT NOT NULL, message TEXT NOT NULL,
                    status TEXT NOT NULL, claim_hash TEXT,
                    UNIQUE(grant_hash, request_key));
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL, scope TEXT, job TEXT, details TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS mailbox (
                    job TEXT PRIMARY KEY REFERENCES jobs(id),
                    message TEXT NOT NULL, event_seq INTEGER UNIQUE NOT NULL REFERENCES events(seq));
            """)
            rows = db.execute("SELECT mode FROM metadata").fetchall()
            if not rows:
                db.execute("INSERT INTO metadata VALUES (?)", (mode,))
            elif len(rows) != 1 or rows[0]["mode"] != mode:
                raise ValueError("A database cannot change comparator mode")

    def connect(self):
        db = sqlite3.connect(self.database, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA synchronous=FULL")
        return db

    @contextmanager
    def transaction(self):
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    @staticmethod
    def event(db, kind, scope=None, job=None, **details):
        return db.execute("INSERT INTO events(kind,scope,job,details) VALUES (?,?,?,?)",
                          (kind, scope, job, json.dumps(details, sort_keys=True))).lastrowid

    @staticmethod
    def grant(db, scope):
        token = secrets.token_hex(32)
        db.execute("INSERT INTO grants VALUES (?,?,?,1)",
                   (digest(token), scope["id"], scope["epoch"]))
        return token

    @staticmethod
    def scope(db, scope_id):
        scope = db.execute("SELECT * FROM scopes WHERE id=?", (scope_id,)).fetchone()
        if scope is None:
            raise Rejected(404, "Unknown scope")
        return scope

    @staticmethod
    def authorize_agent(db, token):
        scope = db.execute("""SELECT s.* FROM grants g JOIN scopes s ON s.id=g.scope
            WHERE g.hash=? AND g.active=1 AND s.active=1 AND g.epoch=s.epoch""",
                           (digest(token),)).fetchone()
        if scope is None:
            raise Rejected(403, "Unknown or revoked agent capability")
        return scope

    def root_scope(self, db, scope):
        while scope["parent"] is not None:
            scope = self.scope(db, scope["parent"])
        return scope

    @staticmethod
    def family(db, root):
        return db.execute("""WITH RECURSIVE family(id) AS (
            SELECT id FROM scopes WHERE id=? UNION ALL
            SELECT s.id FROM scopes s JOIN family f ON s.parent=f.id)
            SELECT id FROM family""", (root,)).fetchall()

    def create(self):
        with self.transaction() as db:
            sid = identifier()
            db.execute("INSERT INTO scopes VALUES (?,NULL,0,1)", (sid,))
            self.event(db, "create", sid, parent=None)
            return {"scope": sid, "token": self.grant(db, self.scope(db, sid))}

    def agent(self, token, body):
        action = body.get("action") if isinstance(body, dict) else None
        fields(body, ("action", "key", "message") if action == "submit" else ("action",))
        with self.transaction() as db:
            scope = self.authorize_agent(db, token)
            family = self.family(db, self.root_scope(db, scope)["id"])
            if action == "delegate":
                if len(family) >= MAX_ROOT_SCOPES:
                    raise Rejected(409, "Scope family limit")
                depth, parent = 0, scope
                while parent["parent"] is not None:
                    depth += 1
                    parent = self.scope(db, parent["parent"])
                if depth >= 7:
                    raise Rejected(409, "Delegation depth limit")
                sid = identifier()
                db.execute("INSERT INTO scopes VALUES (?,?,0,1)", (sid, scope["id"]))
                self.event(db, "create", sid, parent=scope["id"])
                return {"scope": sid, "token": self.grant(db, self.scope(db, sid))}
            if action != "submit":
                raise Rejected(400, "Unknown agent action")
            prior = db.execute("SELECT * FROM jobs WHERE grant_hash=? AND request_key=?",
                               (digest(token), body["key"])).fetchone()
            if prior:
                if prior["message"] != body["message"]:
                    raise Rejected(409, "Idempotency key already bound to another message")
                return {"job": prior["id"], "status": prior["status"]}
            family_ids = {row["id"] for row in family}
            pending = db.execute("SELECT scope,COUNT(*) AS n FROM jobs WHERE status IN ('queued','claimed') GROUP BY scope").fetchall()
            if sum(row["n"] for row in pending if row["scope"] in family_ids) >= MAX_ROOT_OUTSTANDING:
                raise Rejected(409, "Scope family outstanding job limit")
            if sum(row["n"] for row in pending) >= MAX_OUTSTANDING:
                raise Rejected(409, "Outstanding job limit")
            jid = identifier()
            db.execute("INSERT INTO jobs VALUES (?,?,?,?,?,?, 'queued',NULL)",
                       (jid, scope["id"], scope["epoch"], digest(token), body["key"], body["message"]))
            self.event(db, "submit", scope["id"], jid, message=body["message"])
            return {"job": jid, "status": "queued"}

    def operator(self, body):
        action = body.get("action") if isinstance(body, dict) else None
        if action == "create":
            fields(body, ("action",))
            return self.create()
        if action == "requeue":
            fields(body, ("action", "job"))
            with self.transaction() as db:
                job = db.execute("SELECT * FROM jobs WHERE id=?", (body["job"],)).fetchone()
                if not job:
                    raise Rejected(404, "Unknown job")
                scope = self.scope(db, job["scope"])
                if job["status"] != "claimed" or not scope["active"] or job["epoch"] != scope["epoch"]:
                    raise Rejected(409, "Job cannot be requeued under this authority")
                db.execute("UPDATE jobs SET status='queued',claim_hash=NULL WHERE id=?", (job["id"],))
                self.event(db, "requeue", job["scope"], job["id"])
                return {"status": "queued"}
        fields(body, ("action", "scope"))
        if action not in ("stop", "resume"):
            raise Rejected(400, "Unknown operator action")
        with self.transaction() as db:
            root = self.scope(db, body["scope"])
            if action == "resume":
                # Resuming a child beneath a stopped ancestor would bypass root stop.
                ancestor = root
                while ancestor["parent"] is not None:
                    ancestor = self.scope(db, ancestor["parent"])
                    if not ancestor["active"]:
                        raise Rejected(409, "Ancestor remains stopped")
                if root["active"]:
                    raise Rejected(409, "Scope is already active")
            # Stop reaches descendants; resume is deliberately narrower. A root
            # restart must not silently lift an independently stopped child.
            descendants = self.family(db, root["id"]) if action == "stop" else [root]
            for row in descendants:
                sid = row["id"]
                db.execute("UPDATE scopes SET epoch=epoch+1,active=? WHERE id=?",
                           (int(action == "resume"), sid))
                db.execute("UPDATE grants SET active=0 WHERE scope=?", (sid,))
                if action == "stop":
                    # Fencing stale delivery is insufficient if an abandoned claim
                    # permanently consumes admission capacity. Both strong modes
                    # settle cancelled work without cooperation from its worker.
                    statuses = "('queued')" if self.mode == "cooperative_cancel" else "('queued','claimed')"
                    db.execute(f"UPDATE jobs SET status='cancelled' WHERE scope=? AND status IN {statuses}", (sid,))
            seq = self.event(db, action, root["id"])
            answer = {"status": action, "event_seq": seq}
            if action == "resume":
                answer["token"] = self.grant(db, self.scope(db, root["id"]))
            return answer

    def worker(self, body):
        action = body.get("action") if isinstance(body, dict) else None
        fields(body, ("action",) if action == "claim" else ("action", "job", "lease"))
        with self.transaction() as db:
            if action == "claim":
                job = db.execute("""SELECT j.* FROM jobs j JOIN scopes s ON j.scope=s.id
                    WHERE j.status='queued' AND s.active=1 AND s.epoch=j.epoch
                    ORDER BY j.rowid LIMIT 1""").fetchone()
                if not job:
                    return {"status": "empty"}
                lease = secrets.token_hex(32)
                db.execute("UPDATE jobs SET status='claimed',claim_hash=? WHERE id=?",
                           (digest(lease), job["id"]))
                self.event(db, "claim", job["scope"], job["id"])
                return {"status": "claimed", "job": job["id"], "lease": lease}
            if action != "deliver":
                raise Rejected(400, "Unknown worker action")
            job = db.execute("SELECT * FROM jobs WHERE id=?", (body["job"],)).fetchone()
            if not job or job["claim_hash"] is None or not secrets.compare_digest(job["claim_hash"], digest(body["lease"])):
                raise Rejected(403, "Claim is not bound to this job")
            if job["status"] == "delivered":
                return {"status": "already_delivered"}
            scope = self.scope(db, job["scope"])
            allowed = job["status"] == "claimed"
            if self.mode == "transactional_cancel":
                allowed = allowed and bool(scope["active"])
            elif self.mode == "epoch_fence":
                allowed = allowed and bool(scope["active"]) and job["epoch"] == scope["epoch"]
            if not allowed:
                if job["status"] == "claimed":
                    db.execute("UPDATE jobs SET status='cancelled' WHERE id=?", (job["id"],))
                seq = self.event(db, "blocked_delivery", job["scope"], job["id"])
                return {"status": "blocked", "event_seq": seq}
            # No cached decision leaves this transaction: authority, durable effect,
            # job settlement and audit record publish atomically at commit.
            seq = self.event(db, "delivery", job["scope"], job["id"])
            db.execute("INSERT INTO mailbox VALUES (?,?,?)", (job["id"], job["message"], seq))
            db.execute("UPDATE jobs SET status='delivered' WHERE id=?", (job["id"],))
            return {"status": "delivered", "event_seq": seq}

    def snapshot(self):
        db = self.connect()
        try:
            db.execute("BEGIN")
            return {
                "mode": self.mode,
                "events": [dict(r, details=json.loads(r["details"])) for r in db.execute("SELECT * FROM events ORDER BY seq")],
                "mailbox": [dict(r) for r in db.execute("SELECT * FROM mailbox ORDER BY event_seq")],
                "jobs": [dict(r) for r in db.execute("SELECT id,scope,status FROM jobs ORDER BY rowid")],
            }
        finally:
            db.rollback()
            db.close()
