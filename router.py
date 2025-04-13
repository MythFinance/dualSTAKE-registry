from pyteal import *
from str import *
from decorators import assert_admin


def create_storage():
    return App.globalPut(str_admin_addr, Txn.sender())


# Main router class
router = Router(
    # Name of the contract
    "Registry Contract",
    # What to do for each on-complete type when no arguments are passed (bare call)
    BareCallActions(
        no_op=OnCompleteAction.create_only(create_storage()),
        update_application=OnCompleteAction.call_only(assert_admin()),
        delete_application=OnCompleteAction.call_only(assert_admin()),
        opt_in=OnCompleteAction.always(Reject()),
        close_out=OnCompleteAction.always(Reject()),
    ),
    clear_state=Approve(),
)
