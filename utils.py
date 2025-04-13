from pyteal import (
    App,
    Assert,
    Bytes,
    For,
    If,
    InnerTxnBuilder,
    Int,
    Itob,
    Not,
    OnComplete,
    ScratchVar,
    Seq,
    Subroutine,
    TealType,
    TxnField,
    TxnType,
)


# assert that fails with an error string attached
def custom_assert(cond, str):
    """assert with custom error message"""
    return If(Not(cond)).Then(Assert(Bytes("") == Bytes(str)))


@Subroutine(TealType.uint64)
def box_exists(key_uint64):
    return Seq(box := App.box_length(Itob(key_uint64)), box.hasValue())


@Subroutine(TealType.none)
def vroom(num):
    """
    Forward txn counter
    """
    i = ScratchVar(TealType.uint64)
    return For(i.store(Int(0)), i.load() < num, i.store(i.load() + Int(1))).Do(
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.on_completion: OnComplete.DeleteApplication,
                TxnField.approval_program: Bytes("base64", "C4EBQw=="),
                TxnField.clear_state_program: Bytes("base64", "C4EBQw=="),
            }
        )
    )
