import pymysql
from config.mysql import host, port, username, password, database


class Transaction(object):
    def __init__(self, sql):
        self.sql = sql

    def start(self, level='REPEATABLE READ'):
        self.sql.query("SET AUTOCOMMIT=FALSE")
        self.sql.query(f"SET SESSION TRANSACTION ISOLATION LEVEL {level}")
        self.sql.query("SET innodb_lock_wait_timeout = 10")
        self.sql.query("START TRANSACTION")

    def commit(self):
        self.sql.query("COMMIT")
        self.sql.query("SET AUTOCOMMIT=TRUE")

    def rollback(self):
        self.sql.query("ROLLBACK")
        self.sql.query("SET AUTOCOMMIT=TRUE")


class MySQL(object):
    def __init__(self, dict_cursor=False):
        try:
            self.__connInfo = pymysql.connect(host=host, port=port, user=username,
                                              password=password, db=database, charset='utf8')
        except Exception as e:
            self.__cursor = None
            raise e
        else:
            if dict_cursor:
                self.__cursor = self.__connInfo.cursor(pymysql.cursors.DictCursor)
            else:
                self.__cursor = self.__connInfo.cursor()
            self.query("SET AUTOCOMMIT=TRUE")
            self.query("SET TIME_ZONE='+09:00'")
            return

    def __del__(self):
        try:
            self.__connInfo.close()
        except:
            return False
        else:
            return True

    def query(self, query_string, *args):
        if query_string is None:
            return None
        if self.__cursor is None:
            return None
        self.__cursor.execute(query_string, *args)
        return self.__cursor.fetchall()

    def escape(self, string):
        return self.__connInfo.escape(string)

    @property
    def transaction(self):
        return Transaction(self)


__all__ = ['MySQL']
