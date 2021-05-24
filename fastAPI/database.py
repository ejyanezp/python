import traceback
from sqlalchemy import create_engine, event
from sqlalchemy.pool import Pool
import cx_Oracle
from configuration import OracleDBConfiguration


class OracleDBConnection:
    def __init__(self, env: str, db_name: str):
        cx_Oracle.init_oracle_client(lib_dir=r"C:\\oraclexe\\instantclient_19_11")
        self.db_conf = OracleDBConfiguration(env, db_name)
        self.engine = create_engine(self.db_conf.db_url(), encoding='utf8',
                                    pool_size=self.db_conf.pool_size,
                                    pool_timeout=self.db_conf.connection_timeout)

    @event.listens_for(Pool, "connect")
    def set_call_timeout(self, conn: cx_Oracle.Connection):
        try:
            # Connection.callTimeout is in milliseconds
            conn.callTimeout = self.db_conf.query_timeout
            print(f"Query timeout configured to: {self.db_conf.query_timeout}.")
        except Exception as err:
            traceback.print_exc()
            print(f"Trying to configure query timeout thrown an unknown error: {err}.")

    def get_raw_connection(self):
        return self.engine.raw_connection()
