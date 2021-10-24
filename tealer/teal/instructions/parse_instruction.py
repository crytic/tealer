from typing import Optional

from tealer.teal.instructions import instructions
from tealer.teal.instructions.parse_global_field import parse_global_field
from tealer.teal.instructions.parse_transaction_field import parse_transaction_field
from tealer.teal.instructions.parse_asset_holding_field import parse_asset_holding_field
from tealer.teal.instructions.parse_asset_params_field import parse_asset_params_field
from tealer.teal.instructions.parse_app_params_field import parse_app_params_field


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


def handle_itxna(x: str) -> instructions.Itxna:
    args = x.split(" ")
    tx_field = parse_transaction_field(args[0])
    idx = int(args[1])
    return instructions.Itxna(tx_field, idx)


def handle_extract(x: str) -> instructions.Extract:
    args = x.split(" ")
    print(args)
    start = int(args[0])
    length = int(args[1])
    return instructions.Extract(start, length)


# Order in the parser_rules is important
parser_rules = [
    ("#pragma version ", lambda x: instructions.Pragma(x)),
    ("err", lambda _x: instructions.Err()),
    ("assert", lambda _x: instructions.Assert()),
    ("int ", lambda x: instructions.Int(x)),
    ("pushint ", lambda x: instructions.PushInt(x)),
    ("txn ", lambda x: instructions.Txn(parse_transaction_field(x))),
    ("txna ", lambda x: instructions.Txna(parse_transaction_field(x))),
    ("gtxn ", lambda x: handle_gtnx(x)),
    ("gtxna ", lambda x: handle_gtnxa(x)),
    ("gtxns ", lambda x: instructions.Gtxns(parse_transaction_field(x))),
    ("gtxnsa ", lambda x: instructions.Gtxnsa(parse_transaction_field(x))),
    ("load ", lambda x: instructions.Load(int(x))),
    ("store ", lambda x: instructions.Store(int(x))),
    ("gload ", lambda x: instructions.Gload(int(x.split(" ")[0]), int(x.split(" ")[1]))),
    ("gloads ", lambda x: instructions.Gloads(int(x))),
    ("gaid ", lambda x: instructions.Gaid(int(x))),
    ("gaids", lambda x: instructions.Gaids()),
    ("loads", lambda _x: instructions.Loads()),
    ("stores", lambda _x: instructions.Stores()),
    ("dig ", lambda x: instructions.Dig(int(x))),
    ("swap", lambda _x: instructions.Swap()),
    ("getbit", lambda _x: instructions.GetBit()),
    ("setbit", lambda _x: instructions.SetBit()),
    ("getbyte", lambda _x: instructions.GetByte()),
    ("setbyte", lambda _x: instructions.SetByte()),
    ("extract ", lambda x: handle_extract(x)),
    ("extract3", lambda _x: instructions.Extract3()),
    ("extract_uint16", lambda _x: instructions.Extract_uint16()),
    ("extract_uint32", lambda _x: instructions.Extract_uint32()),
    ("extract_uint64", lambda _x: instructions.Extract_uint64()),
    ("sha256", lambda _x: instructions.Sha256()),
    ("sha512_256", lambda _x: instructions.Sha512_256()),
    ("keccak256", lambda _x: instructions.Keccak256()),
    ("ed25519verify", lambda _x: instructions.Ed25519verify()),
    ("ecdsa_verify", lambda x: instructions.Ecdsa_verify(x)),
    ("ecdsa_pk_decompress", lambda x: instructions.Ecdsa_pk_decompress(x)),
    ("ecdsa_pk_recover", lambda x: instructions.Ecdsa_pk_recover(x)),
    ("global ", lambda x: instructions.Global(parse_global_field(x))),
    ("dup2", lambda _x: instructions.Dup2()),
    ("dup", lambda _x: instructions.Dup()),
    ("select", lambda _x: instructions.Select()),
    ("cover", lambda x: instructions.Cover(int(x))),
    ("uncover", lambda x: instructions.Uncover(int(x))),
    ("concat", lambda _x: instructions.Concat()),
    ("b ", lambda x: instructions.B(x)),
    ("bz ", lambda x: instructions.BZ(x)),
    ("bnz ", lambda x: instructions.BNZ(x)),
    ("return", lambda x: instructions.Return()),
    ("callsub ", lambda x: instructions.Callsub(x)),
    ("retsub", lambda x: instructions.Retsub()),
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
    ("min_balance", lambda x: instructions.MinBalance()),
    ("asset_holding_get ", lambda x: instructions.AssetHoldingGet(parse_asset_holding_field(x))),
    ("asset_params_get ", lambda x: instructions.AssetParamsGet(parse_asset_params_field(x))),
    ("app_params_get ", lambda x: instructions.AppParamsGet(parse_app_params_field(x))),
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
    ("bitlen", lambda _x: instructions.BitLen()),
    ("b%", lambda x: instructions.BModulo()),
    ("b!=", lambda x: instructions.BNeq()),
    ("b==", lambda x: instructions.BEq()),
    ("b&", lambda x: instructions.BBitwiseAnd()),
    ("b|", lambda x: instructions.BBitwiseOr()),
    ("b+", lambda x: instructions.BAdd()),
    ("b-", lambda x: instructions.BSubtract()),
    ("b/", lambda x: instructions.BDiv()),
    ("b*", lambda x: instructions.BMul()),
    ("b>=", lambda x: instructions.BGreaterE()),
    ("b>", lambda x: instructions.BGreater()),
    ("b<=", lambda x: instructions.BLessE()),
    ("b<", lambda x: instructions.BLess()),
    ("b^", lambda x: instructions.BBitwiseXor()),
    ("b~", lambda x: instructions.BBitwiseInvert()),
    ("bzero", lambda x: instructions.BZero()),
    ("log", lambda _x: instructions.Log()),
    ("itxn_begin", lambda _x: instructions.Itxn_begin()),
    ("itxn_field ", lambda x: instructions.Itxn_field(parse_transaction_field(x))),
    ("itxn_submit", lambda _x: instructions.Itxn_submit()),
    ("itxn ", lambda x: instructions.Itxn(parse_transaction_field(x))),
    ("itxna ", lambda x: handle_itxna(x)),
    ("itob", lambda x: instructions.Itob()),
    ("btoi", lambda x: instructions.Btoi()),
    ("byte base64", lambda x: instructions.ByteBase64(x)),
    ("byte ", lambda x: instructions.Byte(x)),
    ("pushbytes ", lambda x: instructions.PushBytes(x)),
    ("pop", lambda x: instructions.Pop()),
    ("addr ", lambda x: instructions.Addr(x)),
    ("mulw", lambda x: instructions.Mulw()),
    ("addw", lambda x: instructions.Addw()),
    ("divmodw", lambda x: instructions.Divmodw()),
    ("expw", lambda x: instructions.Expw()),
    ("exp", lambda x: instructions.Exp()),
    ("shl", lambda x: instructions.Shl()),
    ("shr", lambda x: instructions.Shr()),
    ("sqrt", lambda x: instructions.Sqrt()),
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
    comment = ""
    if "//" in line:
        comment_start = line.find("//")
        # save comment
        comment = line[comment_start:]
        # strip line of comments and leading/trailing whitespace
        line = line[:comment_start].strip()
    if ":" in line:
        return instructions.Label(line[0 : line.find(":")])
    for key, f in parser_rules:
        if line.startswith(key):
            ins = f(line[len(key) :].strip())
            ins.comment = comment
            return ins
    if line:
        print(f"Not found {line}")
        return None
    return None
