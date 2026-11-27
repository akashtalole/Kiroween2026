from hypothesis import given, strategies as st
from spec_lint import VAGUE, lint

GOOD = """# Requirements: policy
## R-POL-1 Tier classification
Acceptance criteria
1. [PBT] WHEN any signal is added to a change, THE system SHALL NOT lower the tier.
2. [EX] WHEN the policy file is missing, THE system SHALL refuse to merge and report why.

## Open questions
- Should docs-only changes skip review? Recommended default: yes, tier A0.
"""


def test_good_spec_is_ready():
    assert lint(GOOD) == []


def test_missing_tag_is_reported():
    bad = GOOD.replace("[PBT] ", "")
    assert any("not tagged" in f for f in lint(bad))


def test_non_ears_is_reported():
    bad = GOOD.replace("WHEN any signal is added to a change, THE system SHALL NOT lower the tier.", "Tiers go up.")
    assert any("EARS" in f for f in lint(bad))


def test_question_without_default_is_reported():
    bad = GOOD.replace(" Recommended default: yes, tier A0.", "")
    assert any("default" in f for f in lint(bad))


def test_requirement_without_criteria_is_reported():
    assert any("no acceptance criteria" in f for f in lint("## R-X-1 Empty\n"))


def test_duplicate_ids_are_reported():
    assert any("duplicate" in f for f in lint(GOOD + "\n## R-POL-1 Again\nAcceptance criteria\n1. [EX] WHEN x, THE system SHALL y.\n"))


@given(st.sampled_from(VAGUE))
def test_any_vague_word_without_a_number_is_reported(word):
    spec = GOOD.replace("report why", f"report why in a {word} way")
    assert any("vague" in f for f in lint(spec))


@given(st.sampled_from(VAGUE))
def test_vague_word_with_a_number_is_allowed(word):
    spec = GOOD.replace("report why", f"report why within 200 ms ({word})")
    assert not any("vague" in f for f in lint(spec))


@given(st.text(max_size=300))
def test_lint_never_crashes(text):
    assert isinstance(lint(text), list)
