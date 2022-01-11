from typing import List, Dict


def instruction_cost(ins_str: str, version: int) -> int:
    """calculate the execution cost of the given instruction in given Teal version.

    Args:
        ins_str (str): string representation of the instruction.
        version (int): Teal version of the contract.
    Returns:
        (int): returns the execution cost of the instruction.

    """

    # changes_version_{i} contains costs of instructions whose cost is changed in `i`th version or
    # if that instruction is introduced in `i`th version and has cost greater than 1.
    # As most of the instructions have cost equal to 1 in all the teal versions, default value for
    # any instruction not present in the dictionary is taken as 1.

    changes_version_1: Dict[str, int] = {
        "sha256": 7,
        "keccak256": 26,
        "sha512_256": 9,
        "ed25519verify": 1900,
    }

    changes_version_2: Dict[str, int] = {
        "sha256": 35,
        "keccak256": 130,
        "sha512_256": 45,
    }

    changes_version_4: Dict[str, int] = {
        "divmodw": 20,
        "sqrt": 4,
        "expw": 10,
        "b+": 10,
        "b-": 10,
        "b/": 20,
        "b*": 20,
        "b%": 20,
        "b|": 6,
        "b&": 6,
        "b^": 6,
        "b~": 4,
    }

    changes_version_5: Dict[str, int] = {
        "ecdsa_verify": 1700,
        "ecdsa_pk_decompress": 650,
        "ecdsa_pk_recover": 2000,
    }

    def _combine_dicts(l: List[Dict[str, int]]) -> Dict[str, int]:
        """combine dict keys and values, where keys, values of dicts at large index
        override lower index dict values.

        """
        new_dict = {}
        for d in l:
            new_dict.update(d)
        return new_dict

    # map version to cost map(instruction to cost)
    cost_table: Dict[int, Dict[str, int]] = {}

    cost_table[1] = changes_version_1
    cost_table[2] = _combine_dicts([cost_table[1], changes_version_2])
    cost_table[3] = cost_table[2]
    cost_table[4] = _combine_dicts([cost_table[3], changes_version_4])
    cost_table[5] = _combine_dicts([cost_table[4], changes_version_5])

    # ignore immediate arguments as execution cost is independent of it
    # for all instructions
    ins = ins_str.strip().split(" ")[0]

    return cost_table[version].get(ins, 1)
