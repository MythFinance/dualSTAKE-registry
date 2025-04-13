from pyteal import (
    ScratchVar,
    TealType,
    Gtxn,
    Txn,
    Int,
    ImportScratchValue,
    Seq,
    TxnType,
    OnComplete,
    Global,
    MethodSignature,
    App,
    abi,
)
from router import router
from decorators import admin_only
from utils import custom_assert
from str import str_admin_addr
from err import (
    err_chadm_app_arg,
    err_chadm_app_id,
    err_chadm_not_called_by_new_admin,
    err_chadm_oc,
    err_chadm_txn_type,
)


@router.method
@admin_only
def change_admin_1(new_admin: abi.Address):
    """admin method. first of 2-step admin change process."""
    admin = ScratchVar(TealType.bytes, 13)
    return admin.store(new_admin.get())


@router.method
def change_admin_2():
    """public method. second of 2-step admin change process. called by new admin in atomic group after change_admin_1"""
    prev_txn = Gtxn[Txn.group_index() - Int(1)]
    new_admin = ImportScratchValue(0, 13)
    return Seq(
        custom_assert(
            prev_txn.type_enum() == TxnType.ApplicationCall, err_chadm_txn_type
        ),
        custom_assert(prev_txn.on_completion() == OnComplete.NoOp, err_chadm_oc),
        custom_assert(
            prev_txn.application_id() == Global.current_application_id(),
            err_chadm_app_id,
        ),
        custom_assert(
            prev_txn.application_args[0]
            == MethodSignature("change_admin_1(address)void"),
            err_chadm_app_arg,
        ),
        custom_assert(Txn.sender() == new_admin, err_chadm_not_called_by_new_admin),
        App.globalPut(str_admin_addr, new_admin),
    )
