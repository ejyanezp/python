import pyodbc
import datetime

server = 'tcp:OPENLEGACY'
database = 'ol'
username = 'sa'
password = 'qwer1234'
conn_timeout = 20  # 20 seconds
query_timeout = 10  # 10 seconds
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password, timeout=conn_timeout)
conn.timeout = query_timeout

# First Test
with conn.cursor() as cursor:
    cursor.execute("SELECT @@version;")
    row = cursor.fetchone()
    while row:
        print(row[0])
        row = cursor.fetchone()

# First Select
with conn.cursor() as cursor:
    cursor.execute("select config_name from [ol].[dbo].[application_entity]")
    row = cursor.fetchone()
    while row:
        print(row[0])
        row = cursor.fetchone()

# First Stored procedure - several output resultsets
# Using a tuple for the input parameters
database = 'training'
username = 'sa'
password = 'qwer1234'
conn_timeout = 20  # 20 seconds
query_timeout = 10  # 10 seconds
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password, timeout=conn_timeout)
conn.timeout = query_timeout
sql = """
DECLARE @out nvarchar(max);
EXEC [dbo].[test_for_pyodbc] @Param_in = ?, @Param_out = @out OUTPUT;
SELECT @out as the_output;
"""
with conn.cursor() as cursor:
    params = ("Eduardo", )
    cursor.execute(sql, params)
    # Fetch first resultset
    rows = cursor.fetchall()
    while rows:
        print(rows)
        # Fetch next resultset
        if cursor.nextset():
            rows = cursor.fetchall()
        else:
            rows = None

# Second Stored Procedure
sql = """
DECLARE
    @return_value int,
    @p_response_code varchar(40),
    @p_message varchar(40)
EXEC @return_value = [dbo].[get_creditcard_data]
    @p_format = ?,
    @p_company = ?,
    @p_source = ?,
    @p_country = ?,
    @p_query_date = ?,
    @p_year_month = ?,
    @p_account_id = ?,
    @p_credit_card = ?,
    @p_traceId = ?,
    @p_response_code = @p_response_code OUTPUT,
    @p_message = @p_message OUTPUT

SELECT @p_response_code as N'@p_response_code', 
    @p_message as N'@p_message'

-- SELECT 'Return Value' = @return_value
"""
with conn.cursor() as cursor:
    params = ('json', 1, 'n5', 1, datetime.datetime(2021, 5, 24), '2021-05', '654321', '123456', 'ey')
    cursor.execute(sql, params)
    # Fetch first resultset
    raw_resultset = cursor.fetchall()
    resultset_dict = dict()
    resultset_counter = 0
    while raw_resultset:
        record_counter = 0
        records = []
        for row in raw_resultset:
            columns_dict = dict()
            columns_counter = 0
            for elem in row:
                columns_dict[row.cursor_description[columns_counter][0]] = elem
                columns_counter += 1
            records.append(columns_dict)
            record_counter += 1
        resultset_dict[f"resultset{resultset_counter}"] = records
        resultset_counter += 1
        # Fetch next resultset
        if cursor.nextset():
            raw_resultset = cursor.fetchall()
        else:
            raw_resultset = None
    print(resultset_dict)
