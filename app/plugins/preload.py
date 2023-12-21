from app.plug import *
from sqlalchemy import create_engine
import cx_Oracle


@Plug.register("_on_load_index_success")
class OnLoadIndexSuccess(Plugin):
    def process(self, data, **kwargs):
        # username = "voting"
        # hostname = "111.230.198.42"
        # password = "123456"
        # port = 1521
        # db_name = "VOTING"
        # oracle_connection_string = f'oracle://{username}:{password}@{hostname}:{port}/{db_name}'
        # engine = create_engine(oracle_connection_string)
        # # 使用 dataset
        # print(engine.url)
        # db = dataset.connect(oracle_connection_string)
        # Plug.set_state(db=db)
        # connection = cx_Oracle.connect(f"{username}/{password}@{hostname}:{port}")
        # cursor = connection.cursor()
        # cursor.execute("select * from vote;")
        # for row in cursor.fetchall():
        #     print(row)
        return super().process(data, **kwargs)