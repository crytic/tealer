import re
from pathlib import Path
from typing import List, Optional, Tuple, Set

from tealer.teal.instructions.instructions import Instruction, Label
from tealer.teal.instructions.parse_instruction import parse_line
from tealer.teal.teal import Teal
from tealer.utils.output import CFGDotConfig, full_cfg_to_dot


# pylint: disable=too-few-public-methods
class Regex:
    def __init__(self, label: str, instructions: List[Instruction]) -> None:
        self.label = label
        self.instructions = instructions


def parse_regex(regex: str) -> Regex:
    """
    Parse the regex

    Args:
        regex: regex as a string

    Returns:
        Regex as an object

    Raises:
        ValueError: if the text does not have the correct format
    """
    pattern = re.compile(r"^(.*?)=>\s*(.*?)$", re.DOTALL)
    match = pattern.search(regex)
    if match:
        # Group 1 is the label, Group 2 is the content
        label_found, content_found = match.groups()
        label = label_found.strip()
        instructions_text = content_found.strip().splitlines()

        instructions: List[Instruction] = []
        for line in instructions_text:
            instruction = parse_line(line)
            if instruction:
                instructions.append(instruction)

        return Regex(label, instructions)

    raise ValueError("Invalid text format")


def _find_label(instructions: List[Instruction], label: str) -> Optional[Instruction]:
    # Assuming "*" is not a valid teal label ?
    # Assuming the first instruction is the entry point
    if label == "*":
        return instructions[0]

    match = [ins for ins in instructions if isinstance(ins, Label) and ins.label == label]

    # assuming the same label can't be reused in a contract
    assert len(match) <= 1

    if match:
        return match[0]

    return None


def _is_equal(a: Instruction, b: Instruction) -> bool:
    if type(a) is not type(b):
        return False

    # We don't have current a good way to compare two instructions subfield
    # So we use the string representation as a temp solution
    # Note both objects are not expected to be the same, as one is coming from the teal contract
    # The other one was generated based on the regex
    return str(a) == str(b)


def _is_match(current_instruction: Optional[Instruction], regex: List[Instruction]) -> bool:
    for _, regex_ins in enumerate(regex):
        if current_instruction is None:
            return False
        if not _is_equal(current_instruction, regex_ins):
            return False
        current_instruction = (
            current_instruction.next[0]
            if current_instruction.next and len(current_instruction.next) == 1
            else None
        )

    return True


def _find_instructions(
    current_instruction: Instruction,
    regex: List[Instruction],
    visited: Set[Instruction],
    matches: List[List[Instruction]],
    covered: Set[Instruction],
) -> bool:
    if current_instruction in visited:
        return False

    visited.add(current_instruction)

    reaches = False

    if _is_match(current_instruction, regex):
        match: List[Instruction] = []
        current = current_instruction
        for _ in range(0, len(regex) - 1):

            if not current:
                break
            match.append(current)

            if len(current.next) != 1:
                print(f"Regex cannot work on branching instructions {current_instruction}")
                return False
            current = current.next[0]

        match.append(current)
        matches.append(match)
        reaches = True

    for next_ins in current_instruction.next:

        if next_ins in covered:
            continue

        if _find_instructions(next_ins, regex, visited, matches, covered):
            covered.add(current_instruction)
            reaches = True

    return reaches


def match_regex(contract: Teal, regex: Regex) -> Tuple[List[List[Instruction]], Set[Instruction]]:
    """
    Match the regex in the contract

    Args:
        contract: target
        regex: regex

    Returns:
        A tuple of (matches, covered), where
        - matches: contains all the instructions that match the regex
        - covered: contains all the instruction between the label and the matches
    """
    label = _find_label(contract.instructions, regex.label)

    if not label:
        print(f"{label} cannot be found in {contract}")
        return [], set()

    matches: List[List[Instruction]] = []
    covered: Set[Instruction] = set()

    _find_instructions(label, regex.instructions, set(), matches, covered)

    return matches, covered


def update_config(
    config: CFGDotConfig, matches: List[List[Instruction]], covered: Set[Instruction]
) -> None:
    """
    Update the config with the regex result. It color match in red, and covered in green

    Args:
        config: config
        matches: instructions that match the regex
        covered: instructions between the label and the match
    """
    for inss in matches:
        for ins in inss:
            config.custom_background_color[ins] = "#e0182b"  # red

    for ins in covered:
        config.custom_background_color[ins] = "#36d899"  # green


def run_regex(teal: Teal, regex_Path: Path, export_path: Path) -> None:
    """
    Run the regex analysis and generate the dot file

    Args:
        teal: target
        regex_Path: path to the regex
        export_path: path to generate the dot file
    """
    with open(regex_Path, "r", encoding="utf8") as f_regex:
        regex = parse_regex(f_regex.read())

    matches, covered = match_regex(teal, regex)

    if not matches:
        print("Not match was found")
        return
    # Ensure the CFG generation does not crash
    config = CFGDotConfig()
    update_config(config, matches, covered)

    with open(export_path, "w", encoding="utf8") as fp:
        full_cfg_to_dot(teal, config, Path(fp.name))

    print(f"Result generated in {export_path}")
