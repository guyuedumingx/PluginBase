from app.plug import *
import flet as ft
import requests

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
                server_addr="127.0.0.1", server_port=36909, **kwargs):
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
