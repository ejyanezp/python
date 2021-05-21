import yaml


class OracleDBConfiguration:
    def __init__(self, env: str, db_name: str):
        self.db_name = db_name
        with open(f'application-{env}.yml') as config_file:
            self.conf = yaml.load(config_file, Loader=yaml.FullLoader)

    @staticmethod
    def routing_configuration(env: str, country: int, company: int):
        if country == 1 and company == 1:
            db_name = 'PanamaSRV'
        elif country == 1 and company == 1007:
            db_name = 'UnicorpSRV'
        elif country == 1 and company == 8994:
            db_name = 'PlanintSRV'
        return OracleDBConfiguration(env, db_name)

    def db_url(self) -> str:
        return "{0}://{1}:{2}@{3}:{4}/{5}".format(
            self.conf['database'][self.db_name]['driver-className'],
            self.conf['database'][self.db_name]['username'],
            self.conf['database'][self.db_name]['password'],
            self.conf['database'][self.db_name]['host'],
            self.conf['database'][self.db_name]['port'],
            self.conf['database'][self.db_name]['schema']
        )

    @property
    def pool_size(self) -> int:
        return int(self.conf['database'][self.db_name]['pool-max-size'])

    @property
    def connection_timeout(self) -> int:
        return int(self.conf['database'][self.db_name]['connection-timeout'])

    @property
    def query_timeout(self) -> int:
        return int(self.conf['database'][self.db_name]['query-timeout'])
