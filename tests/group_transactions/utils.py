from typing import Dict, Any, List
from dataclasses import dataclass
from pathlib import Path
import yaml


class InvalidTestCase(Exception):
    pass


@dataclass
class OutputContract:
    contract_name: str
    function_name: str

    @staticmethod
    def from_yaml(contract: Dict[str, Any]) -> "OutputContract":
        if "contract" not in contract or "function" not in contract:
            raise InvalidTestCase(
                f"Missing required fields in the contract description: {contract}"
            )
        return OutputContract(contract["contract"], contract["function"])


@dataclass
class OutputTransaction:
    transaction_id: str
    contracts: List[OutputContract]

    @staticmethod
    def from_yaml(transaction: Dict[str, Any]) -> "OutputTransaction":
        if "txn_id" not in transaction:
            raise InvalidTestCase(f'Missing "txn_id" field for the transaction {transaction}')

        contracts = []
        if "contracts" in transaction:
            for contract in transaction["contracts"]:
                contracts.append(OutputContract.from_yaml(contract))
        return OutputTransaction(
            transaction["txn_id"],
            sorted(contracts, key=lambda x: (x.contract_name, x.function_name)),
        )


@dataclass
class OutputOperation:
    operation: str
    vulnerable_transactions: List[OutputTransaction]

    @staticmethod
    def from_yaml(operation: Dict[str, Any]) -> "OutputOperation":
        if "operation" not in operation or "vulnerable_transactions" not in operation:
            raise InvalidTestCase(f"Missing required fields in the operation: {operation}")

        operation_name = operation["operation"]

        vulnerable_transactions = []
        for transaction in operation["vulnerable_transactions"]:
            vulnerable_transactions.append(OutputTransaction.from_yaml(transaction))

        return OutputOperation(operation_name, vulnerable_transactions)


@dataclass
class ExpectedOutput:
    name: str
    operations: List[OutputOperation]

    @staticmethod
    def from_yaml(output: Dict[str, Any]) -> "ExpectedOutput":
        if "name" not in output or "operations" not in output:
            raise InvalidTestCase(f"Missing required fields in the expected output: {output}")

        name = output["name"]
        operations = []
        for operation in output["operations"]:
            operations.append(OutputOperation.from_yaml(operation))
        return ExpectedOutput(name, operations)


def expected_output_from_file(file_path: Path) -> "ExpectedOutput":
    with open(file_path, encoding="utf-8") as f:
        # print(yaml.safe_load(f.read()))
        return ExpectedOutput.from_yaml(yaml.safe_load(f.read()))
