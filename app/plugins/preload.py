from app.plug import *


@Plug.register("_on_load_index_success")
class OnLoadIndexSuccess(Plugin):
    def process(self, data, **kwargs):
        username = "voting"
        hostname = "111.230.198.42"
        password = "123456"
        port = 1521
        sid = "XE"
        oracle_connection_string = f'oracle://{username}:{password}@{hostname}:{port}/{sid}'
        remote_db = dataset.connect(oracle_connection_string)
        Plug.set_state(remote_db=remote_db)
        return super().process(data, **kwargs)