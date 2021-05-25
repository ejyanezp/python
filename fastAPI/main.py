from fastapi import FastAPI, Depends
import cx_Oracle
import database
# only for debugging
import uvicorn
import models

# Parameters: environment=dev, DB=local
ora_db_conn = database.OracleDBConnection('dev', 'local')
app = FastAPI()


# Dependency
def get_raw_connection():
    raw_conn = ora_db_conn.get_raw_connection()
    try:
        yield raw_conn
    finally:
        raw_conn.close()


@app.post("/mock-cash-transactions")
async def mock_cash_transactions(request: models.TransactionRequest):
    print(request)

    cash_transactions_local = {
        'tmoCodUsr': 12345,
        'tmoCodTra': 1,
        'tmoTipoTra': 'C',
        'tmoSucCue': 1,
        'tmoNumCue': 12345,
        'tmoTerminal': "xyz",
        'tmoFecha': "2021-05-11 00:00",
        'empId': "abcd1234",
        'empNombre': "Jose Pérez"
    }

    response = {
        'code': 200,
        'message': 'Información recuperada exitosamente',
        'totalPages': 10,
        'totalRecords': 100,
        'cashTransactions': [cash_transactions_local]
    }

    return response


def declare_parameters(request_map) -> str:
    key_list = list(request_map.keys())
    sql_params = ':' + key_list[0]
    for key in key_list[1:]:  # Remove last element through python's array slicing
        sql_params += ', :' + key
    return sql_params


@app.post("/cash-transactions-sp")
async def cash_transactions_sp(request: models.TransactionRequest, my_conn: cx_Oracle.Connection = Depends(get_raw_connection)):
    print(request)
    with my_conn.cursor() as cursor:
        collection_type = my_conn.gettype("ott_cashTransactionsList")
        request4 = {'P_FORMAT': request.format,
                    'P_COMPANY': request.company,
                    'P_SOURCE': request.source,
                    'P_COUNTRY': request.country,
                    'P_ACCOUNT_ID': request.accountId,
                    'P_DATE_FROM': request.dateFrom,
                    'P_DATE_TO': request.dateTo,
                    'P_TRACE_ID': "eyanez",
                    'P_ITEMS_PER_PAGE': request.itemsPerPage,
                    'P_PAGE_NUMBER': request.pageNumber,
                    'P_TOTAL_PAGES': cursor.var(int), 'P_TOTAL_RECORDS': cursor.var(int),
                    'P_RESPONSE_CODE': cursor.var(int), 'P_MESSAGE': cursor.var(str),
                    'PTT_CASHTRANSACTIONS': cursor.var(collection_type)}
        pl_sql4 = f"begin TRAINING_PACKAGE.PRO_GET_CASH_TRANSACTIONS({declare_parameters(request4)}); end;"
        cursor.execute(pl_sql4, request4)
        my_collection = request4['PTT_CASHTRANSACTIONS'].getvalue().aslist()
        print(f"PTT_CASHTRANSACTIONS length: {len(my_collection)}")
        # Fetch data using reflection (using the metadata from the DB):
        # No impact for changes in the contract
        response_collection = []
        for elem in my_collection:
            my_dict = dict()
            for the_attrib in elem.type.attributes:
                my_dict[the_attrib.name] = getattr(elem, the_attrib.name)
            response_collection.append(my_dict)
    response = {
        'P_TOTAL_PAGES': request4['P_TOTAL_PAGES'].getvalue(),
        'P_TOTAL_RECORDS': request4['P_TOTAL_RECORDS'].getvalue(),
        'P_RESPONSE_CODE': request4['P_RESPONSE_CODE'].getvalue(),
        'P_MESSAGE': request4['P_MESSAGE'].getvalue(),
        'PTT_CASHTRANSACTIONS': response_collection
    }
    return response


# Only for debugging, for production use the uvicorn command line.
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

