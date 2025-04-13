# Registry contract

A registry for the SDK to fetch available contracts.

All methods are admin-guarded except read-only methods and simulate targets/helpers for frontend.

Contract-to-contract calls also available to fetch an APP ID from ASA, or LST Asset ID from ASA.

Decorators are used for access control.

Entry point is `sc.py`.
