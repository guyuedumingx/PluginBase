from app.plug import *
import json
import flet as ft
import os
import shutil
from functools import partial
from uvicorn.config import Config
from uvicorn.main import Server
import asyncio
import socket


@PlugManager.register('_search_plugin')
class SearchPlugin(Plugin):
    """
    data: word: the search key word
    """

    def process(self, word, show_build_in=False, **kwargs):
        plugins = PlugManager.PLUGINS
        func = partial(self.match_rules, word=word, show_build_in=show_build_in)
        return dict(filter(lambda x: func(x=x), plugins.items()))

    def match_rules(self, word, x, show_build_in=False):
        name, plug = x[0], x[1]
        if (not show_build_in and name.startswith("_")):
            return False
        matchs = plug.MATCHS
        for item in matchs:
            if (word in item):
                return True


@PlugManager.register('_plugin_cards')
class BuildShowCards(Plugin):
    def process(self, data: dict, plugin_onclick: lambda e: e, **kwargs):
        tile_lst = [ft.ListTile(
                leading=ft.Icon(item[1].ICON),
                title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                subtitle=ft.Text(
                    item[1].DESC.strip().split("\n")[0]
                ),
                on_click=plugin_onclick,
                ) for item in data.items()]
        return tile_lst

@PlugManager.register('_plugin_search_stream')
class PluginSearchStream(UIPlugin):
    """
    主页搜索插件流
    data: word: the search key word
    """

    def process(self, key_word, plugin_onclick, **kwargs):
        return PlugManager.run(plugins=("_search_plugin", "_plugin_cards", "_flowUI"),
                               data=key_word,
                               plugin_onclick=plugin_onclick,
                               **kwargs)


@PlugManager.register('_mainbackground')
class MainShowBackground(UIPlugin):
    """
    显示在主页的初始背景
    """

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_plugin_search_stream",),
                               data=data,
                               plugin_onclick=PlugManager.getPlugin("_index").load_plugin)


@PlugManager.register('_defaultbackground')
class DefaultBackground(UIPlugin):
    """
    默认背景
    """

    def process(self, data, **kwargs):
        return ft.Container(content=ft.Icon(
            ft.icons.SETTINGS,
            size=300,
            color=ft.colors.GREY_200),
            expand=1,
            alignment=ft.alignment.center)


@PlugManager.register('安装插件')
class InstallPlugin(UIPlugin):
    """
    安装新插件
    """
    ICON = ft.icons.UPLOAD_FILE

    def process(self, data, page, **kwargs):

        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                success = []
                plugin_dir = ENV['plugin_dir']
                if not os.path.exists(plugin_dir):
                    os.makedirs(plugin_dir)
                try:
                    for f in e.files:
                        if not f.name.endswith(".py"):
                            continue
                        shutil.copyfile(f.path, plugin_dir+os.sep+f.name)
                        success.append(f)
                    PlugManager.run(
                        plugins=("_preload_plugin", "_notice"), data=plugin_dir, page=page, **kwargs)
                except Exception as e:
                    PlugManager.run(plugins=("_notice",),
                                    data=e, page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.UPLOAD_FILE,
                    size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
            alignment=ft.alignment.center
        )


@PlugManager.register('_notice')
class Notice(Plugin):
    def process(self, data, page: ft.Page, **kwargs):
        page.snack_bar = ft.SnackBar(ft.Text(data))
        page.snack_bar.open = True
        page.update()
        return data


@PlugManager.register('_listUI')
class ListUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.ListView(controls=data, expand=1)


@PlugManager.register('_flowUI')
class FlowUI(UIPlugin):
    def process(self, data: list, counts_per_row=2, **kwargs):
        for item in data:
            item.col = {"sm": 12 / counts_per_row,
                        "xs": 12, "lg": 12 / (counts_per_row*2)}
        return ft.ListView(controls=[ft.ResponsiveRow(controls=data, expand=1)], expand=1)


@PlugManager.register('_tableUI')
class TableUI(UIPlugin):
    def process(self, rows: list, columns=[], **kwargs):
        rowsUI = []
        for row in rows:
            cellsUI = [ft.DataCell(ft.Text(value=i),
                                   on_tap=self.on_tap
                                   ) for i in row]
            rowsUI.append(ft.DataRow(cells=cellsUI))
        columnsUI = [ft.DataColumn(ft.TextField(
            value=col,
            border=ft.InputBorder.NONE,
            )
        ) for col in columns]
        return ft.ListView([ft.DataTable(rows=rowsUI, columns=columnsUI, expand=1)], expand=1)
    
    def on_tap(self, e):
        text = e.control.content.value
        e.control.content = ft.TextField(
            value=text,
            border=ft.InputBorder.NONE,
            on_blur=partial(self.leave_tap,cell=e.control),
            on_submit=partial(self.leave_tap,cell=e.control),
            )
        e.control.update()
        
    def leave_tap(self, e, cell=ft.Text("")):
        text = e.control.value
        cell.content = ft.Text(text)
        cell.update()


@PlugManager.register('_dictUI')
class DictUI(UIPlugin):
    """
    显示key value 的 dict
    mode: show edit
    multiline: enable multiline turn into textarea
    """

    def process(self, data: dict, mode='show', multiline=False, **kwargs):
        def on_change(e):
            data[e.control.hint_text] = e.data
        return ft.ListView([ft.ResponsiveRow(
            controls=[
                ft.ListTile(leading=ft.Icon(ft.icons.KEY), title=ft.Text(
                    item[0], size=ft.FontWeight.W_500), col={"xs": 12, "md": 3}),
                ft.TextField(value=item[1],
                             border=ft.InputBorder.UNDERLINE,
                             hint_text=item[0], col={"xs": 12, "md": 9},
                             on_change=on_change,
                             disabled=mode == 'show',
                             multiline=multiline)
            ],
        ) for item in data.items()], expand=1, spacing=10)


@PlugManager.register('_tocUI')
class TocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        def on_click(e):
            key = e.control.title.value
            main_container.content = data[key]
            main_container.update()

        main_container = ft.Container(expand=1)
        listiles = [ft.ListTile(leading=ft.Icon(ft.icons.BOOKMARK_OUTLINE_ROUNDED),
                    title=ft.Text(i), on_click=on_click)
                    for i in data.keys()]
        return ft.ResponsiveRow(
            controls=[
                ft.ListView(listiles, col={"xs": 12, "md": 3}, expand=1),
                ft.ListView([main_container], col={
                            "xs": 12, "md": 9}, expand=1)
            ],
            expand=True
        )


@PlugManager.register('_markdown_tocUI')
class MarkdownTocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        data = {k: ft.Markdown(
                        value=v,
                        col={"xs": 12, "md": 9},
                        expand=1,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
                        )
                for k, v in data.items()}
        return PlugManager.run(("_tocUI",), data, **kwargs)


@PlugManager.register('环境信息')
class ENVInformation(UIPlugin):
    """
    查看ENV中的所有信息
    """
    ICON = ft.icons.MISCELLANEOUS_SERVICES

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_dictUI",), data=ENV, mode="show", **kwargs)


@PlugManager.register('重新加载')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    ICON=ft.icons.REFRESH
    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_preload_plugin",),data=ENV['plugin_dir'])

@PlugManager.register('_tipsview')
class TipsView(UIPlugin):
    def process(self, data, plugin_obj, **kwargs):
        ui = [
            ft.Text(data, size=30),
            ft.Text(plugin_obj.VERSION),
            ft.Markdown(plugin_obj.DESC,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
            ft.Text("SOURCE", size=30),
            ft.Text("".join(plugin_obj.SOURCE), size=15)
        ]
        return ft.ListView(ui, expand=1, spacing=10)


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
        

@PlugManager.register('_search_base')
class SearchBase(UIPlugin):
    """
    基础知识库样式
    """
    ICON = ft.icons.BOOKMARKS_OUTLINED

    def process(self, data: dict, db, search_feild, container, ui_template="_markdown_tocUI", **kwargs):
        self.db = db
        self.container = container
        search_feild.on_change = self.on_change
        self.table_name = data
        self.ui_template = ui_template
        return self.ui("")

    def on_change(self, e):
        self.container.content = self.ui(e.data)
        self.container.update()

    def ui(self, key):
        data = {}
        table = self.db.get_table(self.table_name, primary_id="key")
        for item in table.find(key={'like': f"%{key}%"}):
            data[item['key']] = item['value']
        return PlugManager.run(plugins=(self.ui_template,), data=data)


@PlugManager.register('_index')
class IndexPlugin(UIPlugin):
    """
    首页插件：项目起始页
    page: the page to load in
    search_feild: the search area showed in all page
    container: the main container that developer can change and also
               the main area to show all information of the plugin
    """
    ICON = ft.icons.SEARCH
    HINT_TEXT = "Search Plugins"

    def process(self, page: ft.Page, **kwargs):
        page.window_height = 600
        page.window_width = 800 
        page.fonts = {
            "LXGWWenKai-Regular": "fonts/LXGWWenKai-Regular.ttf",
        }
        page.theme = ft.Theme(font_family="LXGWWenKai-Regular")
        self.page = page
        self.search_feild = ft.TextField(
            hint_text=self.HINT_TEXT,
            prefix_icon=self.ICON,
            border_radius=40,
            on_change=self.search_func
        )
        self.container = ft.Container(PlugManager.run(plugins=("_plugin_search_stream",),
                                                      plugin_onclick=self.load_plugin), expand=1)
        self.page.add(
            ft.ResponsiveRow([ft.Container(self.search_feild, padding=5,)]),
            self.container
        )
        self.search_feild.focus()
        self.page.update()
        return page

    def load_plugin(self, e):
        plugin_name = e.control.title.value
        PlugManager.run(plugins=("_load_plugin",),
                        data=plugin_name, page=self.page)

    def search_func(self, e):
        self.search_feild.value = e.data
        self.container.content = PlugManager.run(
            plugins=("_plugin_search_stream",),
            plugin_onclick=self.load_plugin,
            data=e.data)
        self.search_feild.focus()
        self.page.update()


@PlugManager.register('_load_plugin')
class BasePluginView(UIPlugin):
    def process(self, plugin_name, page, **kwargs):
        self.plugin_name = plugin_name
        self.plugin = PlugManager.getPlugin(plugin_name)
        self.page = page
        home_btn, search_feild, tips_btn = self.base_ui(
            page, plugin_name, self.plugin.ICON)
        self.container = PlugManager.run(plugins=("_defaultbackground",))
        plugin = PlugManager.getPlugin(plugin_name)
        func = partial(
            PlugManager.run,
            search_feild=search_feild,
            page=page,
            container=self.container,
            data=plugin_name
            )
        if(not isinstance(plugin, UIPlugin)):
            func(plugins=(plugin_name,"_notice"))
            page.update()
            return

        page.views.append(
            ft.View(
                "/" + plugin_name,
                [
                    ft.ResponsiveRow([search_feild, home_btn]),
                    tips_btn,
                    self.container
                ]
            )
        )
        page.go("/"+plugin_name)
        page.update()
        self.container.content = func(plugins=(plugin_name,)) 
        search_feild.focus()
        page.update()
        return plugin_name

    def tips_onclick(self, e):
        back_btn = ft.FloatingActionButton(icon=ft.icons.ARROW_BACK,
                                           scale=0.7,
                                           opacity=0.5,
                                           bgcolor=ft.colors.WHITE,
                                           shape=ft.CircleBorder(),
                                           on_click=lambda _: self.page.views.pop() and self.page.update()
                                           )
        url = "/" + self.plugin_name + "/tips"
        container = PlugManager.run(
            plugins=("_tipsview",), data=self.plugin_name, plugin_obj=self.plugin)
        self.page.views.append(ft.View(url, [back_btn, container]))
        self.page.go(url)

    def search_feild_onchange(self, e):
        self.page.views.pop() and self.page.update()
        PlugManager.getPlugin("_index").search_func(e)

    def base_ui(self, page, plugin_name, icon=ft.icons.SETTINGS):
        home_btn = ft.Container(
            ft.Icon(name=ft.icons.HOME),
            col={"xs": 2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
            on_click=lambda _: page.views.pop() and page.update()
        )
        search_feild = ft.TextField(
            hint_text=plugin_name,
            prefix_icon=icon,
            border_radius=40,
            col={"xs": 10, "sm": 11, "md": 11, "xl": 11},
            on_change=self.search_feild_onchange
        )
        tips_btn = ft.FloatingActionButton(icon=ft.icons.TIPS_AND_UPDATES,
                                           scale=0.7,
                                           opacity=0.5,
                                           bgcolor=ft.colors.WHITE,
                                           shape=ft.CircleBorder(),
                                           on_click=self.tips_onclick
                                           )
        return (home_btn, search_feild, tips_btn)
