from .plug import *
import importlib
import flet as ft
import dataset
import os
import shutil
from functools import partial

@PlugManager.register('_search_plugin')
class SearchPlugin(Plugin):
    """
    data: word: the search key word
    """
    def process(self, word, **kwargs):
        plugins = PlugManager.PLUGINS
        func = partial(self.match_rules, word=word)
        return dict(filter(lambda x: func(x=x), plugins.items()))
    
    def match_rules(self, word, x):
        name, plug = x[0], x[1]
        if(name.startswith("_")): return False
        matchs = plug.MATCHS
        for item in matchs:
            if(word in item): return True

@PlugManager.register('_plugin_cards')
class BuildShowCards(Plugin):
    def process(self, data: dict, plugin_onclick: lambda e:e, **kwargs):
        return [ft.ListTile(
                leading=ft.Icon(item[1].ICON),
                title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                subtitle=ft.Text(
                    item[1].DESC[0:31].strip()
                ),
                on_click=plugin_onclick,
                ) for item in data.items()]
        
@PlugManager.register('_plugin_search_stream')
class PluginSearchStream(UIPlugin):
    """
    主页搜索插件流
    data: word: the search key word
    """
    def process(self, key_word, **kwargs):
        indexPlugin = PlugManager.getPlugin("_index")
        return PlugManager.run(plugins=("_search_plugin", "_plugin_cards", "_flowUI"),
                               data=key_word,
                               plugin_onclick=indexPlugin.load_plugin)

@PlugManager.register('_mainbackground')
class MainShowBackground(UIPlugin):
    """
    显示在主页的初始背景
    """
    # def process(self, data, **kwargs):
    #     return ft.Container(content=ft.Icon(ft.icons.SETTINGS, 
    #         size=300, 
    #         color=ft.colors.GREY_200),
    #     expand=1,
    #     alignment=ft.alignment.center)

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_plugin_search_stream",), data=data)

@PlugManager.register('_setDB')
class SetGlobalDatabase(Plugin):
    """
    加载程序数据库
    Load Default Database
    data: url : the url to connect database would be like: sqlite:///plug.db
    """
    def process(self, url, **kwargs):
        db = dataset.connect(url)
        PlugManager.setState(db=db)
        return db 

@PlugManager.register('安装插件')
class InstallPlugin(UIPlugin):
    """
    安装新插件
    """
    ICON=ft.icons.UPLOAD_FILE
    def process(self, data, page, **kwargs):

        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                success = []
                plugin_dir = ENV['plugin_dir']
                try:
                    for f in e.files:
                        if not f.name.endswith(".py"): continue
                        shutil.copyfile(f.path, plugin_dir+os.sep+f.name)
                        success.append(f)
                    PlugManager.run(plugins=("_preload_plugin","_notice"),data=plugin_dir, page=page, **kwargs)
                except:
                    PlugManager.run(plugins=("_notice",),data=f"load fails!!!", page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.UPLOAD_FILE, size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
        alignment=ft.alignment.center
        )

@PlugManager.register('_notice')
class Notice(Plugin):
    def process(self, data, page:ft.Page, **kwargs):
        page.snack_bar = ft.SnackBar(ft.Text(data))
        page.snack_bar.open = True
        page.update()
        return data
    
@PlugManager.register('_listUI')
class ListUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.ListView(controls=data, expand=1)

@PlugManager.register('_gridUI')
class GridUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.GridView(controls=data,
                           child_aspect_ratio=1,
                           height=60,
                           max_extent=160,
                           )

@PlugManager.register('_flowUI')
class FlowUI(UIPlugin):
    def process(self, data: list, counts_per_row=2, **kwargs):
        for item in data:
            item.col = {"sm": 12 / counts_per_row, "xs": 12}
        return ft.ResponsiveRow(controls=data, expand=1)

@PlugManager.register('_tableUI')
class TableUI(UIPlugin):
    def process(self, rows: list, columns=[], **kwargs):
        rowsUI = []
        for row in rows:
            cellsUI = [ft.DataCell(ft.Text(i)) for i in row]
            rowsUI.append(ft.DataRow(cells=cellsUI))
        columnsUI = [ft.DataColumn(ft.Text(col)) for col in columns]
        return ft.ListView([ft.DataTable(rows=rowsUI, columns=columnsUI, expand=1)], expand=1)

@PlugManager.register('_dictUI')
class DictUI(UIPlugin):
    """
    显示key value 的 dict
    mode: show edit
    multiline: enable multiline turn into textarea
    """
    def process(self, data: dict, mode='edit', multiline=False, **kwargs):
        def on_change(e):
            data[e.control.hint_text] = e.data
        return ft.ListView([ft.ResponsiveRow(
            controls=[
                ft.ListTile(leading=ft.Icon(ft.icons.SETTINGS), title=ft.Text(item[0],size=ft.FontWeight.W_500), col={"xs":12, "md":3}),
                ft.TextField(value=item[1],
                            border=ft.InputBorder.UNDERLINE,
                            hint_text=item[0], col={"xs":12, "md":9},
                            on_change=on_change,
                            disabled=mode=='show',
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
                    title=ft.Text(i),on_click=on_click)
                    for i in data.keys()]
        return ft.ResponsiveRow(
            controls=[
                ft.ListView(listiles, col={"xs":12, "md": 3}, expand=1),
                ft.ListView([main_container], col={"xs":12, "md": 9}, expand=1)
            ],
            expand=True
        )

@PlugManager.register('_markdown_tocUI')
class MarkdownTocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        data = {k:ft.Markdown(value=v,col={"xs":12, "md": 9}, expand=1) for k,v in data.items()}
        return PlugManager.run(("_tocUI",), data, **kwargs)

@PlugManager.register('_load_plugin')
class LoadPlugin(Plugin):
    def process(self, data, search_feild: ft.TextField, **kwargs):
        self.indexPlugin = PlugManager.getPlugin("_index")
        search_feild.prefix_icon = PlugManager.PLUGINS[data].ICON
        search_feild.value = ""
        search_feild.hint_text = data
        search_feild.on_submit = self.plugin_inner_search
        search_feild.on_change = self.plugin_inner_search
        return PlugManager.run(plugins=(data,), data=data,**kwargs)

    def plugin_inner_search(self, e):
        self.indexPlugin.container.content = PlugManager.run(plugins=("_reset_search","_plugin_search_stream",),
                                 data=self.indexPlugin.search_feild.value)
        self.indexPlugin.page.update()

@PlugManager.register('_reset_search')
class ResetSearch(Plugin):
    def process(self, data, **kwargs):
        indexPlugin = PlugManager.getPlugin("_index")
        search_feild = indexPlugin.search_feild
        search = indexPlugin.search_func
        search_feild.prefix_icon = indexPlugin.ICON
        search_feild.label = None
        search_feild.hint_text = indexPlugin.HINT_TEXT
        search_feild.on_change = search
        search_feild.on_submit = search
        search_feild.focus()
        return data

@PlugManager.register('_preload_plugin')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    def process(self, plugin_dir, **kwargs):
        plugins_files = os.listdir(plugin_dir)
        for files in plugins_files:
            if not files.endswith(".py"): continue
            plug_path = plugin_dir + os.sep + files.split(".")[0]
            import_path = os.path.relpath(plug_path, ENV['app_dir']).replace(os.sep, ".")
            importlib.import_module(import_path, package="app")
        return f"RELOAD SUCCESS!!!"

@PlugManager.register('环境信息')
class TestTocUI(Plugin):
    """
    查看ENV中的所有信息
    """
    ICON=ft.icons.MISCELLANEOUS_SERVICES
    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_dictUI",), data=ENV, mode="edit", **kwargs)

@PlugManager.register('_rebind_search_action')
class RebindSearchAction(Plugin):
    def process(self, data, search_func, search_feild:ft.TextField, hint_text="", **kwargs):
        search_feild.label = data
        search_feild.on_change = search_func
        search_feild.on_submit = search_func
        search_feild.label = data
        search_feild.hint_text = hint_text
        search_feild.value = ""
        search_feild.focus()
        search_feild.update()
        return data

@PlugManager.register('键值对数据库')
class KeyValueDatabase(Plugin):
    """
    全局内置数据库的查询
    """
    ICON = ft.icons.DATA_OBJECT
    def process(self, data, search_feild:ft.TextField, container, db, **kwargs):
        self.search_feild = search_feild
        self.container = container
        self.db = db
        PlugManager.run(plugins=("_rebind_search_action",),
                        data=data,
                        search_func=self.search_handler,
                        hint_text="Enter a table name")
        return ft.Text("Enter a table name")
        
    def search_handler(self, e):
        key_word = self.search_feild.value
        if(key_word == ''): return
        table = self.db[key_word]
        data = {item['key']: item['value'] for item in table.all()}
        self.container.content = PlugManager.run(plugins=("_dictUI",),data=data, mode="edit")
        self.container.update()

@PlugManager.register('_index')
class IndexPlugin(UIPlugin):
    """
    首页插件：项目起始页
    page: the page to load in
    search_feild: the search area showed in all page
    container: the main container that developer can change and also
               the main area to show all information of the plugin
    """
    # ICON = ft.icons.MORE_VERT_SHARP
    ICON = ft.icons.SEARCH
    HINT_TEXT = "Search Plugins"
    def process(self, page, **kwargs):
        self.page = page
        self.search_feild = ft.TextField(hint_text=self.HINT_TEXT, prefix_icon=self.ICON, border_radius=40)
        self.container = ft.Container(PlugManager.run(
                        plugins=("_mainbackground",),data=""),
                        expand=1)

        # 构造全局上下文
        PlugManager.setState(page=page,
                             search_feild=self.search_feild,
                             container=self.container)

        page.add(ft.ResponsiveRow([
            ft.Container(
                ft.Icon(name=ft.icons.HOME),
                col={"xs":2, "sm": 1, "md": 1, "xl": 1},
                alignment=ft.alignment.center,
                height=60,
                on_click=self.back_to_home,
            ),
            ft.Container(
                self.search_feild, 
                padding=5,
                col={"xs":10, "sm": 11, "md": 11, "xl": 11},
            )
        ]))
        page.add(self.container)
        self.search_feild.on_change = self.search_func
        self.search_feild.focus()
        return page

    def load_plugin(self, e):
        plugin_name = e.control.title.value
        self.container.content = PlugManager.run(plugins=("_load_plugin",),
                                 data=plugin_name)
        self.container.update()
        self.page.update()
    
    def back_to_home(self, e):
        self.container.content = PlugManager.run(
                        plugins=("_reset_search","_mainbackground",))
        self.search_feild.value = ""
        self.page.update()

    def search_func(self, e):
        self.container.content = PlugManager.run(
                                plugins=("_plugin_search_stream",),
                                data=self.search_feild.value)
        self.page.update()