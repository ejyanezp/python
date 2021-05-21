from typing import List
from fastapi import FastAPI, HTTPException, Depends
from dbmodels import TransactionRequest, TransactionResponse, CashTransactions, Client, Base
from sqlalchemy.orm import Session
import database
import crud

ora_db_session = database.OracleDBConnection('dev', 'local')
app = FastAPI()


# Dependency
def get_db():
    db = database.get_db_session('dev', 'local')
    try:
        yield db
    finally:
        db.close()


@app.post("/mock-cash-transactions", response_model=TransactionResponse)
async def mock_cash_transactions(request: TransactionRequest) -> TransactionResponse:
    print(request)

    cash_transactions_local = CashTransactions(
        tmoCodUsr=12345,
        tmoCodTra=1,
        tmoTipoTra="C",
        tmoSucCue=1,
        tmoNumCue=12345,
        tmoTerminal="xyz",
        tmoFecha="2021-05-11 00:00",
        empId="abcd1234",
        empNombre="Jose Pérez"
    )

    response = TransactionResponse(
        code=200,
        message='Información recuperada exitosamente',
        totalPages=10,
        totalRecords=100,
        cashTransactions=[cash_transactions_local]
    )

    return response


@app.get("/clients/{client_id}", response_model=Client)
async def get_client_by_id(client_id: int, db: Session = Depends(get_db)) -> Client:
    client = crud.get_client(db, client_id)
    if client is None:
        raise HTTPException(status_code=404, detail="Client  not found")
    return client


@app.get("/clients/", response_model=List[Client])
async def get_clients(db: Session = Depends(get_db)) -> List[Client]:
    clients = crud.get_all_clients(db)
    print("ejecución get clients")
    if clients is None:
        raise HTTPException(status_code=404, detail="The are no clients")
    return clients


@app.post("/cash-transactions-sp", response_model=TransactionResponse)
async def cash_transactions_sp(request: TransactionRequest, db: Session = Depends(get_db)) -> TransactionResponse:
    print(request)
    cursor = get_connection().cursor()
    response = TransactionResponse(
        code=200,
        message='Información recuperada exitosamente',
        totalPages=10,
        totalRecords=100,
        cashTransactions=[]
    )
    args = (request.format,       request.company,     request.source,      request.country,
            request.accountId,    request.dateFrom,    request.dateTo,      request.traceId,
            request.itemsPerPage, request.pageNumber,  response.totalPages, response.totalRecords,
            response.code,        response.message,    response.cashTransactions)
    cursor.callproc("TRAINING_PACKAGE.PRO_GET_CASH_TRANSACTIONS", args)
    results = list(cursor.fetchall())
    print(results)
    cursor.close()

    return None
