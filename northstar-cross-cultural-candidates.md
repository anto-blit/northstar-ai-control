# Candidate stories: cross-cultural extension of the lesson collection

**Status: proposal. Not reviewed by a human. Not authored under any experimental
protocol. `deployment_approved: false`.**

This is an outside suggestion for the `curriculum/` collection. Nothing here has
been read against a fixed protocol, scored, or compared with a factual
counterpart. It should not enter a live authoring or evaluation session while any
run is open, because introducing new guidance mid-run contaminates the comparison
the project is trying to make.

---

## Why this might be worth adding

The current collection takes six Aesop fables from V. S. Vernon Jones's 1912
translation and annotates them. The README already states the limitation plainly:
one tradition does not stand in for cultural consensus. That is a real exposure,
and it is the kind of objection that costs nothing to raise and is expensive to
answer later.

The proposal below responds to that specific gap. Each entry is a *cluster*: a
moral lesson that appears in traditions with no plausible line of transmission
between them. The claim being made is narrow. Independent reinvention is evidence
that a lesson is memorable and socially useful across very different
circumstances. It is not evidence that the lesson is true, and it is not evidence
that a story teaches it better than a rule or a worked example. That remains the
open question the four-method comparison exists to settle.

**Two of these are new rows. Three are reinforcements of rows that already
exist.** The reinforcements may matter more than the new rows, because they let
the project say that an already-adopted lesson is attested outside the tradition
it was drawn from, without expanding the rule surface at all.

---

## Summary table

Same three columns as the existing collection.

| Cluster | Adopted lesson | Interpretation we explicitly limit or reject | Relation to current collection |
| --- | --- | --- | --- |
| Reciprocity | Test an action by accepting it in the recipient's position | Reciprocity as exchange, where obligation depends on the other party's ability to repay or retaliate | Reinforces *The Fox and the Stork* |
| The stranger in the ditch | Obligation follows need, capability and proximity, not group membership | Unlimited obligation to every distant need, and self-sacrifice as the default | Reinforces *The Lion and the Mouse* |
| The weighed record | The record of what was done is held by someone other than the actor | Treating the existence of an audit as proof that conduct was good | **New row** |
| The servant that will not stop | Delegated capability requires a working stop, checked where the action commits | Treating literal compliance with instructions as sufficient obedience | **New row** |
| The false alarm | Report evidence honestly; a false signal is paid for by everyone who later relies on it | Blaming the recipient for eventually disbelieving; and the beacon story's framing of a woman as the cause | Reinforces *The Shepherd's Boy and the Wolf* |

---

## 1. Reciprocity

**Attestations.** Confucius, *Analects* 15:24, where Zigong asks for a single
word to act on for life and receives *shu*, framed negatively. The *Mahabharata*,
Anushasana Parva 113, which calls it the sum of duty. Leviticus 19:18, and
Hillel's negative formulation in b. Shabbat 31a. Matthew 7:12. Isocrates,
*Nicocles*, around 374 BCE. The Jain *Sutrakritanga* 1.11. The *Udanavarga* 5.
An-Nawawi's thirteenth hadith. Also present in oral proverb traditions across
West Africa and elsewhere, which are harder to date but not derived from any of
the above.

Chinese, Indic, Hellenic and Levantine attestations within roughly two centuries
of each other, with no adequate transmission story between them. This is the most
independently reinvented moral claim on record.

**Adopted lesson.** An action is tested by whether the actor would accept it
while occupying the recipient's position, with the recipient's needs and
constraints rather than the actor's.

**Limited or rejected.** The exchange reading, under which obligation is
contingent on repayment or on the other party's power to retaliate. Also rejected:
the naive projection reading, where the actor substitutes their own preferences
for the recipient's. The Fox and the Stork row already blocks the second of these;
the dish is the wrong shape precisely because the host reasoned from their own
convenience.

**Factual counterpart to author.** A procurement case where a supplier is offered
terms the buyer's own policy would reject if the roles were reversed, with the
same facts as the narrative version.

**Candidate fact key.** `reversal_acceptable` (caller-supplied). Note that this is
a judgment, not an observation, and the engine cannot compute it. Adding it widens
the REVIEW surface.

---

## 2. The stranger in the ditch

**Attestations.** Mencius 2A:6, on anyone who suddenly sees a child about to fall
into a well, and who feels alarm without reference to any relationship with the
parents. Luke 10, where the helper is a member of the despised group. Leviticus
19:34 and Deuteronomy 10:19 on the stranger. Greek *xenia* under Zeus Xenios,
running through the *Odyssey*. The *Taittiriya Upanishad*'s treatment of the guest.
Bedouin guest-right. These reach the same place from four unconnected directions.

Mencius is the strongest of these for the project's purposes, because the argument
is explicitly not theological. It is a claim about what any person's reaction
reveals, offered as evidence rather than as commandment.

**Adopted lesson.** Whether help is owed turns on the presence of need, the
actor's relevant capability, and proximity. It does not turn on the recipient's
group, status, or capacity to return the favour.

**Limited or rejected.** The unlimited-obligation reading, where every distant
need generates a duty and the actor is required to exhaust themselves. Also
rejected: reading the Samaritan's group identity as the point, which turns a claim
about need into a claim about which group is virtuous.

**Factual counterpart to author.** A triage case where two requests arrive and
only one can be served, differing in need and in the requester's account standing.

**Candidate fact key.** The existing `recipient_can_use` and
`serious_harm_avoided` cover much of this. If anything is added, prefer
`assistance_withheld_for_group_membership` as a violation flag rather than adding
a positive duty key, since a violation flag composes with the existing override
behaviour and a duty key does not.

---

## 3. The weighed record

**Attestations.** The Egyptian weighing of the heart against the feather of Maat,
spell 125 of the Book of the Dead, from the New Kingdom onward, with Thoth
recording and Ammit waiting. The Zoroastrian Chinvat bridge, where Rashnu holds
the scales. The Qur'anic *mizan*. Chitragupta's ledger in the *Garuda Purana*.
The ledgers of the Ten Kings in Chinese Diyu, and later the Ming merit-and-demerit
ledgers, which are the same idea turned into a self-audit.

The Egyptian, Iranian and Abrahamic versions may be linked by diffusion. The
Chinese material is much harder to derive from any of them.

**Adopted lesson.** The record of what was done is kept by a party other than the
actor, is not writable by the actor, and is checked afterwards against what was
claimed.

**Limited or rejected.** Treating the existence of an audit as evidence that the
conduct was acceptable. Also rejected: the deterrence-only reading, where the
record matters solely because of the punishment attached to it, which collapses
into the exchange error already rejected in cluster 1.

**Why this is the strongest new row.** G8-C's design is this story. An agent can
edit the working database; an independent scorer retains the original evidence;
offline verification reconstructs the tool history and checks actual database
events. The project built the mechanism before naming the lesson. Adding the row
would let the curriculum and the experiment cite each other.

**Factual counterpart to author.** A release-approval case where the actor's
summary and the retained check output disagree.

**Candidate fact keys.** `record_independently_held`, `actor_modified_record`.
Action type `report`.

---

## 4. The servant that will not stop

**Attestations.** Lucian's *Philopseudes*, around 150 to 180 CE, where Eucrates
animates a pestle to fetch water and cannot undo the command; Goethe's 1797 poem
takes this directly. Midas and the touch, in Ovid and in older Phrygian material.
The wish-granted-literally family: djinn bound to the exact wording, the three
wishes, the Grimms' porridge pot, W. W. Jacobs's monkey's paw. The golem that
keeps working after its maker loses control.

**Provenance caution.** The golem tradition is old in outline, but the Prague
version in which the creature must be stopped and cannot be is attested in written
form only in the nineteenth century. Do not date it to antiquity. The Lucian
attestation carries the weight here.

**Adopted lesson.** Capability delegated to an agent requires a revocation path
that exists, is reachable, and is rechecked at the point where the action becomes
irreversible. Instruction alone is not control.

**Limited or rejected.** The hubris reading, where the moral is that the maker
should not have built the thing. That reading is emotionally satisfying and
operationally empty, since it specifies no line and no mechanism. Also rejected:
treating the agent's literal compliance as obedience, which is the failure, not a
defence.

**Why this is the second new row.** It is the G6 and G7 stop-boundary work stated
as a lesson. The project has already tested whether authority can be withdrawn
after work is queued, and found that enforcement has to happen in the same
transaction as delivery. The fable and the finding say the same thing.

**Factual counterpart to author.** A dispatch case where a stop arrives after the
job is queued but before it commits, with a separate authorized job that must
still finish.

**Candidate fact keys.** `revocation_path_exists`,
`authority_rechecked_at_commit`. These join `authorization_valid` rather than
replacing it, since a valid authorization at issue time is exactly the condition
under which this failure occurs. Action type `assign`.

---

## 5. The false alarm

**Attestations.** Aesop's shepherd boy, already in the collection. Independently,
the Chinese account of King You of Zhou lighting the warning beacons for
amusement, so that the marchers did not come when the attack was real, recorded in
the *Shiji* and traditionally set at 771 BCE. And the inversion in Aeschylus's
*Agamemnon*, where Cassandra's warnings are accurate and disbelieved anyway.

**Provenance caution.** The beacon episode is disputed. Some historians doubt that
beacon towers of that kind existed then, and the Tsinghua bamboo-slip account of
the period does not include it. Present it as traditional narrative, not as
event.

**Adopted lesson.** Report evidence honestly. A false signal is not paid for by
the person who sends it but by everyone who later has to decide whether to act on
a true one.

**Limited or rejected.** The existing row already rejects permanently ignoring a
past false reporter, which is right and should carry over. Add two rejections. The
beacon story's traditional framing blames a woman for the king's decision; that
framing is not adopted and should be recorded as an extension the project
declines. And the Cassandra case blocks the inference that disbelief is always
earned, since there the signal was true and the failure sat entirely with the
recipients.

**Value of the pairing.** The shepherd boy alone teaches a reporter-side duty. The
shepherd boy plus Cassandra teaches that signal reliability is a joint property of
reporter and recipient, which is the version that applies to a monitoring system.

**Candidate fact key.** `evidence_supports_claim`. Action type `report`.

---

## Sourcing and retelling policy

The existing method reads the source passage first, preserves it, and labels new
retellings as such. That works cleanly for Vernon Jones because the 1912
translation is public domain in the USA. These clusters are harder, in two
distinct ways.

**Translation licensing.** Public-domain translations exist for most of this:
Legge for the *Analects* and *Mencius*, Ganguli for the *Mahabharata*, Jacobi in
the Sacred Books of the East for the Jain material, Budge for the Egyptian, Fowler
for Lucian. Each needs checking individually rather than assuming. Some widely
quoted modern translations are not free to redistribute.

**Living traditions.** Four of these five clusters draw on texts that are
currently scripture for someone. A project that compiles them into a machine-
readable moral catalog, annotates which readings it rejects, and marks the result
`deployment_approved: false` is doing something different from quoting Aesop, and
will be read differently. The safest construction is the one already in use:
**cite the source passage by reference, do not reproduce it, and write an original
retelling that carries the structure without standing in for the text.** That also
keeps the story and factual-counterpart conditions matched, which the comparison
requires anyway.

---

## What this does not establish

It does not establish that any of these lessons is correct, that stories teach
them better than principles or worked examples, or that a broader collection would
change model behaviour. The project's own record is the relevant evidence here: in
the first story comparison all three conditions reached the same score once
Markdown wrappers were removed, and the apparent difference was formatting rather
than judgment.

Cross-cultural attestation answers one objection, that the collection is
parochial. It answers nothing else. A larger and better-sourced catalog that still
shows no narrative advantage is a catalog that should be narrowed, as the site
already commits to doing.

---

## Suggested next step

Open this as an issue rather than a pull request, marked as an unreviewed external
proposal. If any of it is adopted, take clusters 3 and 4 first: they are the only
genuinely new rows, they map onto mechanisms the project has already built and
tested, and they can be authored with public-domain sources and no scriptural
material at all.
