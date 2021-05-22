from sqlalchemy import create_engine, event
from sqlalchemy.pool import Pool
import cx_Oracle
import datetime
import base64


def declare_parameters(request_map) -> str:
    key_list = list(request_map.keys())
    sql_params = ':' + key_list[0]
    for key in key_list[1:]:  # Remove last element through python's array slicing
        sql_params += ', :' + key
    return sql_params


@event.listens_for(Pool, "connect")
def set_call_timeout(self, conn: cx_Oracle.Connection):
    try:
        # Connection.callTimeout is in milliseconds
        conn.callTimeout = 20000
        print(f"Query timeout configured to: 20000 milisecs.")
    except Exception as err:
        print(f"Trying to configure query timeout thrown an unknown error: {err}.")


cx_Oracle.init_oracle_client(lib_dir=r"C:\oraclexe\instantclient_19_11")
engine = create_engine("oracle+cx_oracle://OPENLEGACY:OPENLEGACY@OPENLEGACY:1521/xe",
                       encoding='utf8', pool_size=5, pool_timeout=30)
# SQL binding by name
with engine.connect() as conn:
    my_id = 4
    result = conn.execute("select id, nombre, email from cliente where id<:id", my_id)
    for row in result:
        print(row)

# PL/SQL call with positional binding using a tuple
my_conn = engine.raw_connection()
print(f"VERSION: {my_conn.version}")
with my_conn.cursor() as cursor:
    total_pages = cursor.var(int)
    total_records = cursor.var(int)
    response_code = cursor.var(int)
    message = cursor.var(str)
    cursor.callproc("TRAINING_PACKAGE.GET_CASH_TRANSACTIONS",
                    ('JSON', 1, "N5", 1, 1, datetime.datetime(2021, 5, 1), datetime.datetime(2021, 5, 30),
                     'ey', 10, 1, total_pages, total_records, response_code, message))
    print(f"1.- {total_pages.getvalue()}, \n{total_records.getvalue()}, "
          f"\n{response_code.getvalue()}, \n{message.getvalue()}")

# PL/SQL call with named binding using a dictionary
with my_conn.cursor() as cursor:
    request = {'P_FORMAT': 'JSON', 'P_COMPANY': 1, 'P_SOURCE': 'N5', 'P_COUNTRY': 1,
               'P_ACCOUNT_ID': 123, 'P_DATE_FROM': datetime.datetime(2021, 5, 1),
               'P_DATE_TO': datetime.datetime(2021, 5, 30), 'P_TRACE_ID': 'ey', 'P_ITEMS_PER_PAGE': 10,
               'P_PAGE_NUMBER': 1, 'P_TOTAL_PAGES': cursor.var(int), 'P_TOTAL_RECORDS': cursor.var(int),
               'P_RESPONSE_CODE': cursor.var(int), 'P_MESSAGE': cursor.var(str)}
    pl_sql = f"begin TRAINING_PACKAGE.GET_CASH_TRANSACTIONS({declare_parameters(request)}); end;"
    cursor.execute(pl_sql, request)
    print(f"2.- {request['P_TOTAL_PAGES'].getvalue()}, \n{request['P_TOTAL_RECORDS'].getvalue()}, "
          f"\n{request['P_RESPONSE_CODE'].getvalue()}, \n{request['P_MESSAGE'].getvalue()}")

# Getting BLOBs from the DB
with my_conn.cursor() as cursor:
    request2 = {'P_ID': 1, 'P_BLOB_OUT': cursor.var(cx_Oracle.DB_TYPE_BLOB)}
    pl_sql2 = f"begin TRAINING_PACKAGE.BLOB_TEST({declare_parameters(request2)}); end;"
    cursor.execute(pl_sql2, request2)
    my_blob: cx_Oracle.LOB = request2['P_BLOB_OUT'].getvalue()
    my_byte_array = my_blob.read()
    my_b64_encode = base64.b64encode(my_byte_array)
    print(my_b64_encode)

# Getting CLOBs from the DB
with my_conn.cursor() as cursor:
    request3 = {'P_ID': 1, 'P_CLOB_OUT': cursor.var(cx_Oracle.DB_TYPE_CLOB)}
    pl_sql3 = f"begin TRAINING_PACKAGE.CLOB_TEST({declare_parameters(request3)}); end;"
    cursor.execute(pl_sql3, request3)
    my_clob: cx_Oracle.LOB = request3['P_CLOB_OUT'].getvalue()
    my_text = my_clob.read()
    print(my_text)


# PL/SQL binding complex structures
class CashTransactions(object):
    def __init__(self):
        self.tmoCodUsr: int = 1
        self.tmoCodTra: int = 1
        self.tmoTipoTra: str = 'C'
        self.tmoSucCue: int = 1
        self.tmoNumCue: int = 1
        self.tmoTerminal: str = '123'
        self.tmoFecha: datetime = datetime.datetime(2021, 5, 30)
        self.empId: str = '1'
        self.empNombre: str = 'eyanez'


with my_conn.cursor() as cursor:
    collectionType = my_conn.gettype("ott_cashTransactionsList")
    request4 = {'P_FORMAT': 'JSON', 'P_COMPANY': 1, 'P_SOURCE': 'N5', 'P_COUNTRY': 1,
                'P_ACCOUNT_ID': 123, 'P_DATE_FROM': datetime.datetime(2021, 5, 1),
                'P_DATE_TO': datetime.datetime(2021, 5, 30), 'P_TRACE_ID': 'ey', 'P_ITEMS_PER_PAGE': 10,
                'P_PAGE_NUMBER': 1, 'P_TOTAL_PAGES': cursor.var(int), 'P_TOTAL_RECORDS': cursor.var(int),
                'P_RESPONSE_CODE': cursor.var(int), 'P_MESSAGE': cursor.var(str),
                'PTT_CASHTRANSACTIONS': cursor.var(collectionType)}
    pl_sql4 = f"begin TRAINING_PACKAGE.PRO_GET_CASH_TRANSACTIONS({declare_parameters(request4)}); end;"
    cursor.execute(pl_sql4, request4)
    print(f"3.- {request4['P_TOTAL_PAGES'].getvalue()}, \n{request4['P_TOTAL_RECORDS'].getvalue()}, "
          f"\n{request4['P_RESPONSE_CODE'].getvalue()}, \n{request4['P_MESSAGE'].getvalue()}")
    my_collection = request4['PTT_CASHTRANSACTIONS'].getvalue().aslist()
    print(f"PTT_CASHTRANSACTIONS length: {len(my_collection)}")
    # Fetch data using reflection (using the metadata from the DB):
    response = []
    for elem in my_collection:
        my_dict = dict()
        for the_attrib in elem.type.attributes:
            my_dict[the_attrib.name] = getattr(elem, the_attrib.name)
        response.append(my_dict)
    print(response)

