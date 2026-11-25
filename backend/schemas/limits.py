"""
Upper bounds for every number a client can send.

A bound is what rejects infinity and NaN (Pydantic accepts both for a plain
float, and `gt=0` stops neither), and it keeps absurd finite figures — a
1e300 down payment — out of the calculators. One trillion in the market's
own currency is far above any household figure in any of the three markets
(about 25 billion USD in lira, the smallest unit) and far below anything
that overflows. test_every_number_is_bounded.py refuses a new field without
one.
"""
from typing import Annotated

from pydantic import Field

MAX_AMOUNT = 1e12
MAX_ID = 2**31 - 1  # Postgres integer: a larger id is a 500, not a 404

# A portfolio weight is a fraction; the routes check that they sum to 1.
Weight = Annotated[float, Field(ge=0, le=1)]
