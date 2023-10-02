import tempfile
from pathlib import Path

from tealer.teal.instructions.instructions import Eq
from tealer.teal.parse_teal import parse_teal
from tealer.utils.regex.regex import parse_regex, match_regex, update_config
from tealer.utils.output import CFGDotConfig, full_cfg_to_dot


def test_parse_regex() -> None:
    txt = """
    some_label => 
   gtxn 0 Amount
   int 13337
   =="""

    regex = parse_regex(txt)
    assert regex.label == "some_label"
    assert len(regex.instructions) == 3
    assert isinstance(regex.instructions[-1], Eq)


def test_match() -> None:

    with open("./tests/regex/vote_approval.teal", "r", encoding="utf8") as f_codebase:
        teal = parse_teal(f_codebase.read())

    with open("./tests/regex/regex.txt", "r", encoding="utf8") as f_regex:
        regex = parse_regex(f_regex.read())

    matches, covered = match_regex(teal, regex)

    assert len(matches) == 1

    assert len(covered) == 21

    # Ensure the CFG generation does not crash
    config = CFGDotConfig()
    update_config(config, matches, covered)

    with tempfile.NamedTemporaryFile() as fp:
        full_cfg_to_dot(teal, config, Path(fp.name))
