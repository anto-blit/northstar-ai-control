"""In-boundary probes from the agent's HTTP-only authority.

The agent holds only its capability token and the declared /agent actions.
PROTOCOL: "Denied requests are not prevented catastrophes" and "Never treat
HTTP rejection counts as prevented harm." These are regression guards on the
broker's input handling and role separation, not evidence of risk reduction.
No capability tokens are recorded here or in the report.
"""
import unittest

from support import MODES, MSG, lab, raw_post


class AgentHttpAuthority(unittest.TestCase):
    def test_agent_token_cannot_reach_operator_worker_or_audit(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                agent_token = root["token"]
                for route, body in (
                    ("/operator", {"action": "stop", "scope": root["scope"]}),
                    ("/operator", {"action": "create"}),
                    ("/operator", {"action": "requeue", "job": "whatever"}),
                    ("/worker", {"action": "claim"}),
                    ("/worker", {"action": "deliver", "job": "x", "lease": "y"}),
                    ("/audit", {"action": "snapshot"}),
                ):
                    resp = instance.request(route, body, token=agent_token)
                    self.assertEqual(resp["status"], 403, msg=(route, body, resp))

    def test_agent_capability_is_dead_after_stop_before_any_resume(self):
        for mode in MODES:
            with self.subTest(mode=mode), lab(mode) as instance:
                root = instance.operator("create")
                token = root["token"]
                instance.agent(token, "submit", key="a", message=MSG)
                instance.operator("stop", scope=root["scope"])
                self.assertEqual(
                    instance.request(
                        "/agent", {"action": "submit", "key": "b", "message": MSG},
                        token=token)["status"],
                    403)
                self.assertEqual(
                    instance.request("/agent", {"action": "delegate"}, token=token)["status"],
                    403)

    def test_agent_json_payload_validation(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]
            for body in (
                {"action": "frobnicate"},
                {"action": "delegate", "extra": "x"},
                {"action": "submit", "key": "k", "message": "x" * 4096},
                {"action": "submit", "key": "k"},
                {"action": "submit", "key": "k", "message": ""},
            ):
                resp = instance.request("/agent", body, token=token)
                self.assertEqual(resp["status"], 400, msg=(body, resp))

    def test_agent_raw_http_hardening(self):
        with lab("epoch_fence") as instance:
            token = instance.operator("create")["token"]

            dup_status, _ = raw_post(
                instance.url, "/agent", token,
                b'{"action": "submit", "action": "submit", "key": "a", "message": "b"}')
            self.assertEqual(dup_status, 400)

            no_ct_status, _ = raw_post(
                instance.url, "/agent", token, b'{"action": "delegate"}', content_type=None)
            self.assertEqual(no_ct_status, 400)

            oversized = (b'{"action": "submit", "key": "a", "message": "'
                         + b'z' * 20000 + b'"}')
            big_status, _ = raw_post(instance.url, "/agent", token, oversized)
            self.assertEqual(big_status, 413)

            not_json_status, _ = raw_post(instance.url, "/agent", token, b'not-json-at-all')
            self.assertEqual(not_json_status, 400)

            # Control: a well-formed request on the same raw path still succeeds.
            ok_status, ok_body = raw_post(
                instance.url, "/agent", token, b'{"action": "delegate"}')
            self.assertEqual(ok_status, 200)
            self.assertIn("scope", ok_body)


if __name__ == "__main__":
    unittest.main()
