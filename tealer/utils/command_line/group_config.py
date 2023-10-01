import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Optional
import yaml

from tealer.utils.teal_enums import TransactionType


GROUP_CONFIG_CONTRACT_TYPES = [
    "LogicSig",
    "ApprovalProgram",
    "ClearStateProgram",
]

USER_CONFIG_TRANSACTION_TYPES = {
    "pay": TransactionType.Pay,
    "keyreg": TransactionType.KeyReg,
    "acfg": TransactionType.Acfg,
    "axfer": TransactionType.Axfer,
    "afrz": TransactionType.Afrz,
    "appl": TransactionType.Appl,
    "txn": TransactionType.Any,
}


class InvalidGroupConfiguration(Exception):
    pass


def check_fields_are_present(required_fields: List[str], config: Dict[str, Any]) -> List[str]:
    absent_fields: List[str] = []
    for field in required_fields:
        if field not in config:
            absent_fields.append(field)
    return absent_fields


@dataclass
class GroupConfigFunction:
    name: str
    dispatch_path: List[str]

    @staticmethod
    def from_yaml(function: Dict[str, Any]) -> "GroupConfigFunction":
        if "name" not in function:
            raise InvalidGroupConfiguration("function name is not given")
        name: str = function["name"]
        absent_fields = check_fields_are_present(["dispatch_path"], function)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Function name: {name}\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )

        dispatch_path: List[str] = function["dispatch_path"]
        for block_id in dispatch_path:
            if not block_id.startswith("B") or not block_id[1:].isdigit():
                raise InvalidGroupConfiguration(
                    f"Function name: {name}\nIncorrect block id in dispatch path: {dispatch_path}"
                )

        return GroupConfigFunction(name, dispatch_path)

    def to_yaml(self) -> Dict[str, Any]:
        return {"name": self.name, "dispatch_path": self.dispatch_path}


@dataclass
class GroupConfigContract:
    name: str
    file_path: Path
    contract_type: str
    version: int
    subroutines: List[str]
    functions: List[GroupConfigFunction]

    @staticmethod
    def from_yaml(contract: Dict[str, Any]) -> "GroupConfigContract":
        if "name" not in contract:
            raise InvalidGroupConfiguration("contract name is not given")
        name: str = contract["name"]

        required_fields = ["file_path", "type", "version", "subroutines", "functions"]
        absent_fields: List[str] = []
        for field in required_fields:
            if field not in contract:
                absent_fields.append(field)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Contract name: {name}\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )

        file_path: Path = Path(contract["file_path"])
        contract_type: str = contract["type"]
        version: int = contract["version"]
        subroutines: List[str] = contract["subroutines"]

        if contract_type not in GROUP_CONFIG_CONTRACT_TYPES:
            raise InvalidGroupConfiguration(
                f"Contract name: {name}\n Invalid contract type: {contract_type}"
            )

        functions: List[Dict[str, Any]] = contract["functions"]
        parsed_functions: List[GroupConfigFunction] = []

        for function in functions:
            try:
                parsed_functions.append(GroupConfigFunction.from_yaml(function))
            except InvalidGroupConfiguration as err:
                # pylint: disable=raise-missing-from
                raise InvalidGroupConfiguration(f"Contract name: {name}\n{err}")

        return GroupConfigContract(
            name, file_path, contract_type, version, subroutines, parsed_functions
        )

    def to_yaml(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "file_path": self.file_path,
            "type": self.contract_type,
            "version": self.version,
            "subroutines": self.subroutines,
            "functions": [function.to_yaml() for function in self.functions],
        }


@dataclass
class GroupConfigFunctionCall:
    contract: str
    function: str

    @staticmethod
    def from_yaml(function_call: Dict[str, Any]) -> "GroupConfigFunctionCall":
        absent_fields = check_fields_are_present(["contract", "function"], function_call)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Function call:\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )
        contract = function_call["contract"]
        function = function_call["function"]

        return GroupConfigFunctionCall(contract, function)

    def to_yaml(self) -> Dict[str, Any]:
        return {
            "contract": self.contract,
            "function": self.function,
        }


@dataclass
class GroupConfigTransaction:
    txn_id: str
    txn_type: str
    application: Optional[GroupConfigFunctionCall] = None
    has_logic_sig: Optional[bool] = None
    logic_sig: Optional[GroupConfigFunctionCall] = None
    absolute_index: Optional[int] = None
    relative_indexes: Optional[Dict[str, int]] = None

    @staticmethod
    def from_yaml(transaction: Dict[str, Any]) -> "GroupConfigTransaction":
        absent_fields = check_fields_are_present(["txn_id", "txn_type"], transaction)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Transaction:\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )

        txn_id = transaction["txn_id"]
        txn_type = transaction["txn_type"]
        if txn_type not in USER_CONFIG_TRANSACTION_TYPES:
            raise InvalidGroupConfiguration(
                f"Transaction: Unknown transaction type {txn_type} of transaction {txn_id}"
            )
        application = transaction.get("application")
        has_logic_sig = transaction.get("has_logic_sig")
        logic_sig = transaction.get("logic_sig")
        absolute_index = transaction.get("absolute_index")
        relative_indexes = transaction.get("relative_indexes")

        if application is not None:
            application = GroupConfigFunctionCall.from_yaml(application)

        if logic_sig is not None:
            logic_sig = GroupConfigFunctionCall.from_yaml(logic_sig)

        if relative_indexes is not None:
            parsed_relative_indexes: Dict[str, int] = {}
            for relative_index in relative_indexes:
                absent_fields = check_fields_are_present(["other_txn_id", "offset"], relative_index)
                if absent_fields:
                    raise InvalidGroupConfiguration(
                        f'Transaction: {txn_id}\n\nFollowing Required fields are absent in relative_indexes: {", ".join(absent_fields)}'
                    )
                parsed_relative_indexes[relative_index["other_txn_id"]] = relative_index["offset"]
            relative_indexes = parsed_relative_indexes

        return GroupConfigTransaction(
            txn_id,
            txn_type,
            application,
            has_logic_sig,
            logic_sig,
            absolute_index,
            relative_indexes,
        )

    def to_yaml(self) -> Dict[str, Any]:
        output: Dict[str, Any] = {
            "txn_id": self.txn_id,
            "txn_type": self.txn_type,
        }
        if self.application is not None:
            output["application"] = self.application.to_yaml()
        if self.logic_sig is not None:
            output["logic_sig"] = self.logic_sig.to_yaml()
        if self.has_logic_sig is not None:
            output["has_logic_sig"] = self.has_logic_sig
        if self.absolute_index is not None:
            output["absolute_index"] = self.absolute_index
        if self.relative_indexes is not None:
            relative_indexes = []
            for txn_id, offset in self.relative_indexes.items():
                relative_indexes.append(
                    {
                        "other_txn_id": txn_id,
                        "offset": offset,
                    }
                )
            output["relative_indexes"] = relative_indexes

        return output


@dataclass
class GroupConfigGroup:
    operation: str
    transactions: List[GroupConfigTransaction]

    @staticmethod
    def from_yaml(group: Dict[str, Any]) -> "GroupConfigGroup":
        absent_fields = check_fields_are_present(["operation", "transactions"], group)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Group:\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )

        operation = group["operation"]
        parsed_transactions = []
        for transaction in group["transactions"]:
            parsed_transactions.append(GroupConfigTransaction.from_yaml(transaction))

        return GroupConfigGroup(operation, parsed_transactions)

    def to_yaml(self) -> Dict[str, Any]:
        return {
            "operation": self.operation,
            "transactions": [transaction.to_yaml() for transaction in self.transactions],
        }


@dataclass
class GroupConfig:
    name: str
    contracts: List[GroupConfigContract]
    groups: List[GroupConfigGroup]

    @staticmethod
    def from_yaml(config: Dict[str, Any]) -> "GroupConfig":
        absent_fields = check_fields_are_present(["name", "contracts", "groups"], config)
        if absent_fields:
            raise InvalidGroupConfiguration(
                f'Config:\n\nFollowing Required fields are absent: {", ".join(absent_fields)}'
            )
        name = config["name"]
        contracts = []
        for contract in config["contracts"]:
            contracts.append(GroupConfigContract.from_yaml(contract))
        groups = []
        for group in config["groups"]:
            groups.append(GroupConfigGroup.from_yaml(group))

        return GroupConfig(name, contracts, groups)

    def to_yaml(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "contracts": [contract.to_yaml() for contract in self.contracts],
            "groups": [group.to_yaml() for group in self.groups],
        }


def write_to_yaml_file(file: Path, output: Dict[str, Any]) -> None:
    with open(file, "w", encoding="utf-8") as f:
        # yaml = YAML()
        # yaml.indent(sequence=4, offset=2)
        # yaml.dump(output, f)
        yaml.safe_dump(output, f, sort_keys=False)


def read_config_from_file(file: Path) -> GroupConfig:
    with open(file, encoding="utf-8") as f:
        d = yaml.safe_load(f.read())
    try:
        parsed_config = GroupConfig.from_yaml(d)
        # given file_path is relative path of the contract from config file.
        for contract in parsed_config.contracts:
            contract.file_path = file.parent / contract.file_path
        return parsed_config
    except InvalidGroupConfiguration as err:
        print(f"\nInvalidGroupConfiguration:\n\n{err}")
        print(err)
        sys.exit(1)


# if __name__ == "__main__":
# filename = "tests/group_transactions/ans/ans_config.yaml"
# with open("tests/group_transactions/ans_config.yaml") as f:
# try:
# if 1:
# parsed_config = read_config_from_file(filename)
# write_to_yaml_file(Path("test.yaml"), parsed_config.to_yaml())
# except InvalidGroupConfiguration as err:
# print(f"\nInvalidGroupConfiguration:\n\n{err}")
# print(err)
# sys.exit(1)
