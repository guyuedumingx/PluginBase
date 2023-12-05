from app.plug import *
import socket
import json
from uvicorn.config import Config
from uvicorn.main import Server
import asyncio

@PlugManager.register('键值对数据库')
class KeyValueDatabase(UIPlugin):
    """
    全局内置数据库的查询
    """
    ICON = ft.icons.DATA_OBJECT

    def process(self, data, search_feild: ft.TextField, container, db, **kwargs):
        self.search_feild = search_feild
        self.container = container
        self.db = db
        search_feild.hint_text = "Enter a table name to fine data"
        search_feild.on_change = self.search_handler
        tableNameArea = ft.TextField(hint_text="Choose a table to save")
        keyArea = ft.TextField(
            hint_text="Enter key to save", multiline=True, expand=1)
        valueArea = ft.TextField(
            hint_text="Enter value to save", multiline=True, expand=1)
        return ft.Container(ft.ListView([
            tableNameArea,
            keyArea,
            valueArea,
            ft.OutlinedButton(
                text="Save",
                height=45,
                on_click=lambda _: db.get_table(tableNameArea.value, primary_id="key").insert(dict(key=keyArea.value, value=valueArea.value))),
            ft.Text(
                """If your want to save json value like : {key: 'key', value: 'value'}, paste you json value into value feild and click the button below to save"""),
            ft.OutlinedButton(
                text="Json Save",
                height=45,
                on_click=lambda _: db[tableNameArea.value].insert(json.loads(valueArea.value))),
        ], expand=1, spacing=10), alignment=ft.alignment.top_left, expand=1)

    def search_handler(self, e):
        key_word = self.search_feild.value
        if (key_word == ''):
            return
        table = self.db[key_word]
        data = {item['key']: item['value'] for item in table.all()}
        self.container.content = PlugManager.run(
            plugins=("_dictUI",), data=data, mode="edit")
        self.container.update()

@PlugManager.register('_server')
class FastApiServer(Plugin):
    def __init__(self):
        self.is_running = True

    def process(self, data, container, page, port=36909, **kwargs):
        self.host = "0.0.0.0"
        self.port = port
        self.container = container 
        self.page = page
        self.container.content = self.ui()
        self.container.update()
        if hasattr(self, "server"):
            if(self.is_running):
                PlugManager.run(plugins=("_notice",), data="Server has running...", page=page)
        else:
            config = Config(app, host=self.host, port=port, loop="asyncio")
            self.server = Server(config)
            self.is_running = True
            asyncio.run(self.start_server())
        return self.ui()
    
    def ui(self):
        return ft.Container(ft.ListView(controls=[
            ft.Text(f"Server run on: {self.get_local_ip()}: {self.port}"),
            ft.Switch(label="Trun on server",
                      label_position=ft.LabelPosition.LEFT,
                      value=self.is_running,
                      on_change=self.on_change
                      )
        ], spacing=10), height=80, width=300, alignment=ft.alignment.center)

    def on_change(self, e):
        if e.data == "true": 
            self.is_running = True
            asyncio.run(self.start_server())
        else: 
            self.is_running = False
            asyncio.run(self.stop_server())

    def get_local_ip(self):
        try:
            # 获取本机主机名
            host_name = socket.gethostname()
            # 通过主机名获取本机 IP 地址列表
            ip_list = socket.gethostbyname_ex(host_name)[2]
            # 从 IP 地址列表中选择非回环地址（127.0.0.1）的地址
            local_ip = next((ip for ip in ip_list if not ip.startswith("127.")), None)
            return local_ip
        except Exception as e:
            PlugManager.run(plugins=("_notice",), data=f"Error: {e}", page=self.page)

    async def start_server(self):
        await self.server.serve()

    async def stop_server(self):
        await self.server.shutdown()