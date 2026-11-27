import json

from hypothesis import given, strategies as st
from touch_index import compute, load


def test_example_night(tmp_path):
    events = [
        {"type": "task_done", "task": "T1", "merged": True, "retries": 1, "credits": 10, "night": "n"},
        {"type": "task_done", "task": "T2", "merged": True, "retries": 0, "credits": 20, "night": "n"},
        {"type": "task_done", "task": "T3", "merged": False, "retries": 3, "credits": 5, "night": "n"},
        {"type": "human_approval", "task": "T2", "seconds": 90, "night": "n"},
        {"type": "escape", "task": "T1", "night": "m"},
    ]
    p = tmp_path / "ledger.ndjson"
    p.write_text("\n".join(json.dumps(e) for e in events) + "\nnot json\n")
    m = compute(load(str(p), "n"))
    assert m["tasks_done"] == 3 and m["merged"] == 2 and m["zero_touch_merged"] == 1
    assert m["zero_touch_rate"] == 0.5 and m["human_seconds_per_merged_task"] == 45.0 and m["escapes"] == 0


task = st.fixed_dictionaries({"type": st.just("task_done"), "task": st.sampled_from(["A", "B", "C", "D"]),
                              "merged": st.booleans(), "retries": st.integers(0, 3), "credits": st.integers(0, 50)})
touch = st.fixed_dictionaries({"type": st.just("human_prompt"), "task": st.sampled_from(["A", "B", "C", "D"]),
                               "seconds": st.integers(0, 300)})


@given(st.lists(st.one_of(task, touch), max_size=30))
def test_rates_are_bounded_and_consistent(events):
    m = compute(events)
    assert m["zero_touch_merged"] <= m["merged"] <= m["tasks_done"]
    if m["zero_touch_rate"] is not None:
        assert 0 <= m["zero_touch_rate"] <= 1


@given(st.lists(st.one_of(task, touch), max_size=30), st.randoms())
def test_metrics_do_not_depend_on_event_order_for_touches(events, rnd):
    touches = [e for e in events if e["type"] != "task_done"]
    tasks = [e for e in events if e["type"] == "task_done"]
    shuffled = touches[:]
    rnd.shuffle(shuffled)
    assert compute(tasks + touches) == compute(tasks + shuffled)


@given(st.lists(task, max_size=20))
def test_adding_a_touch_never_increases_zero_touch_count(tasks):
    base = compute(tasks)
    more = compute(tasks + [{"type": "human_prompt", "task": "A", "seconds": 1}])
    assert more["zero_touch_merged"] <= base["zero_touch_merged"]
