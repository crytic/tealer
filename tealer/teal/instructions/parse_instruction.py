"""Parser for teal instructions.

Each teal instruction is represented as a class. Parsing teal instructions
is creating the correct Instruction subclass instance and setting the fields
of it given the source code line.

Each teal instruction in the source code start with a fixed prefix. A instruction
might contain additional immediate values which need to be handled case by case.
Instruction parser works by first creating a list where each item has the fixed prefix
for the instruction and a callable(function) that will handle parsing of immediate
arguments specific to that instruction. All the callables take a string containing
all the immediate arguments and return the instruction object with the parsed immediates.

In teal contracts, a source line might contain comments, indentation, additional to the
instruction. Teal comments in the same line as the instruction will be stored in the
instruction object. Indentation, comments without a instruction, empty lines are all
ignored by the instruction parser.

Attributes:
    parser_rules (List[Tuple[str, Callable[[str], Instruction]]]):
        List of tuple each containing the instruction prefix and a callable.
        Callable handles the parsing of immediate arguments of the instruction and
        creation of instruction object.

Exceptions:
    ParseError: Exception class to represent errors raised while parsing
        invalid or incorrectly formatted instructions.
"""

from typing import Optional, Callable, Tuple, List
import base64

from tealer.teal.instructions import instructions
from tealer.teal.instructions.instructions import Instruction
from tealer.teal.instructions.parse_acct_params_field import parse_acct_params_field
from tealer.teal.instructions.parse_app_params_field import parse_app_params_field
from tealer.teal.instructions.parse_asset_holding_field import parse_asset_holding_field
from tealer.teal.instructions.parse_asset_params_field import parse_asset_params_field
from tealer.teal.instructions.parse_global_field import parse_global_field
from tealer.teal.instructions.parse_transaction_field import parse_transaction_field


class ParseError(Exception):
    """Exception class to represent instruction parsing errors."""


def handle_gtxn(x: str, itxn: bool = False) -> Instruction:
    """Parse gtxn instruction.

    Args:
        x: proper string representation of gtxn instruction immediate
            arguments.
        itxn: True if the instruction is gitxn

    Returns:
        Gtxn instruction object created after parsing immediate
        arguments.
    """

    split = x.split(" ")
    idx = _parse_int(split[0])
    tx_field = parse_transaction_field(" ".join(split[1:]), False)
    if itxn:
        return instructions.Gitxn(idx, tx_field)
    return instructions.Gtxn(idx, tx_field)


def handle_gtxna(x: str, itxn: bool = False) -> Instruction:
    """Parse gtxna instruction.

    Args:
        x: proper string representation of gtxna instruction immediate
            arguments.
        itxn: True if the instruction is gitxna

    Returns:
        Gtxna instruction object created after parsing immediate
        arguments.
    """

    split = x.split(" ")
    idx = _parse_int(split[0])
    tx_field = parse_transaction_field(" ".join(split[1:]), False)
    if itxn:
        return instructions.Gitxna(idx, tx_field)
    return instructions.Gtxna(idx, tx_field)


def handle_gtxnas(x: str, itxn: bool = False) -> Instruction:
    """Parse gtxnas instruction.

    Args:
        x: proper string representation of gtxnas instruction
            immediate arguments.
        itxn: True if the instruction is gitxnas

    Returns:
        Gtxnas instruction object created after parsing immediate
        arguments.
    """

    args = x.split(" ")
    idx = _parse_int(args[0])
    tx_field = parse_transaction_field(args[1], True)
    if itxn:
        return instructions.Gitxnas(idx, tx_field)
    return instructions.Gtxnas(idx, tx_field)


def _parse_int(x: str) -> int:
    """Parse teal integers.

    Teal supports three formats to write integers: hex, octal and
    decimal. hexadecimal numbers start with the prefix 0x and octal
    numbers have prefix 0.

    Args:
        x: string representation of the teal integer.

    Returns:
        python integer equal to the value represented by the given
        teal integer.
    """

    if x.startswith("0x"):
        return int(x[2:], 16)
    if x.startswith("0"):
        return int(x, 8)
    return int(x)


def _split_instruction_into_tokens(line: str) -> List[str]:
    """Split given instruction into tokens.

    Teal instructions are divided into tokens. Tokens in teal are
    comments, string literals or sequence of non-space characters.

    Args:
        line (str): string representation of teal instruction.

    Returns:
        List[str]: List of tokens.

    Examples:
        >>> _split_instruction_into_tokens('a "string" // comment')
        ['a', '"string"', '// comment']
        >>> _split_instruction_into_tokens('a "s tring //" // "comment"')
        ['a', '"s tring //"', '// "comment"']

    Raises:
        ParseError: raises ParseError if string literals are not
            properly enclosed in the line.
    """

    fields: List[str] = []
    line = line.strip()
    i = 0
    start = i
    while i < len(line):
        if line[i].isspace():
            if start != i:
                fields.append(line[start:i].strip())
            i += 1
            start = i
        elif line[i] == '"':
            if start != i:
                i += 1
                continue
            i += 1
            while i < len(line):
                if line[i] == '"' and line[i - 1] != "\\":
                    fields.append(line[start : i + 1])
                    i += 1
                    start = i
                    break
                i += 1
            else:
                raise ParseError(f"missing closing qoute {line}")
        elif line[i : i + 2] == "//":
            fields.append(line[i:])
            return fields
        else:
            i += 1
    if start < len(line):
        fields.append(line[start:].strip())
    return fields


def _b64_decode(s: str) -> str:
    """Return hex representation of base64 encoded string.

    Args:
        s: base64 encoded string.

    Returns:
        hex representation of the given string with the prefix "0x"
    """

    return "0x" + base64.b64decode(s + "=" * (-len(s) % 4)).hex()


def _b32_decode(s: str) -> str:
    """Return hex representation of base32 encoded string.

    Args:
        s: base32 encoded string.

    Returns:
        hex representation of the given string with the prefix "0x"
    """

    return "0x" + base64.b32decode(s + "=" * (-len(s) % 8)).hex()


def _parse_byte_arguments(fields: List[str]) -> List[str]:
    """Parse multiple representations of teal byte literals.

    Parses byte literals and convert all base encoded strings to hex
    encoding. currently parses following formats
    base64 AAAA..., b64 AAAA..., base64(AAAA...), b64(AAAA...),
    base32 AAAA..., b32 AAAA..., base32(AAAA...), b32(AAAA...),
    0x0123..., "literal".

    Args:
        fields (List[str]): list of space separated fields(tokens).

    Returns:
        List[str]: list of byte arguments, all either encoded in
            hex or as string literals.

    Examples:
        >>> _parse_byte_arguments(['base64', 'AA', 'base64(AA)', 'b64(AA)'])
        ['0x00', '0x00', '0x00']
        >>> _parse_byte_arguments(['0x00', '"str"', 'base32', 'AA'])
        ['0x00', '"str"', '0x00']

    Raises:
        ParseError: raises ParseError if the byte arguments are not correctly
            encoded.
    """

    arguments: List[str] = []
    error: bool = False
    i: int = 0
    while i < len(fields) and not error:
        if fields[i] == "base64" or fields[i] == "b64":
            if len(fields) <= i + 1:
                error = True
                break
            arguments.append(_b64_decode(fields[i + 1]))
            i += 2
        elif fields[i] == "base32" or fields[i] == "b32":
            if len(fields) <= i + 1:
                error = True
                break
            arguments.append(_b32_decode(fields[i + 1]))
            i += 2
        elif fields[i].startswith("base64(") or fields[i].startswith("b64("):
            if fields[i][-1] != ")":
                error = True
                break
            data = fields[i].split("(")[1][:-1]
            arguments.append(_b64_decode(data))
            i += 1
        elif fields[i].startswith("base32(") or fields[i].startswith("b32("):
            if fields[i][-1] != ")":
                error = True
                break
            data = fields[i].split("(")[1][:-1]
            arguments.append(_b32_decode(data))
            i += 1
        elif fields[i].startswith("0x") or fields[i].startswith('"'):
            arguments.append(fields[i])
            i += 1
        else:
            error = True
            i += 1
            break
    if error:
        line = " ".join(fields)
        raise ParseError(f"incorrect byte format {line}")
    return arguments


# return true if the given string is a teal integer.
_is_int: Callable[[str], bool] = lambda x: x.startswith("0x") or x.isdigit()


# Order in the parser_rules is important
parser_rules: List[Tuple[str, Callable[[str], Instruction]]] = [
    ("#pragma version ", lambda x: instructions.Pragma(_parse_int(x))),
    ("err", lambda _x: instructions.Err()),
    ("assert", lambda _x: instructions.Assert()),
    ("int ", lambda x: instructions.Int(_parse_int(x) if _is_int(x) else x)),
    ("pushints ", lambda x: instructions.PushInts(list(map(_parse_int, x.split(" "))))),
    ("pushint ", lambda x: instructions.PushInt(_parse_int(x) if _is_int(x) else x)),
    ("txn ", lambda x: instructions.Txn(parse_transaction_field(x, False))),
    ("txna ", lambda x: instructions.Txna(parse_transaction_field(x, False))),
    ("gtxn ", lambda x: handle_gtxn(x)),
    ("gtxna ", lambda x: handle_gtxna(x)),
    ("gtxns ", lambda x: instructions.Gtxns(parse_transaction_field(x, False))),
    ("gtxnsa ", lambda x: instructions.Gtxnsa(parse_transaction_field(x, False))),
    ("load ", lambda x: instructions.Load(_parse_int(x))),
    ("store ", lambda x: instructions.Store(_parse_int(x))),
    (
        "gload ",
        lambda x: instructions.Gload(_parse_int(x.split(" ")[0]), _parse_int(x.split(" ")[1])),
    ),
    ("gloads ", lambda x: instructions.Gloads(_parse_int(x))),
    ("gloadss", lambda _x: instructions.Gloadss()),
    ("gaid ", lambda x: instructions.Gaid(_parse_int(x))),
    ("gaids", lambda x: instructions.Gaids()),
    ("loads", lambda _x: instructions.Loads()),
    ("stores", lambda _x: instructions.Stores()),
    ("dig ", lambda x: instructions.Dig(_parse_int(x))),
    ("swap", lambda _x: instructions.Swap()),
    ("getbit", lambda _x: instructions.GetBit()),
    ("setbit", lambda _x: instructions.SetBit()),
    ("getbyte", lambda _x: instructions.GetByte()),
    ("setbyte", lambda _x: instructions.SetByte()),
    (
        "extract ",
        lambda x: instructions.Extract(_parse_int(x.split(" ")[0]), _parse_int(x.split(" ")[1])),
    ),
    ("extract3", lambda _x: instructions.Extract3()),
    ("extract_uint16", lambda _x: instructions.Extract_uint16()),
    ("extract_uint32", lambda _x: instructions.Extract_uint32()),
    ("extract_uint64", lambda _x: instructions.Extract_uint64()),
    ("sha256", lambda _x: instructions.Sha256()),
    ("sha512_256", lambda _x: instructions.Sha512_256()),
    ("keccak256", lambda _x: instructions.Keccak256()),
    ("ed25519verify_bare", lambda _x: instructions.Ed25519verify_bare()),
    ("ed25519verify", lambda _x: instructions.Ed25519verify()),
    ("ecdsa_verify", lambda x: instructions.Ecdsa_verify(x)),
    ("ecdsa_pk_decompress", lambda x: instructions.Ecdsa_pk_decompress(x)),
    ("ecdsa_pk_recover", lambda x: instructions.Ecdsa_pk_recover(x)),
    ("global ", lambda x: instructions.Global(parse_global_field(x))),
    ("dupn ", lambda x: instructions.Dupn(_parse_int(x))),
    ("dup2", lambda _x: instructions.Dup2()),
    ("dup", lambda _x: instructions.Dup()),
    ("select", lambda _x: instructions.Select()),
    ("cover", lambda x: instructions.Cover(_parse_int(x))),
    ("uncover", lambda x: instructions.Uncover(_parse_int(x))),
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
    ("acct_params_get ", lambda x: instructions.AcctParamsGet(parse_acct_params_field(x))),
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
    ("bsqrt", lambda x: instructions.BSqrt()),
    ("log", lambda _x: instructions.Log()),
    ("itxn_begin", lambda _x: instructions.Itxn_begin()),
    ("itxn_next", lambda _x: instructions.Itxn_next()),
    ("itxn_field ", lambda x: instructions.Itxn_field(parse_transaction_field(x, True))),
    ("itxn_submit", lambda _x: instructions.Itxn_submit()),
    ("itxn ", lambda x: instructions.Itxn(parse_transaction_field(x, False))),
    ("itxna ", lambda x: instructions.Itxna(parse_transaction_field(x, False))),
    ("gitxn ", lambda x: handle_gtxn(x, itxn=True)),
    ("gitxna ", lambda x: handle_gtxna(x, itxn=True)),
    ("gitxnas ", lambda x: handle_gtxnas(x, itxn=True)),
    ("txnas ", lambda x: instructions.Txnas(parse_transaction_field(x, True))),
    ("itxnas ", lambda x: instructions.Itxnas(parse_transaction_field(x, True))),
    ("gtxnas ", lambda x: handle_gtxnas(x)),
    ("gtxnsas ", lambda x: instructions.Gtxnsas(parse_transaction_field(x, True))),
    ("args", lambda _x: instructions.Args()),
    ("itob", lambda x: instructions.Itob()),
    ("btoi", lambda x: instructions.Btoi()),
    ("popn ", lambda x: instructions.Popn(_parse_int(x))),
    ("pop", lambda x: instructions.Pop()),
    ("addr ", lambda x: instructions.Addr(x)),
    ("mulw", lambda x: instructions.Mulw()),
    ("addw", lambda x: instructions.Addw()),
    ("divmodw", lambda x: instructions.Divmodw()),
    ("divw", lambda x: instructions.Divw()),
    ("expw", lambda x: instructions.Expw()),
    ("exp", lambda x: instructions.Exp()),
    ("shl", lambda x: instructions.Shl()),
    ("shr", lambda x: instructions.Shr()),
    ("sqrt", lambda x: instructions.Sqrt()),
    ("intcblock", lambda x: instructions.Intcblock(list(map(_parse_int, x.strip().split())))),
    ("intc ", lambda x: instructions.Intc(_parse_int(x))),
    ("intc_0", lambda x: instructions.Intc0()),
    ("intc_1", lambda x: instructions.Intc1()),
    ("intc_2", lambda x: instructions.Intc2()),
    ("intc_3", lambda x: instructions.Intc3()),
    ("bytec ", lambda x: instructions.Bytec(_parse_int(x))),
    ("bytec_0", lambda x: instructions.Bytec0()),
    ("bytec_1", lambda x: instructions.Bytec1()),
    ("bytec_2", lambda x: instructions.Bytec2()),
    ("bytec_3", lambda x: instructions.Bytec3()),
    ("arg ", lambda x: instructions.Arg(_parse_int(x))),
    ("arg_0", lambda x: instructions.Arg0()),
    ("arg_1", lambda x: instructions.Arg1()),
    ("arg_2", lambda x: instructions.Arg2()),
    ("arg_3", lambda x: instructions.Arg3()),
    ("len", lambda x: instructions.Len()),
    (
        "substring ",
        lambda x: instructions.Substring(_parse_int(x.split(" ")[0]), _parse_int(x.split(" ")[1])),
    ),
    ("substring3", lambda x: instructions.Substring3()),
    ("replace2 ", lambda x: instructions.Replace2(_parse_int(x))),
    ("replace3", lambda _x: instructions.Replace3()),
    ("replace", lambda x: instructions.Replace(None if x == "" else _parse_int(x))),
    ("base64_decode ", lambda x: instructions.Base64_decode(x)),
    ("json_ref ", lambda x: instructions.Json_ref(x)),
    ("sha3_256", lambda _x: instructions.Sha3_256()),
    ("vrf_verify ", lambda x: instructions.Vrf_verify(x)),
    ("block ", lambda x: instructions.Block(x)),
    ("bury ", lambda x: instructions.Bury(_parse_int(x))),
    (
        "proto ",
        lambda x: instructions.Proto(_parse_int(x.split(" ")[0]), _parse_int(x.split(" ")[1])),
    ),
    ("frame_dig ", lambda x: instructions.FrameDig(_parse_int(x))),
    ("frame_bury ", lambda x: instructions.FrameBury(_parse_int(x))),
    ("switch ", lambda x: instructions.Switch(x.split(" "))),
    ("match ", lambda x: instructions.Match(x.split(" "))),
    ("box_create", lambda x: instructions.BoxCreate()),
    ("box_extract", lambda x: instructions.BoxExtract()),
    ("box_replace", lambda x: instructions.BoxReplace()),
    ("box_del", lambda x: instructions.BoxDel()),
    ("box_len", lambda x: instructions.BoxLen()),
    ("box_get", lambda x: instructions.BoxGet()),
    ("box_put", lambda x: instructions.BoxPut()),
]


def parse_line(line: str) -> Optional[instructions.Instruction]:
    """Parse line into a teal instruction.

    This might return None instead of an instance of Instruction subclass
    if the line is empty, contains only comments, etc.

    Args:
        line: Teal source code line to parse.

    Returns:
        returns instance of Instruction subclass corresponding to the given
        string representation if :line: contains a valid representation or
        else returns None.

    Raises:
        ParseError: raises ParseError if the instruction present in the given
            line is not correctly formatted and if is not valid.
    """
    if not line.strip():
        return None

    source_code_line = line
    fields = _split_instruction_into_tokens(line)
    comment = ""
    if fields[-1].startswith("//"):
        comment = fields[-1]
        fields = fields[:-1]

    if not fields:
        return None

    ins: Optional[Instruction] = None
    if fields[0][-1] == ":":
        if len(fields) != 1:
            raise ParseError(f"incorrect format of label: {line}")
        ins = instructions.Label(fields[0][:-1])

    if fields[0] == "byte" or fields[0] == "pushbytes" or fields[0] == "method":
        imm: List[str] = _parse_byte_arguments(fields[1:])
        if len(imm) != 1:
            raise ParseError(f"{fields[0]} expects exactly one argument: {line}")
        ins = {
            "byte": instructions.Byte,
            "pushbytes": instructions.PushBytes,
            "method": instructions.Method,
        }[fields[0]](imm[0])

    if fields[0] == "bytecblock":
        imm = _parse_byte_arguments(fields[1:])
        ins = instructions.Bytecblock(imm)

    if fields[0] == "pushbytess":
        imm = _parse_byte_arguments(fields[1:])
        ins = instructions.PushBytess(imm)

    if ins is not None:
        ins.comment = comment
        ins.source_code = source_code_line
        return ins

    line = " ".join(fields)

    f: Callable[[str], Instruction]
    for key, f in parser_rules:
        if line.startswith(key):
            ins = f(line[len(key) :].strip())
            ins.comment = comment
            ins.source_code = source_code_line
            return ins

    # line is checked to not empty at the start of the function.
    print(f'Not found instruction: "{line}"')
    ins = instructions.UnsupportedInstruction(line)
    ins.source_code = source_code_line
    ins.comment = ins.comment
    return ins
