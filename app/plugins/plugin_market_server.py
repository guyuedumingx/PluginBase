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
    

@Plug.register("构建更新包")
class BuildUpdateFile(Plugin):
    """
    构建用于更新的软件包app/plugins/build_in
    """
    ICON=ft.icons.BUILD_CIRCLE_OUTLINED
    def process(self, data, **kwargs):
        # 压缩整个 app 目录
        build_in_dir = ENV['update_dir']
        with zipfile.ZipFile(f"assets{os.path.sep}update.zip", "w") as zip_file:
            for foldername, subfolders, filenames in os.walk(build_in_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, build_in_dir)
                    zip_file.write(file_path, arcname)
        return "更新包构建成功!!!"
