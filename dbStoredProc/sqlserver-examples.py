import pyodbc

server = 'tcp:192.168.2.100'
database = 'ol'
username = 'sa'
password = 'qwer1234'
conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+password)
with conn.cursor() as cursor:
    cursor.execute("SELECT @@version;")
    row = cursor.fetchone()
    while row:
        print(row[0])
        row = cursor.fetchone()

with conn.cursor() as cursor:
    cursor.execute("select config_name from [ol].[dbo].[application_entity]")
    row = cursor.fetchone()
    while row:
        print(row[0])
        row = cursor.fetchone()

