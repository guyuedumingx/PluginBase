from app.plug import *
import flet as ft
import requests
from uvicorn.config import Config
import socket
from uvicorn.main import Server
import asyncio

@Plug.register('_plugin_cards_list')
class BuildShowCards(UIPlugin):
    def process(self, data: list, plugin_onclick: lambda e: e, **kwargs):
        return [ft.ListTile(
                leading=ft.Icon(item[1].ICON),
                title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                subtitle=ft.Text(
                    item[1].DESC.strip().split("\n")[0]
                ),
                on_click=plugin_onclick,
                ) for item in data.items()]


@Plug.register('插件市场')
class PluginMarket(UIPlugin):
    """
    支持插件下载安装
    """
    ICON = ft.icons.EXTENSION_OUTLINED
    def process(self, data, db, page, search_feild, container,
                server_addr=ENV['server_addr'], server_port=ENV['server_port'], **kwargs):
        self.url_prefix = f"http://{server_addr}:{server_port}"
        resp = requests.get(f"{self.url_prefix}/plugins")
        self.data = resp.json()
        self.page = page
        self.container = container
        search_feild.on_change = self.search_feild_on_change
        return self.main_ui()
        
    def search_feild_on_change(self, e):
        resp = requests.get(f"{self.url_prefix}/plugins/s/{e.data}")
        self.data = resp.json()
        self.container.content = self.main_ui()
        self.container.update()
    
    def main_ui(self):
        return ft.ListView([ft.ListTile(
            leading=ft.Icon(item['icon']),
            title=ft.Text(item['name'], weight=ft.FontWeight.W_700),
            subtitle=ft.Row([
                ft.Text(item['desc'].strip().split("\n")[0]),
                ]),
            on_click=self.plugin_detail_ui
        ) for _, item in self.data.items()],expand=1)

    def plugin_detail_ui(self, e):
        name = e.control.title.value
        plugin = self.data[name]
        back_btn = ft.FloatingActionButton(
            icon=ft.icons.ARROW_BACK,
            scale=0.7,
            opacity=0.5,
            bgcolor=ft.colors.WHITE,
            shape=ft.CircleBorder(),
            on_click=lambda _: self.page.views.pop() and self.page.update()
            )
        top_view = self.page.views[-1]
        url = top_view.route + "/detail"
        ui = [
            ft.Text(name, size=30),
            ft.Markdown(plugin['desc']),
            ft.Markdown(f" ## Author  \n{plugin['author']}"),
            ft.Markdown(f" ## Version  \n{plugin['version']}"),
            ft.OutlinedButton(
                text = "Install this extension",
                height=40,
                on_click=lambda e: self.install_plugin(plugin)
                )
        ]
        self.page.views.append(ft.View(url, [back_btn,ft.ListView(ui, expand=1, spacing=10) ]))
        self.page.go(url)
    
    def install_plugin(self, plugin):
        resp = requests.get(f"{self.url_prefix}/plugins/d/{plugin['name']}")
        if resp.status_code == 200:
            # 获取文件名
            content_disposition = resp.headers.get("Content-Disposition")
            if content_disposition and "filename" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
            else:
                filename = "downloaded_plugin.py"  # 默认文件名
            with open(ENV['plugin_dir']+os.path.sep+filename, "wb") as f:
                f.write(resp.content)
        Plug.run(plugins=("重新加载",))


@Plug.register('_server')
class FastApiServer(Plugin):
    def __init__(self):
        self.is_running = True

    def process(self, data, container, page, port=ENV['server_port'], **kwargs):
        self.host = "0.0.0.0"
        self.port = port
        self.container = container 
        self.page = page
        self.container.content = self.ui()
        self.container.update()
        if hasattr(self, "server"):
            if(self.is_running):
                Plug.run(plugins=("_notice",), data="Server has running...", page=page)
        else:
            config = Config(app, host=self.host, port=port, loop="asyncio", log_config="assets/config/uvicorn_log.json")
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
            Plug.run(plugins=("_notice",), data=f"Error: {e}", page=self.page)

    async def start_server(self):
        await self.server.serve()

    async def stop_server(self):
        await self.server.shutdown()
