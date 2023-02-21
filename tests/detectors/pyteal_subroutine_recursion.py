# pylint: skip-file
# mypy: ignore-errors
from pyteal import *  # pylint: disable=wildcard-import, unused-wildcard-import
from tealer.detectors.all_detectors import IsUpdatable

# Basic recursion
@Subroutine(TealType.uint64)  # type: ignore[misc]
def factorial(n: Expr) -> Expr:
    # Note: Recursion is not supported if the subroutine takes ScratchVar type argument
    return If(
        n == Int(0),  # condition
        Return(Int(1)),  # then expression
        Return(n * factorial(n - Int(1))),  # else expression
    )


# recursion with multiple subroutines
@Subroutine(TealType.none)
def recursive_1(n: Expr) -> Expr:
    return Seq(
        [
            Pop(Bytes("Recursive 1 Subroutine")),
            If(
                n < Int(5),
                recursive_2(n),
            ),
        ]
    )


@Subroutine(TealType.none)
def recursive_2(n: Expr) -> Expr:
    return Seq([recursive_3(n)])


@Subroutine(TealType.none)
def recursive_3(n: Expr) -> Expr:
    return Seq(
        [
            Pop(Bytes("Recursive 2 Subroutine")),
            recursive_1(n + Int(1)),
            Return(),
        ]
    )


# loop in a subroutine
@Subroutine(TealType.none)
def loop_in_sub() -> Expr:
    i = ScratchVar()
    return Seq(
        [
            Pop(Bytes("Loop in Subroutine")),
            For(i.store(Int(0)), i.load() < Int(10), i.store(i.load() + Int(1)),).Do(
                Log(Itob(i.load())),
            ),
            Return(),
        ]
    )


# loop in a subroutine calling a recursive subroutine
@Subroutine(TealType.none)
def loop_recursive_1(n: Expr) -> Expr:
    i = ScratchVar()
    return Seq(
        [
            Pop(Bytes("Loop Recursive Subroutine")),
            For(i.store(Int(0)), i.load() < Int(2), i.store(i.load() + Int(1)),).Do(
                If(
                    n < Int(3),
                    loop_recursive_2(n),
                    Return(),
                )
            ),
        ]
    )


@Subroutine(TealType.none)
def loop_recursive_2(n: Expr) -> Expr:
    return Seq([loop_recursive_1(n + Int(1)), Return()])


def compile_program(approval_program: Expr) -> str:
    return compileTeal(
        approval_program,
        mode=Mode.Application,
        version=7,
    )


basic_recursion = Seq([Pop(factorial(Int(4))), Approve()])
multiple_recursion = Seq([recursive_1(Int(1)), Approve()])
loop_in_subroutine = Seq([loop_in_sub(), Approve()])
loop_and_recursion = Seq([loop_recursive_1(Int(0)), Approve()])

multiple_calls_to_same_sub = Seq([loop_in_sub(), loop_in_sub(), Approve()])

all_patterns = Seq(
    [
        Pop(factorial(Int(4))),
        recursive_1(Int(1)),
        loop_in_sub(),
        loop_recursive_1(Int(0)),
        loop_in_sub(),
        Approve(),
    ]
)

basic_recursion_teal = compile_program(basic_recursion)

multiple_recursion_teal = compile_program(multiple_recursion)
loop_in_subroutine_teal = compile_program(loop_in_subroutine)
loop_and_recursion_teal = compile_program(loop_and_recursion)

multiple_calls_to_same_sub_teal = compile_program(multiple_calls_to_same_sub)

all_patterns_teal = compile_program(all_patterns)


# Test that detectors are enumerating paths correctly by asserting the detector results.
# None of the programs contain a check for any of the detectors. So, detectors should report
# all valid paths.

# TODO: Having a edge from callsub to the called subroutine was a really bad idea. Change this as soon as
# possible.

basic_recursion_paths = [
    [0, 2, 5, 1],
    # We completely ignore the path using the recursion/loop.
    # May be we should consider one iteration and generate path from that
    # [0,
    # 2, 3, 4,  # Block 4 calls subroutine in Block 2
    # 2, 5
    # 1]
]

multiple_recursion_paths = [
    [0, 2, 5, 1],
    # [0, 2, 3, 6, 8, 2, 5, 1]
]

loop_in_subroutine_paths = [
    [0, 2, 3, 5, 1],
    # [0, 2, 3, 4, 3, 5, 1]
]

loop_and_recursion_paths = [
    [0, 2, 3, 4, 5, 1],
    [0, 2, 3, 9, 1],
    ### [0, 2, 3, 4, 7, 10, 2, .., 11, 8, 6, 3, ...]
    # [0, 2, 3, 4, 7, 10, 2, 3, 9, 1]
    # [0, 2, 3, 4, 7, 10, 2, 3, 4, 5, 1]
    # [0, 2, 3, 4, 7, 10, 2, 3, 9, 11, 8, 6, 3, 9, 1]
    # [0, 2, 3, 4, 7, 10, 2, 3, 4, 5, 11, 8, 6, 3, 9, 1]
    # [0, 2, 3, 4, 7, 10, 2, 3, 9, 11, 8, 6, 3, 4, 5, 1]
    # [0, 2, 3, 4, 7, 10, 2, 3, 4, 5, 11, 8, 6, 3, 4, 5, 1]
]

multiple_calls_to_same_sub_paths = [
    [0, 3, 4, 6, 1, 3, 4, 6, 2],
    # ...
]

all_patterns_paths = [
    [
        0,
        6,
        9,  # factorial
        1,
        10,
        13,  # recursive1_1
        2,
        18,
        19,
        21,  # loop in sub
        3,
        22,
        23,
        24,
        25,  # loop recursive
        4,
        18,
        19,
        21,  # loop in sub
        5,
    ],
    [
        0,
        6,
        9,  # factorial
        1,
        10,
        13,  # recursive1_1
        2,
        18,
        19,
        21,  # loop in sub
        3,
        22,
        23,
        29,  # loop recursive
        4,
        18,
        19,
        21,  # loop in sub
        5,
    ],
]


subroutine_recursion_patterns_tests = [
    (basic_recursion_teal, IsUpdatable, basic_recursion_paths),
    (multiple_recursion_teal, IsUpdatable, multiple_recursion_paths),
    (loop_in_subroutine_teal, IsUpdatable, loop_in_subroutine_paths),
    (loop_and_recursion_teal, IsUpdatable, loop_and_recursion_paths),
    (multiple_calls_to_same_sub_teal, IsUpdatable, multiple_calls_to_same_sub_paths),
    (all_patterns_teal, IsUpdatable, all_patterns_paths),
]

if __name__ == "__main__":
    print(basic_recursion_teal)
    print(multiple_recursion_teal)
    print(loop_in_subroutine_teal)
    print(loop_and_recursion_teal)
    print(multiple_calls_to_same_sub_teal)
    print(all_patterns_teal)
