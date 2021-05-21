# from pydantic import BaseModel
from datetime import datetime
# from typing import List


class CcbRequestFixedFields:
    format: str
    company: int
    country: int
    source: str


class CcbResponseFixedFields:
    code: int
    message: str


class TransactionRequest(CcbRequestFixedFields):
    accountId: int
    dateFrom: datetime
    dateTo: datetime
    traceId: str
    itemsPerPage: int
    pageNumber: int


# El BaseModel agrega un constructor "AllArgs"
class CashTransactions:
    tmoCodUsr: int
    tmoCodTra: int
    tmoTipoTra: str
    tmoSucCue: int
    tmoNumCue: int
    tmoTerminal: str
    tmoFecha: datetime
    empId: str
    empNombre: str


class TransactionResponse(CcbResponseFixedFields):
    totalPages: int
    totalRecords: int
#    cashTransactions: List[CashTransactions]
