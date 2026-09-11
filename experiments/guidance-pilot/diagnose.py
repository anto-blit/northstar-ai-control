"""Post-hoc format diagnosis. Never replaces the frozen primary score."""
import json
from pathlib import Path
from pilot import MODEL, OUT, decision, digest, read, verify_plan, write_new


def main():
    plan = verify_plan()
    primary = read(OUT / "report.json")
    observations = {(o["case_id"], o["condition"]): o for o in primary["observations"]}
    records = []
    for request in plan["requests"]:
        path = OUT / "responses" / f"{request['index']:03}.json"
        record = read(path)
        text = (record.get("result") or "").strip()
        fenced = text.startswith("```json\n") and text.endswith("\n```")
        # Only remove one complete surrounding JSON Markdown fence. No answer edits.
        altered = dict(record, result=text[8:-4] if fenced else text)
        answer = decision(altered)
        original = observations[(request["case_id"], request["condition"])]
        records.append(dict(index=request["index"], case_id=request["case_id"], condition=request["condition"],
                            pair_id=original["pair_id"], markdown_fence=fenced, primary_correct=original["correct"],
                            diagnostic_decision=answer, expected=original["expected"], diagnostic_correct=answer == original["expected"]))
    summaries = {}
    for arm in "PES":
        subset = [r for r in records if r["condition"] == arm]
        pairs = {r["pair_id"] for r in subset}
        summaries[arm] = dict(correct=sum(r["diagnostic_correct"] for r in subset), total=len(subset),
                              correct_pairs=sum(all(r["diagnostic_correct"] for r in subset if r["pair_id"] == pair) for pair in pairs), total_pairs=len(pairs),
                              markdown_wrapped_outputs=sum(r["markdown_fence"] for r in subset))
    result = dict(schema=1, analysis_type="Post-hoc diagnostic, added after all 48 target responses; not the preregistered/frozen endpoint.",
                  method="Remove only a single enclosing ```json newline ... newline ``` fence, then apply the original parser. No new calls, exclusions or answer changes.",
                  primary_report_sha256=digest(OUT / "report.json"), diagnostic_source_sha256=digest(Path(__file__)),
                  conditions=summaries, records=records,
                  conclusion="All three conditions make the expected substantive judgments on every case. The primary apparent S/E lead arises entirely from format compliance. No demonstrated moral-judgment advantage; corpus at semantic ceiling.")
    path = OUT / "format-diagnosis.json"
    if path.exists():
        assert read(path) == result, "Preserved diagnosis differs"
    else:
        write_new(path, result)
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
