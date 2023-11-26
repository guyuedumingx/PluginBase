from .plug import *
import importlib
import flet as ft
import dataset
import os
import shutil
from functools import partial

@PlugManager.register('_search_plugin')
class SearchPlugin(Plugin):
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

@PlugManager.register('_build_show_cards')
class BuildShowCards(Plugin):
    def process(self, plugin_dict, item_on_click, **kwargs):
        return [ft.ListTile(
                leading=ft.Icon(item[1].ICON),
                title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                subtitle=ft.Text(
                    item[1].DESC[0:31].strip()
                ),
                on_click=item_on_click,
                ) for item in plugin_dict.items()]
        
@PlugManager.register('_mainshow')
class MainShowBackground(UIPlugin):
    """
    显示在主页的初始背景
    """
    def process(self, data, **kwargs):
        return ft.Container(content=ft.Icon(ft.icons.SETTINGS, 
            size=300, 
            color=ft.colors.GREY_200),
        expand=1,
        alignment=ft.alignment.center)

@PlugManager.register('_plugin_search_stream')
class PluginSearchStream(UIPlugin):
    """
    主页搜索插件流
    """
    def process_list(self, key_word, **kwargs):
        if(key_word == ""): return ("_mainshow",)
        return ("_search_plugin", "_build_show_cards", "_listUI")

@PlugManager.register('_setDB')
class SetGlobalDatabase(Plugin):
   def process(self, url, **kwargs):
        db = dataset.connect(url)
        ENV['db'] = db
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
                try:
                    for f in e.files:
                        if not f.name.endswith(".py"): continue
                        shutil.copyfile(f.path, ENV['plugin_dir']+os.sep+f.name)
                        success.append(f)
                    PlugManager.run(plugins=("_notice",),data=f"load {[f.name for f in success]} success!!!", page=page, **kwargs)
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
        return ft.ListView(controls=data,expand=1)

@PlugManager.register('_gridUI')
class GridUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.GridView(controls=data,
                           runs_count=2,
                           child_aspect_ratio=1,
                           )

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
    def process_list(self, data, search_feild, search, **kwargs):
        search_feild.prefix_icon = PlugManager.PLUGINS[data].ICON
        search_feild.label = data
        search_feild.value = ""
        search_feild.on_submit = search
        search_feild.on_change = None
        return (data,)

@PlugManager.register('_exit_plugin')
class ExitPlugin(UIPlugin):
    def process_list(self, data, search_feild, search, search_btn,**kwargs):
        return ("_reset_search","_mainshow",)

@PlugManager.register('_reset_search')
class ResetSearch(Plugin):
    def process(self, data, search_feild, search, search_btn,**kwargs):
        search_feild.prefix_icon = None
        search_feild.label = None
        search_feild.on_change = search
        search_feild.on_submit = search
        search_btn.on_click = search
        return data

@PlugManager.register('_preload_plugin')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    """
    def process(self, data, **kwargs):
        plugins_files = os.listdir(ENV['plugin_dir'])
        for files in plugins_files:
            if not files.endswith(".py"): continue
            plug_path = ENV['plugin_dir'] + os.sep + files.split(".")[0]
            import_path = os.path.relpath(plug_path, ENV['app_dir']).replace(os.sep, ".")
            importlib.import_module(import_path, package="app")

@PlugManager.register('环境信息')
class TestTocUI(Plugin):
    """
    查看ENV中的所有信息
    """
    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_markdown_tocUI",),
                               data=ENV,
                               mode="edit",
                               **kwargs)

@PlugManager.register('键值对数据库')
class KeyValueDatabase(Plugin):
    def process(self, search_feild:ft.TextField, search_btn:ft.Container, 
                container, **kwargs):
        db = ENV['db']
        def search_handler(e):
            key_word = search_feild.value
            if(key_word == ''): return
            table = db[key_word]
            data = {item['key']: item['value'] for item in table.all()}
            container.content = PlugManager.run(plugins=("_dictUI",),data=data, mode="edit",**kwargs)
            container.update()
        search_feild.on_submit = search_handler
        search_feild.focus()

        search_btn.on_click = search_handler
        return ft.Text("Enter a database")
        
