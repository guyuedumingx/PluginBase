from app.plug import *
import json

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


@Plug.register('_tableUI4Database')
class TableUI(UIPlugin):
    def process(self, data, page, container, **kwargs):
        self.container = container
        self.page = page
        self.rowsUI = []
        columns = data.keys
        for row in data:
            cellsUI = []
            for i in range(len(columns)):
                cellsUI.append(self.build_cell(row[columns[i]]))
            self.rowsUI.append(ft.DataRow(cells=cellsUI))
        self.columnsUI = [ft.DataColumn(
            ft.TextField(value=col, border=ft.InputBorder.NONE)) 
            for col in columns]
        self.operators = [ft.Container(
            ft.Text("加一列"),
            bgcolor=ft.colors.AMBER_400,
            on_click=self.add_row,
            ) for i in range(5)]
        return self.build()
    
    def add_column(self, e):
        self.columnsUI.append(ft.DataColumn(
            ft.TextField(
                value=f"Column{len(self.columnsUI)}",
                border=ft.InputBorder.NONE)))
        for row in self.rowsUI:
            row.cells.append(self.build_cell())
        self.container.content = self.build()
        self.container.update()
    
    def add_row(self, e):
        cells = []
        for i in range(len(self.columnsUI)):
            cells.append(self.build_cell()) 
        self.rowsUI.append(ft.DataRow(cells=cells))
        self.container.content = self.build()
        self.container.update()
    
    def build_cell(self, value=""):
        return ft.DataCell(
            ft.TextField(
                value=value,
                border=ft.InputBorder.NONE,
                multiline=True,
                ),
            show_edit_icon=True,
            on_tap=self.to_edit_view,
        )
        
    def to_edit_view(self, e):
        url = self.page.views[-1].route + "/edit"
        inner_feild = ft.TextField(value=e.control.content.value, multiline=True, expand=1)
        self.page.views.append(ft.View(
                url,
                [
                    ft.OutlinedButton(text="Save", on_click=partial(self.edit_save, out_feild=e.control.content,inner_feild=inner_feild)),
                    ft.ListView([inner_feild], expand=1),
                ]
            )
        )
        self.page.go(url)
        self.page.update()
        
    def edit_save(self, e, out_feild, inner_feild):
        out_feild.value = inner_feild.value
        self.page.views.pop() and self.page.update()
        
    def build(self):
        return ft.ListView([
            ft.Row(self.operators),
            ft.DataTable(
                rows=self.rowsUI,
                columns=self.columnsUI,
                expand=1,
            )],
            expand=1,
        )
        

@Plug.register("Linechart")
class BaseBarChart(UIPlugin):

    def process(self, data:dict, **kwargs):
        data = dict(apple=[(1, 30), (2, 40), (3, 50), (4, 20), (5, 10)],
                    bogo=[(1, 15), (2, 25), (3, 40), (4, 10)])
        return Plug.run(plugins=("_linechart",), data=data, **kwargs)