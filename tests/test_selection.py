import json
import time

import pytest

from jev_skill_router.config import Config
from jev_skill_router.jev import RequestBudget, encoded

from jevshelf import cli
from jevshelf.selection import Router, VERIFICATION_CANDIDATES, skill_excerpt


def make_skills(tmp_path, body, count=1):
    root = tmp_path / "skills"
    for i in range(count):
        directory = root / f"candidate-{i}"
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text(
            f"---\nname: candidate-{i}\ndescription: Inspect evidence for the current task.\n---\n{body}"
        )
    return root


def test_excerpt_uses_context_and_reserves_exclusion_evidence():
    body = ("# Method\n" + "ordinary introduction. " * 100 +
            "\n## When to Use\nCompare the source with actual observed behavior.\n" +
            "general notes. " * 100 +
            "\n## When NOT to Use\nDo not use for an urgent incident requiring immediate action.\n" +
            "other notes. " * 100 + "\nInvestigate zephyr_context_evidence before proceeding.\n")
    selected = skill_excerpt(body, "Inspect behavior", "zephyr_context_evidence", 900)
    assert len(selected) <= 900
    assert "When NOT to Use" in selected and "urgent incident" in selected
    assert "When to Use" in selected and "zephyr_context_evidence" in selected
    assert skill_excerpt("Complete short method.", "task", "context", 100) == "Complete short method."


def test_question_and_json_bounds_cover_context_evidence(tmp_path):
    body = '# Method\n' + ('漢🙂"\\\n' * 200) + '\n## When NOT to Use\nAvoid urgent incidents.\n' + ('終"\\' * 300)
    root = make_skills(tmp_path, body)
    router = Router(Config(roots=[str(root)], shortlist=VERIFICATION_CANDIDATES))
    state = router._state("Inspect evidence", "Urgent incident context")
    router._live_plan(state)
    skill = next(iter(router.catalog.skills.values()))
    questions = router.verify_questions([skill], state["task"])
    assert "recent_context" in questions["fit_0"]["instructions"]["question"]
    assert "different step" in questions["fit_0"]["criteria"]["false"]
    assert len(encoded(questions)) <= router._verification_size_bound(skill)
    assert len(questions["fit_0"]["instructions"]["skill"]["instructions_excerpt"]) <= 900


class RecordedClient:
    def __init__(self):
        self.requests = []

    def metrics_snapshot(self):
        count = len(self.requests)
        return {"api_calls": count, "http_requests": count, "input_tokens": count, "output_tokens": count}

    def ask(self, state, questions):
        self.requests.append({"model": "fixture", "state": state, "questions": questions})
        if "rank" in questions:
            ids = [key for key in questions["rank"]["criteria"] if key != "__none__"]
            values = [len(ids) - i for i in range(len(ids))]
            total = sum(values) + 1
            answers = {"rank": {"probabilities": {"__none__": 1 / total, **dict(zip(ids, (v / total for v in values)))}}}
        else:
            answers = {}
            for key, question in questions.items():
                name = question["instructions"]["skill"]["name"]
                fits = int(name.rsplit("-", 1)[1]) >= 3
                answers[key] = {"noul": .98 if fits else .05} if key.startswith("fit_") else {"score": 2, "confidence": .9}
        return {"model": "fixture", "answers": answers, "usage": {"input_tokens": 1, "output_tokens": 1}}


def test_wider_verification_recovers_candidates_without_filling_output(tmp_path):
    root = make_skills(tmp_path, "A compact method.", count=8)
    client = RecordedClient()
    router = Router(Config(roots=[str(root)], shortlist=VERIFICATION_CANDIDATES, max_skills=3), client)
    plan = router.plan("Inspect evidence", "Current step: assess observed behavior")
    result = router._live(router._state("Inspect evidence", "Current step: assess observed behavior"), RequestBudget(32, time.monotonic() + 30))
    assert result["shortlisted"] == 6
    assert {router.catalog.skills[item["id"]].name for item in result["selected"]} == {"candidate-3", "candidate-4", "candidate-5"}
    assert result["api_calls"] <= plan["base_requests_upper_bound"]
    assert all(len(encoded(request)) <= router.config.max_request_bytes for request in client.requests)


def configure(tmp_path, monkeypatch, root):
    manifest = tmp_path / "collections.json"
    manifest.write_text(json.dumps({"collections": {"analysis": {"roots": [str(root)]}}}))
    monkeypatch.setenv("JEVSHELF_CONFIG", str(manifest))


def test_exact_name_lookup_is_local_and_does_not_fill_slots(tmp_path, monkeypatch, capsys):
    root = make_skills(tmp_path, "Method.", count=8)
    configure(tmp_path, monkeypatch, root)
    assert cli.main(["search", "--collection", "analysis", "--mode", "lexical", "--task", " CANDIDATE-3 ", "--context", "candidate-2 evidence", "--max-results", "3"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["method"] == "exact_name" and result["mode"] == "lexical"
    assert [s["name"] for s in result["selected"]] == ["candidate-3"]
    assert "content" not in result["selected"][0]
    assert cli.main(["search", "--collection", "analysis", "--mode", "lexical", "--task", "Inspect evidence"]) == 0
    assert json.loads(capsys.readouterr().out)["method"] == "metadata_bm25"


def test_public_search_and_plan_share_wider_verification_policy(tmp_path, monkeypatch, capsys):
    root = make_skills(tmp_path, "Compact method.", count=8)
    configure(tmp_path, monkeypatch, root)
    monkeypatch.setenv("TYPESAFE_API_KEY", "fixture-never-sent")
    configs = []

    def make_router(config):
        configs.append(config)
        return Router(config, RecordedClient())

    monkeypatch.setattr(cli, "Router", make_router)
    args = ["--collection", "analysis", "--task", "Inspect evidence", "--context", "Current step: assess observed behavior"]
    assert cli.main(["plan", *args]) == 0
    plan = json.loads(capsys.readouterr().out)
    assert cli.main(["search", *args, "--mode", "jev", "--max-results", "3"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert [config.model for config in configs] == ["jev-preview", "jev-preview"]
    assert result["shortlisted"] == 6 and len(result["selected"]) == 3
    assert result["api_calls"] <= plan["base_requests_upper_bound"]


@pytest.mark.parametrize("fit,confidence,status", [(.05, .9, "no_match"), (.98, .1, "uncertain")])
def test_verification_abstention_is_preserved(tmp_path, fit, confidence, status):
    class AbstainingClient(RecordedClient):
        def ask(self, state, questions):
            response = super().ask(state, questions)
            if "rank" not in questions:
                for key in questions:
                    response["answers"][key] = {"noul": fit} if key.startswith("fit_") else {"score": 2, "confidence": confidence}
            return response

    root = make_skills(tmp_path, "Compact method.")
    router = Router(Config(roots=[str(root)], shortlist=VERIFICATION_CANDIDATES, max_skills=3), AbstainingClient())
    result = router._live(router._state("Inspect evidence", "Assessment only"), RequestBudget(32, time.monotonic() + 30))
    assert result["status"] == status and result["selected"] == []
