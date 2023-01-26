# pylint: disable=undefined-variable
# type: ignore[name-defined]
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import

barecalls = BareCallActions(
    no_op=OnCompleteAction(action=Approve(), call_config=CallConfig.CREATE),
    opt_in=OnCompleteAction(action=Approve(), call_config=CallConfig.ALL),
    close_out=OnCompleteAction(action=Approve(), call_config=CallConfig.CALL),
    update_application=OnCompleteAction(call_config=CallConfig.NEVER),
    delete_application=OnCompleteAction(call_config=CallConfig.NEVER),
)

router = Router(
    name="ARC4 application parsing test",
    bare_calls=barecalls,
    clear_state=Approve(),
)


@ABIReturnSubroutine
def identity(arg: abi.Uint64, *, output: abi.Uint64) -> Expr:
    return output.set(arg.get())


@router.method(  # type: ignore[misc]
    opt_in=CallConfig.ALL,
    close_out=CallConfig.CALL,
    update_application=CallConfig.NEVER,
    delete_application=CallConfig.NEVER,
)
def hello(name: abi.String, *, output: abi.String) -> Expr:
    return output.set(Concat(Bytes("Hello "), name.get()))


router.add_method_handler(identity, method_config=MethodConfig(no_op=CallConfig.CALL))


arc4_application_ap, _clear_program, _ = router.compile_program(version=6)
