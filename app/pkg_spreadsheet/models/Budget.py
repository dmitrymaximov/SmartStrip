from pydantic import BaseModel
from enum import StrEnum
from datetime import date as dt


class BudgetTypes(StrEnum):
    FOOD = "food"
    TAXI = "taxi"
    CAT = "cat"


class BudgetTitles(StrEnum):
    DATE = "date"
    TYPE = "type"
    COUNT = "count"


class BudgetRecord(BaseModel):
    date: dt = dt.today()
    type: BudgetTypes
    count: int
