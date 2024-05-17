import sqlite3
from datetime import datetime

from trivago_tool import TaConfig


class TaDB:
    _instance = None
    db_path = ""
    tables = None
    SQL_TYPE_CREATE = "create"
    SQL_TYPE_UPDATE = "update"
    SQL_TYPE_DELETE = "delete"
    SQL_TYPE_INSERT = "insert"
    SQL_TYPE_SEARCH = "search"
    SQL_TYPE_UPDATE_SEARCH_KEY = "update_search_key"

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaDB, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        _config = TaConfig().config

        self.db_path = _config["db"]["path"]
        self.tables = _config["db"]["tables"]
        
        db = TaDB()
        sql = db.tables["city"][db.SQL_TYPE_CREATE]
        db.to_do(db.SQL_TYPE_CREATE, sql)

    def to_do(self, sql_type, sql: str, _data=None):
        # Create a new SQLite database named 'trivago.db'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if sql_type == self.SQL_TYPE_CREATE:
            cursor.execute(sql)
        elif sql_type == self.SQL_TYPE_DELETE:
            cursor.execute(sql, _data)
        elif sql_type == self.SQL_TYPE_UPDATE_SEARCH_KEY:
            cursor.execute(sql, _data)
        elif sql_type == self.SQL_TYPE_UPDATE:
            cursor.execute(sql, _data)
        elif sql_type == self.SQL_TYPE_INSERT:
            cursor.execute(sql, _data)
        elif sql_type == self.SQL_TYPE_SEARCH:
            cursor.execute(sql, _data)
            rows = cursor.fetchall()

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

        if sql_type == self.SQL_TYPE_SEARCH:
            return rows


def test():

    db = TaDB()
    addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 准备要插入的数据
    searchkey = "tokyo"
    # cityname = "1"
    # country = "1"
    # code = "1"

    # sql = db.tables["city"][db.SQL_TYPE_INSERT]
    # db.to_do(db.SQL_TYPE_INSERT, sql, (searchkey, cityname, country, code, addtime))
    # cityname = "tokyo"
    # country = "japan"
    # code = "200-71462"
    # sql = db.tables["city"][db.SQL_TYPE_UPDATE]
    # db.to_do(db.SQL_TYPE_UPDATE, sql, (cityname, country, code, addtime, searchkey))

    # sql = db.tables["city"][db.SQL_TYPE_DELETE]
    # db.to_do(db.SQL_TYPE_DELETE, sql, (searchkey,))

    sql = db.tables["city"][db.SQL_TYPE_SEARCH]
    rows= db.to_do(db.SQL_TYPE_SEARCH, sql, (searchkey,))
    for row in rows:
        print(f"City Name: {row[0]}, Country: {row[1]}, Code: {row[2]}")
