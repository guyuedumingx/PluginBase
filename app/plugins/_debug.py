from app.plug import *
import json
import zipfile

@Plug.register('键值对数据库')
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
        self.container.content = Plug.run(
            plugins=("_dictUI",), data=data, mode="edit")
        self.container.update()

@Plug.register('数据库查询')
class KeyValueDatabase(UIPlugin):
    """
    数据库的查询
    """
    ICON = ft.icons.DATA_OBJECT

    def process(self, data, search_feild: ft.TextField, container, db, **kwargs):
        self.search_feild = search_feild
        self.container = container
        self.db = db
        search_feild.hint_text = "Enter a table name to fine data"
        search_feild.on_submit = self.search_handler
        search_feild.on_change = None
        self.kwargs = kwargs
        return ft.Text("Search a Database")

    def search_handler(self, e):
        key_word = self.search_feild.value
        if (key_word == ''):
            return
        table = self.db[key_word]
        self.container.content = Plug.run(
            plugins=("_tableUI4Database",), data=table.all(), container=self.container,**self.kwargs)
        self.container.update()

@Plug.register("构建更新包")
class BuildUpdateFile(Plugin):
    """
    构建用于更新的软件包app/plugins/build_in
    """
    ICON=ft.icons.BUILD_CIRCLE_OUTLINED
    def process(self, data, **kwargs):
        # 压缩整个 app 目录
        build_in_dir = ENV['plugin_dir']+os.path.sep+"build_in"
        with zipfile.ZipFile(f"assets{os.path.sep}update.zip", "w") as zip_file:
            for foldername, subfolders, filenames in os.walk(build_in_dir):
                for filename in filenames:
                    file_path = os.path.join(foldername, filename)
                    arcname = os.path.relpath(file_path, build_in_dir)
                    zip_file.write(file_path, arcname)
        return "更新包构建成功!!!"


@Plug.register("Linechart")
class BaseBarChart(UIPlugin):

    def process(self, data:dict, **kwargs):
        data = dict(apple=[(1, 30), (2, 40), (3, 50), (4, 20), (5, 10)],
                    bogo=[(1, 15), (2, 25), (3, 40), (4, 10)])
        return Plug.run(plugins=("_linechart",), data=data, **kwargs)