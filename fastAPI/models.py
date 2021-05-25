from pydantic import BaseModel
from datetime import datetime


class CcbRequestFixedFields(BaseModel):
    format: str
    company: int
    country: int
    source: str


class TransactionRequest(CcbRequestFixedFields):
    accountId: int
    dateFrom: datetime
    dateTo: datetime
    itemsPerPage: int
    pageNumber: int
