from pyteal import *
from router import router
from str import *
from admin import *
from decorators import admin_only
from utils import custom_assert, box_exists, vroom


@router.method
@admin_only
def assign_contract():
    """
    Register dualstake contract with registry
    """
    app = Txn.applications[1]
    ds_asa_id = App.globalGetEx(app, str_asa_id)
    ds_lst_id = App.globalGetEx(app, str_lst_id)
    return Seq(
        ds_asa_id,
        ds_lst_id,
        custom_assert(ds_asa_id.hasValue(), "ERR ASA"),
        custom_assert(ds_lst_id.hasValue(), "ERR LST"),
        custom_assert(Not(box_exists(ds_asa_id.value())), "ERR EXIST"),
        App.box_put(Concat(Bytes("a"), Itob(app)), Bytes("")),
        App.box_put(
            Itob(ds_asa_id.value()),
            Concat(
                Itob(ds_lst_id.value()),
                Itob(app),
            ),
        ),
    )


@router.method
@admin_only
def unassign_contract(key: abi.DynamicBytes):
    """
    Delete dualstake contract registration
    """
    return Seq(
        custom_assert(box_exists(Btoi(key.get())), "ERR EXIST"),
        custom_assert(
            App.box_delete(
                Concat(Bytes("a"), App.box_extract(key.get(), Int(8), Int(8)))
            ),
            "ERR DELA",
        ),
        custom_assert(App.box_delete(key.get()), "ERR DEL"),
    )


@router.method
@admin_only
def withdraw_algo(amount: abi.Uint64):
    """
    Withdraw available algo from the contract escrow
    """
    return InnerTxnBuilder.Execute(
        {
            TxnField.type_enum: TxnType.Payment,
            TxnField.sender: Global.current_application_address(),
            TxnField.receiver: Txn.sender(),
            TxnField.amount: amount.get(),
            TxnField.fee: Global.min_txn_fee(),
        }
    )


@router.method
@admin_only
def vanity_configure(
    app_id: abi.Uint64,
    lst_asa_name: abi.DynamicBytes,
    lst_unit_name: abi.DynamicBytes,
    lst_url: abi.DynamicBytes,
):
    """
    Call dualSTAKE.configure2 to mint dualSTAKE token with ASA ID % 1000 === 0
    """
    tc = ScratchVar(TealType.uint64)
    target = ScratchVar(TealType.uint64)
    return Seq(
        InnerTxnBuilder.Execute(
            {
                TxnField.type_enum: TxnType.ApplicationCall,
                TxnField.on_completion: OnComplete.DeleteApplication,
                TxnField.approval_program: Bytes("base64", "C4EBQw=="),
                TxnField.clear_state_program: Bytes("base64", "C4EBQw=="),
            }
        ),
        tc.store(InnerTxn.created_application_id() + Int(1)),
        target.store(tc.load() + Int(1000) - (tc.load() % Int(1000))),
        If(target.load() - tc.load() < Int(2))
        .Then(
            vroom(Int(213)),
            Return(),
        )
        .ElseIf(target.load() - tc.load() > Int(250))
        .Then(vroom(Int(213)), Return())
        .Else(
            vroom(target.load() - tc.load() - Int(2)),
        ),
        InnerTxnBuilder.ExecuteMethodCall(
            app_id=app_id.get(),
            method_signature="configure2(byte[],byte[],byte[])void",
            args=[
                lst_asa_name,
                lst_unit_name,
                lst_url,
            ],
            extra_fields={
                TxnField.fee: Global.min_txn_fee(),
            },
        ),
    )


@router.method
def log_dualstake_listings(app_ids: abi.DynamicArray[abi.Uint64]):
    """
    abi_call dualstakes, log their ContractListing
    """
    i = ScratchVar(TealType.uint64)
    app_id = abi.Uint64()
    logline = ScratchVar(TealType.bytes)
    return For(
        i.store(Int(0)), i.load() < app_ids.length(), i.store(i.load() + Int(1))
    ).Do(
        app_ids[i.load()].store_into(app_id),
        InnerTxnBuilder.ExecuteMethodCall(
            app_id=app_id.get(),
            args=[],
            method_signature="get_contract_listing()(uint64,uint64,uint64,uint64,uint64,string,uint64,string,string,uint16,bool,bool,bool,bool,uint64)",
        ),
        logline.store(InnerTxn.last_log()),
        Log(Extract(logline.load(), Int(4), Len(logline.load()) - Int(4))),
    )


@router.method
def get_asa_dualstake_asset_id(asa_id: abi.Uint64, *, output: abi.Uint64):
    """
    C2C friendly call to get dualstake ASA ID from ASA ID. e.g. COOP -> coopALGO asa ID
    """
    asa = Itob(asa_id.get())
    return Seq(
        If(box_exists(asa))
        .Then(
            output.set(Btoi(App.box_extract(asa, Int(0), Int(8)))),
        )
        .Else(
            output.set(Int(0)),
        )
    )


@router.method
def get_asa_dualstake_app_id(asa_id: abi.Uint64, *, output: abi.Uint64):
    """
    C2C friendly call to get dualstake application ID from ASA ID. e.g. COOP -> coopALGO contract app ID
    """
    asa = Itob(asa_id.get())
    return Seq(
        If(box_exists(asa))
        .Then(
            output.set(Btoi(App.box_extract(asa, Int(8), Int(8)))),
        )
        .Else(
            output.set(Int(0)),
        )
    )


def get_contracts():
    return router.compile_program(version=11)
