from typing import Optional

from tealer.teal.instructions import instructions
from tealer.teal.instructions.parse_global_field import parse_global_field
from tealer.teal.instructions.parse_transaction_field import parse_transaction_field


def handle_gtnx(x: str) -> instructions.Gtxn:
    split = x.split(" ")
    idx = int(split[0])
    tx_field = parse_transaction_field(" ".join(split[1:]))
    return instructions.Gtxn(idx, tx_field)


def handle_gtnxa(x: str) -> instructions.Gtxna:
    split = x.split(" ")
    idx = int(split[0])
    tx_field = parse_transaction_field(" ".join(split[1:]))
    return instructions.Gtxna(idx, tx_field)


# Order in the parser_rules is important
parser_rules = [
    ("#pragma version ", lambda x: instructions.Pragma(x)),
    ("err", lambda _x: instructions.Err()),
    ("int ", lambda x: instructions.Int(x)),
    ("txn ", lambda x: instructions.Txn(parse_transaction_field(x))),
    ("txna ", lambda x: instructions.Txna(parse_transaction_field(x))),
    ("gtxn ", lambda x: handle_gtnx(x)),
    ("gtxna ", lambda x: handle_gtnxa(x)),
    ("load ", lambda x: instructions.Load(int(x))),
    ("store ", lambda x: instructions.Store(int(x))),
    ("sha256", lambda _x: instructions.Sha256()),
    ("sha512_256", lambda _x: instructions.Sha512_256()),
    ("keccak256", lambda _x: instructions.Keccak256()),
    ("ed25519verify", lambda _x: instructions.Ed25519verify()),
    ("global ", lambda x: instructions.Global(parse_global_field(x))),
    ("dup2", lambda _x: instructions.Dup2()),
    ("dup", lambda _x: instructions.Dup()),
    ("concat", lambda _x: instructions.Concat()),
    ("b ", lambda x: instructions.B(x)),
    ("bz ", lambda x: instructions.BZ(x)),
    ("bnz ", lambda x: instructions.BNZ(x)),
    ("return", lambda x: instructions.Return()),
    ("app_global_get_ex", lambda x: instructions.AppGlobalGetEx()),
    ("app_global_get", lambda x: instructions.AppGlobalGet()),
    ("app_global_put", lambda x: instructions.AppGlobalPut()),
    ("app_global_del", lambda x: instructions.AppGlobalDel()),
    ("app_local_get_ex", lambda x: instructions.AppLocalGetEx()),
    ("app_local_get", lambda x: instructions.AppLocalGet()),
    ("app_local_put", lambda x: instructions.AppLocalPut()),
    ("app_local_del", lambda x: instructions.AppLocalDel()),
    ("app_opted_in", lambda x: instructions.AppOptedIn()),
    ("balance", lambda x: instructions.Balance()),
    ("asset_holding_get", lambda x: instructions.AssetHoldingGet()),
    ("asset_params_get", lambda x: instructions.AssetParamsGet()),
    ("%", lambda x: instructions.Modulo()),
    ("!=", lambda x: instructions.Neq()),
    ("!", lambda x: instructions.Not()),
    ("==", lambda x: instructions.Eq()),
    ("&&", lambda x: instructions.And()),
    ("&", lambda x: instructions.BitwiseAnd()),
    ("||", lambda x: instructions.Or()),
    ("|", lambda x: instructions.BitwiseOr()),
    ("+", lambda x: instructions.Add()),
    ("-", lambda x: instructions.Sub()),
    ("/", lambda x: instructions.Div()),
    ("*", lambda x: instructions.Mul()),
    (">=", lambda x: instructions.GreaterE()),
    (">", lambda x: instructions.Greater()),
    ("<=", lambda x: instructions.LessE()),
    ("<", lambda x: instructions.Less()),
    ("^", lambda x: instructions.BitwiseXor()),
    ("~", lambda x: instructions.BitwiseInvert()),
    ("itob", lambda x: instructions.Itob()),
    ("btoi", lambda x: instructions.Btoi()),
    ("byte base64", lambda x: instructions.ByteBase64(x)),
    ("byte ", lambda x: instructions.Byte(x)),
    ("pop", lambda x: instructions.Pop()),
    ("addr ", lambda x: instructions.Addr(x)),
    ("mulw", lambda x: instructions.Mulw()),
    ("addw", lambda x: instructions.Addw()),
    ("intcblock", lambda x: instructions.Intcblock()),
    ("intc ", lambda x: instructions.Intc(x)),
    ("intc_0", lambda x: instructions.Intc0()),
    ("intc_1", lambda x: instructions.Intc1()),
    ("intc_2", lambda x: instructions.Intc2()),
    ("intc_3", lambda x: instructions.Intc3()),
    ("bytec ", lambda x: instructions.Bytec(x)),
    ("bytec_0", lambda x: instructions.Bytec0()),
    ("bytec_1", lambda x: instructions.Bytec1()),
    ("bytec_2", lambda x: instructions.Bytec2()),
    ("bytec_3", lambda x: instructions.Bytec3()),
    ("arg ", lambda x: instructions.Arg(x)),
    ("arg_0", lambda x: instructions.Arg0()),
    ("arg_1", lambda x: instructions.Arg1()),
    ("arg_2", lambda x: instructions.Arg2()),
    ("arg_3", lambda x: instructions.Arg3()),
    ("len", lambda x: instructions.Len()),
    ("bytecblock", lambda x: instructions.Bytecblock()),
    ("substring ", lambda x: instructions.Substring(x.split(" ")[0], x.split(" ")[1])),
    ("substring3", lambda x: instructions.Substring3()),
]


def parse_line(line: str) -> Optional[instructions.Instruction]:
    if "//" in line:
        line = line[0 : line.find("//")]
    if ":" in line:
        return instructions.Label(line[0 : line.find(":")])
    for key, f in parser_rules:
        if line.startswith(key):
            return f(line[len(key) :])
    if line:
        print(f"Not found {line}")
        return None
    return None
