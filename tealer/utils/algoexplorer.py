"""
Helpers to fetch contract from the Algorand network using indexer.

## Test cases(Mainnet)

App id:
    - Invalid app id: 1
    - Valid app id: 991196662

Transaction id:
    - normal_txn (not signed with logic-sig): METJ6SNMBLTBVBLADEQFY6Y6CVPI4ZMSF23HVTY2RK7R4OCO6QDQ
    - delegate sig signed with single key: VFFVCSPFBK36ZN2FPDPDI6PFUO44OLZPBU6XPGOIGSR5L2XK6HFQ
    - delegate sig signed with multiple key(multi-sig): NGJOVS7SEEWRIKZNA5WL7FRENXXPUKSFPKJKM5QBYUOM7UZ2SG5Q
    - signed with contract account's sig: ZICHTBTBC6H3CFOGREUPV3G74WRYDM3ZD7W56VMRMCNXOQHP3AYQ

Contract Accounts:
    - Invalid address:  AOOIJDOIJRPZMCPJQWPIJNDISC2XEOZBDN2SNCONSOSDJX27652DNU2HDI
    - Contract account: D6DDUCPSDWD4IA2L3FL4ZC6NVKXGQYOU4LJQMHKV6NVCYHRURSFKYPFN5M
    - Normal account: ZW3ISEHZUHPO7OZGMKLKIIMKVICOUDRCERI454I3DB2BH52HGLSO67W754

### BETANET:

App id:
    - Invalid app id: 1
    - Valid app id: 1496883334      # worked for this application
    - Valid app id: 1497219145      # valid application but is not found by the indexer.

Dropping the support for betanet for now. Having no support is better than something that only works some times.
And supporting betanet is not a priority.

### TESTNET

App id:
    - Invalid app id: 1
    - Valid app id: 115884263
"""

import base64
import json

import requests
from algosdk.v2client.indexer import IndexerClient
from algosdk.error import IndexerHTTPError

from tealer.exceptions import TealerException


def disassemble_using_algo_explorer(code: str) -> str:
    """Disassemble the AVM bytecode to teal using Algorand node v2 api.

    Args:
        code: Compiled bytecode of the contract.

    Returns:
        Returns disassemble Teal code of :code:.

    Raises:
        TealerException: Raises error if the api returned any status code other than the
            success code (200).
    """
    base = "https://node.algoexplorerapi.io/"
    url = "v2/teal/disassemble"
    headers = {"Content-Type": "application/x-binary"}
    code_bin = base64.b64decode(code)
    r = requests.post(base + url, data=code_bin, headers=headers)
    if r.status_code != 200:
        raise TealerException(f'Unable to disassemble contract: "{code}"')
    disassembly = json.loads(r.text)["result"]
    return disassembly


def get_indexer(network: str) -> IndexerClient:
    main_net_base_url = "https://algoindexer.algoexplorerapi.io/"
    test_net_base_url = "https://algoindexer.testnet.algoexplorerapi.io/"
    # beta_net_base_url = "https://algoindexer.betanet.algoexplorerapi.io/"
    if network.lower() == "testnet":
        indexer_base_url = test_net_base_url
        print('Network: "TESTNET"')
    # Betannet is not supported
    # elif network == "betanet":
    #     indexer_base_url = beta_net_base_url
    #     print('Network: "BETANET"')
    elif network.lower() == "mainnet":
        indexer_base_url = main_net_base_url
        print('Network: "MAINET"')
    else:
        raise TealerException(f'Network "{network}" is not supported')

    return IndexerClient(indexer_token="", indexer_address=indexer_base_url)  # type: ignore


def get_application_using_app_id(network: str, app_id: int) -> str:
    """Downloads approval program using the application id

    Args:
        network: Algorand network identifier.
        app_id: Application Id.

    Returns:
        Returns disassembled Teal code of the :app_id: application fetched from the :network:.

    Raises:
        TealerException: Raises error if the function cannot find the application :app_id: in the
            :network:.
    """
    try:
        response = get_indexer(network).applications(application_id=app_id)  # type: ignore
    except IndexerHTTPError as e:
        raise TealerException(f'Unable to fetch application "{app_id}"\n{e}') from e
    approval = response["application"]["params"]["approval-program"]
    # clear = response["application"]["params"]["clear-state-program"]
    return disassemble_using_algo_explorer(approval)


def logic_sig_from_contract_account(network: str, account_address: str) -> str:
    """Find logic sig of a contract account.

    Logic sig of a contract account is not part of the account and is not stored in the
    blockchain state.

    In order to find the logic sig, find a transaction from the contract account and
    get the logic sig from that.

    Args:
        network: Algorand network identifier.
        account_address: An Algorand account address derived from a LogicSig.

    Returns:
        Returns disassembled Teal code of the contract controlling the contract account :account_address:.
        Contract is searched in the :network:.

    Raises:
        TealerException: Raises error if the function cannot find a transaction from the :account_address: in the
            :network:. Happens if the account_address is invalid, account has not made any transactions or the
            search has timed out.
    """
    try:
        results = get_indexer(network).search_transactions(  # type: ignore
            limit=1, sig_type="lsig", address=account_address, address_role="sender"
        )
    except IndexerHTTPError as e:
        # Happens if account_address is invalid.
        # or The search has timed-out.
        raise TealerException(
            f'Could not find logic signature for contract account "{account_address}"\n{e}'
        ) from e
    transactions = results["transactions"]
    if len(transactions) == 0:
        # Search has finished and didn't find any transactions.
        # -> Either account_address is not a contract account Or
        # -> There is not a single transaction from the account.
        raise TealerException(
            f'Account "{account_address}" is not a contract account.\n'
            "Note: Account should have made submitted atleast one transaction for tealer to find the contract"
        )
    signature = transactions[0]["signature"]["logicsig"]
    if "multi-signature" in signature or "signature" in signature:
        # delegate signature, not a contract account
        raise TealerException(f'Account "{account_address}" is not a contract account.')
    logic_sig = signature["logic"]
    return disassemble_using_algo_explorer(logic_sig)


def logic_sig_from_txn_id(network: str, txn_id: str) -> str:
    """Fetch logic-sig used to sign `txn_id` transaction

    Args:
        network: Algorand network identifier.
        txn_id: Transaction id of a transaction on :network:, the transaction is signed by a logic-sig.

    Returns:
        Returns disassembled Teal code of the contract that signed the transaction :txn_id:.
        The transaction is searched in the :network:.

    Raises:
        TealerException: Raises error if the function cannot find the transaction :txn_id: in the
            :network:
    """
    try:
        txn_info = get_indexer(network).transaction(txn_id)  # type: ignore
    except IndexerHTTPError as e:
        # will happen if txn_id is not a valid base32 string(irrespective of padding)
        # or There's no transaction with the given txn_id
        raise TealerException(f'Invalid transaction id: "{txn_id}"\n{e}') from e

    signature = txn_info["transaction"]["signature"]
    if "logicsig" not in signature:
        raise TealerException(f'Transaction "{txn_id}" is not signed using a logic signature.')
    logic_sig = signature["logicsig"]["logic"]
    return disassemble_using_algo_explorer(logic_sig)
