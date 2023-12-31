from app.plug import *
import socket
import flet as ft
from fastapi import HTTPException
from fastapi.responses import FileResponse
import zipfile
import json
import asyncio
from pydantic import BaseModel
from uvicorn.config import Config
import socket
from uvicorn.main import Server

ONLINE_USERS = {}

class Item(BaseModel):
    ehr: str
    ip: str

@Plug.register('服务器')
class PluginMarketServer(UIPlugin):
    """
    服务器端，向外提供插件
    """
    ICON = ft.icons.LANGUAGE
    def __init__(self):
        self.is_running = True

    def process(self, data, container, page, db, process_bar, **kwargs):
        self.db = db
        self.host = "0.0.0.0"
        self.port = 36909
        self.container = container 
        self.page = page
        process_bar.visible = False
        self.container.content = self.ui()
        self.container.update()
        if hasattr(self, "server"):
            if(self.is_running):
                Plug.run(plugins=("_notice",), data="Server is running...", page=page)
        else:
            config = Config(app, host=self.host, port=self.port, loop="asyncio", log_config="assets/config/uvicorn_log.json")
            self.server = Server(config)
            self.is_running = True
            asyncio.run(self.start_server())
        return self.ui()

    async def start_server(self):
        await self.server.serve()

    async def stop_server(self):
        await self.server.shutdown()

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
        self.page.update()

    def get_local_ip(self):
        try:
            return Plug.run(plugins=("_get_local_ip",))
        except Exception as e:
            Plug.run(plugins=("_notice",), data=f"Error: {e}", page=self.page)

    async def start_server(self):
        await self.server.serve()

    async def stop_server(self):
        await self.server.shutdown()

    @app.get("/plugins")
    def find_plugin_by_name():
        plugins_dict = Plug.run(plugins=("_search_plugin",), data="")
        res = {}
        for name, plugin in plugins_dict.items():
            res[name] = (dict(
                name=name,
                author=plugin.AUTHOR,
                version=plugin.VERSION,
                desc=plugin.DESC,
                icon=plugin.ICON
            ))
        return res
    
    @app.get("/plugins/s/{name}")
    def find_plugin_by_name(name :str):
        plugins_dict = Plug.run(plugins=("_search_plugin",), data=name, show_no_source=False)
        res = {}
        for name, plugin in plugins_dict.items():
            res[name] = (dict(
                name=name,
                author=plugin.AUTHOR,
                version=plugin.VERSION,
                desc=plugin.DESC,
                icon=plugin.ICON
            ))
        return res

    @app.get("/plugins/d/{name}")
    def download_plugin_by_name(name = ""):
        plugins_dict = Plug.run(plugins=("_search_plugin",), data=name, show_build_in=True)
        for name, plugin in plugins_dict.items():
            try:
                # 使用 FileResponse 类，将文件名添加到 Content-Disposition 头部
                return FileResponse(plugin.SOURCEFILE, headers={"Content-Disposition": f'attachment; filename="{os.path.basename(plugin.SOURCEFILE)}"'})
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail="File not found")
        
    @app.get("/update")
    def update():
        filename = f"assets{os.path.sep}update.zip"
        try:
            # 使用 FileResponse 类，将文件名添加到 Content-Disposition 头部
            return FileResponse(filename, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
        except FileNotFoundError:
            Plug.run(plugins=("构建更新包",))
            try:
                return FileResponse(filename, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
            except:
                raise HTTPException(status_code=404, detail="File not found")
    
    @app.post("/login")
    def login(item: Item):
        ONLINE_USERS.update(vars(item))
        return {"ehr":item.ehr, "msg": "Login Success", "code": 200}
    
    @app.get("/onlines")
    def online_list():
        return ONLINE_USERS
    
    @app.post("/logout/{ehr}")
    def logout(ehr):
        try:
            del ONLINE_USERS[ehr]
            return {"ehr": ehr, "msg": "Logout Success", "code": 200}
        except:
            return {"ehr": ehr, "msg": "Logout Fail", "code": 401}
    


@Plug.register("构建更新包")
class BuildUpdateFile(Plugin):
    """
    构建用于更新的软件包app/plugins/build_in
    """
    ICON=ft.icons.BUILD_CIRCLE_OUTLINED
    def process(self, data, **kwargs):
        # 压缩整个 build_in 目录
        build_in_dir = ENV['update_dir']
        with zipfile.ZipFile(f"assets{os.path.sep}update.zip", "w") as zip_file:
            for foldername, subfolders, filenames in os.walk(build_in_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, build_in_dir)
                    zip_file.write(file_path, arcname)
        return "更新包构建成功!!!"


@Plug.register("构建插件包")
class BuildUpdateFile(Plugin):
    """
    构建插件包app/plugins
    """
    ICON=ft.icons.BUILD_CIRCLE_OUTLINED
    def process(self, data, **kwargs):
        build_in_dir = ENV['plugin_dir']
        with zipfile.ZipFile(f"assets{os.path.sep}plugins.zip", "w") as zip_file:
            for foldername, subfolders, filenames in os.walk(build_in_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, build_in_dir)
                    zip_file.write(file_path, arcname)
        return "插件包构建成功!!!"

