from app.plug import *
import flet as ft
from fastapi import HTTPException
from fastapi.responses import FileResponse
import zipfile


@Plug.register('插件市场服务器')
class PluginMarketServer(UIPlugin):
    """
    插件市场的服务器端，向外提供插件
    """
    ICON = ft.icons.LANGUAGE
    def process(self, data, db, **kwargs):
        self.db = db
        return Plug.run(plugins=("_server",), port=36909, **kwargs)

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
        plugins_dict = Plug.run(plugins=("_search_plugin",), data=name)
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
        try:
            # 使用 FileResponse 类，将文件名添加到 Content-Disposition 头部
            filename = f"assets{os.path.sep}update.zip"
            return FileResponse(filename, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
    