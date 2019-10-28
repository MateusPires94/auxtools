import pymysql
from .tools import fetch_credentials
from sqlalchemy import create_engine


class MySQLAux():

    def __init__(self, database, mode='local'):

        if mode == 'local':

            credentials = fetch_credentials('databases.json')[database]

        else:

            credentials = fetch_credentials(
                'credentials/databases.json', mode=mode)[database]

        self.user = credentials['user']
        self.password = credentials['password']
        self.host = credentials['host']
        self.database = credentials['database']

    def connect(self, charset=None):

        if not charset:

            cnx = pymysql.connect(user=self.user, password=self.password,
                                  host=self.host,
                                  database=self.database)

        else:

            cnx = pymysql.connect(user=self.user, password=self.password,
                                  host=self.host,
                                  database=self.database,
                                  charset=charset)

        return cnx

    def engine(self):

        engine = create_engine("mysql://{}:{}@{}/{}?charset=utf8".format(self.user,
                                                            self.password,
                                                            self.host,
                                                            self.database))
        return engine

    def create_indexes(self,table_name,index_list):
        cnx = self.connect()
        cursor = cnx.cursor()
        for ix in index_list:
            query = '''CREATE INDEX {0}_{1}_index
                        ON {2}.{0} ({1})'''.format(table_name,ix,self.database)
            cursor.execute(query)
        cnx.commit()
        cnx.close()

