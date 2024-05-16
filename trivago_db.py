import sqlite3
from datetime import datetime

from trivago_tool import TaConfig

class TaDB:
    _instance = None
    db_path = ''
    tables = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TaDB, cls).__new__(cls)
            cls._instance.init()
        return cls._instance

    def init(self):
        _config = TaConfig().config

        self.db_path = _config["db"]["path"]
        self.tables = _config["db"]["tables"]

    def create(self, create_table_query):
        _config = TaConfig().config

        self.db_path = _config["db"]["path"]
        # Create a new SQLite database named 'trivago.db'
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Execute the query to create the table
        cursor.execute(create_table_query)

        # Commit the changes and close the connection
        conn.commit()
        conn.close()

    def insert(self, insert_data_query, _data):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 插入数据的 SQL 语句
        insert_data_query = insert_data_query

        # 执行插入数据的查询
        cursor.execute(insert_data_query, _data)
        # 提交更改并关闭连接
        conn.commit()
        conn.close()

    def update(self, update_data_query, _data):
        pass


    def search_by_search_key(self, search_data_query, _data):
        pass
    
def test():
    db = TaDB()

    create_table_query = db.tables["city"]["create"]
    db.create(create_table_query)

    # 准备要插入的数据
    searchkey = 'beijing_trip'
    cityname = 'Beijing'
    country = 'China'
    code = 'BJ'
    addtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    insert_data_query = db.tables["city"]["insert"]
    db.insert(insert_data_query,(searchkey, cityname, country, code, addtime))

test()