import traceback
from sqlalchemy import create_engine, event
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker
from cx_Oracle import Connection
from configuration import OracleDBConfiguration


class OracleDBConnection:
    def __init__(self, env: str, db_name: str):
        self.db_conf = OracleDBConfiguration(env, db_name)
        self.engine = create_engine(self.db_conf.db_url(), encoding='utf8',
                                    pool_size=self.db_conf.pool_size,
                                    pool_timeout=self.db_conf.connection_timeout)
        print(self.engine.dialect.name)
        print(self.engine.dialect.driver)

    def get_session(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @event.listens_for(Pool, "connect")
    def set_call_timeout(self, conn: Connection):
        try:
            # Connection.callTimeout is in milliseconds
            conn.callTimeout = self.db_conf.query_timeout
            print(f"Query timeout configured to: {self.db_conf.query_timeout}.")
        except Exception as err:
            traceback.print_exc()
            print(f"Trying to configure query timeout thrown an unknown error: {err}.")

    def get_connection(self):
        return self.engine.raw_connection()
