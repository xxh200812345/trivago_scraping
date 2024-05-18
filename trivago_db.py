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
            addtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_data = _data + (addtime,) 
            cursor.execute(sql, new_data)
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

    # 准备要插入的数据
    # searchkey = "tokyo"
    # city_country = "1"
    # code = "1"

    # sql = db.tables["city"][db.SQL_TYPE_INSERT]
    # db.to_do(db.SQL_TYPE_INSERT, sql, (searchkey, city_country, code))
    # city_country = "tokyo-japan"
    # code = "200-71462"
    # sql = db.tables["city"][db.SQL_TYPE_UPDATE]
    # db.to_do(db.SQL_TYPE_UPDATE, sql, (city_country, code, addtime, searchkey))

    # sql = db.tables["city"][db.SQL_TYPE_DELETE]
    # db.to_do(db.SQL_TYPE_DELETE, sql, (searchkey,))

    sql = db.tables["city"][db.SQL_TYPE_UPDATE_SEARCH_KEY]
    db.to_do(db.SQL_TYPE_UPDATE_SEARCH_KEY, sql, ("Tokyo","tokyo"))

# test()