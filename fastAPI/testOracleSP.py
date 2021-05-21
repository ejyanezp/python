import dbmodels
import database

db_connection = database.OracleDBConnection('dev', 'local')
db_session = db_connection.get_session()
raw_connection = db_connection.get_connection()

try:
    cursor = raw_connection.cursor()
    request = dbmodels.TransactionRequest()
    request.format = "JSON"
    request.company = 1
    request.source = "N5"
    request.country = 1
    request.accountId = 1
    request.dateFrom = "2021-05-01"
    request.dateTo = "2021-05-31"
    request.traceId = "ey"
    request.itemsPerPage = 10
    request.pageNumber = 1

    response = dbmodels.TransactionResponse()
    cursor.callproc("TRAINING_PACKAGE.GET_CASH_TRANSACTIONS", [*request.__dict__], [*response.__dict__])
    results = list(cursor.fetchall())
    cursor.close()
finally:
    raw_connection.close()

