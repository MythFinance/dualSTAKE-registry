from pyteal import *
from utils import *
from str import *
from functools import wraps


# avalidate caller is admin
@Subroutine(TealType.none)
def assert_admin():
    """fails if the caller is not the contract admin"""
    return custom_assert(Txn.sender() == App.globalGet(str_admin_addr), "ERR UNAUTH")


def admin_only(fn):
    """Admin method only"""
    @wraps(fn)
    def wrapper(*args, **kwds):
        return Seq(assert_admin(), fn(*args, **kwds))
    return wrapper
