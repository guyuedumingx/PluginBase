from app.plug import *
import flet as ft
import datetime
import pandas as pd


@Plug.register('计算签证到期日')
class CleanMarkdownItalic(UIPlugin):
    """
    计算签证到期日
    """
    ICON = ft.icons.DATE_RANGE_OUTLINED
    time_format = "%y%m%d"
    VERSION="1.2.0"
    def process(self, data, page, search_feild: ft.TextField, **kwargs):
        def pick_time(e):
            start_time.value = date_picker.value.strftime(self.time_format)
            recale(e)

        def recale(e):
            date_str = start_time.value
            year = '20' + date_str[:2]  # 取前两位作为年份
            month = date_str[2:4]       # 取第三和第四位作为月份
            day = date_str[4:]          # 取最后两位作为日期
            try:
                v = datetime.datetime(year=int(year), month=int(month), day=int(
                    day)) + datetime.timedelta(days=int(day_feild.value))
                result.value = v.strftime("%Y-%m-%d")
                page.update()
            except:
                pass

        date_picker = ft.DatePicker(
            on_change=pick_time,
            first_date=datetime.datetime.now()
        )
        start_time = search_feild
        start_time.label = "开始日期"
        start_time.on_change = recale
        start_time.input_filter=ft.NumbersOnlyInputFilter()
        # start_time.value = datetime.datetime.now().strftime(self.time_format)
        start_time.value = ""
        start_time.suffix_text = "YEAR-MONTH-DAY"
        day_feild = ft.TextField(
            label="可停留天数", on_change=recale, suffix_text="DAYS")

        def btn_click(e):
            day_feild.value = e.control.text
            recale(e)
        btn_list = [ft.OutlinedButton(i, on_click=btn_click, col={"md": 2}) for i in [
            30, 45, 60, 90, 120, 180]]

        day_feild.value = 30
        result = ft.Text(weight=ft.FontWeight.BOLD,
                         size=100, color=ft.colors.GREY_600)

        page.overlay.append(date_picker)

        date_button = ft.ElevatedButton(
            "选择日期",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: date_picker.pick_date(),
        )
        return ft.ListView(
            [date_button, day_feild, ft.ResponsiveRow(btn_list),
             ft.Container(result,
                          alignment=ft.alignment.center,
                          expand=1,
                          padding=20)], expand=1, spacing=20)


@Plug.register('测试Table')
class TestTableUI(UIPlugin):
    def process(self, data, **kwargs):
        columns = ["姓名", "编号", "内容的"]
        rows = [[f"森da啦 {i}", str(i), f"内容 {i}"] for i in range(1000)]
        return Plug.run(plugins=("_tableUI",), data=rows, columns=columns, **kwargs)


@Plug.register('_pandas_show')
class PandasShow(Plugin):
    """
    显示一个pandas DataFrame
    data: DataFrame
    """

    def process(self, data, **kwargs):
        return Plug.run(plugins=("_tableUI",),
                               columns=data.columns.values,
                               data=data.values.tolist(),
                               **kwargs)


@Plug.register('加载XLSX')
class LoadXLSX(UIPlugin):
    def process(self, data, page, container, **kwargs):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                try:
                    f = e.files[0].path
                    data = None
                    if (f.endswith(".xlsx") or f.endswith(".xls") or f.endswith(".xlsm")):
                        data = pd.read_excel(f)
                    elif (f.endswith(".csv")):
                        data = pd.read_csv(f)
                    else:
                        Plug.run(
                            plugins=("_notice",), data=f"请选择xlsx xls csv xlsm文件", page=page, **kwargs)
                        return
                    container.content = Plug.run(plugins=("_pandas_show",),
                                                        data=data,
                                                        page=page, **kwargs)
                    page.update()
                except Exception as e:
                    Plug.run(plugins=("_notice",),
                                    data=e, page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.CLOUD_UPLOAD_OUTLINED,
                    size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files()),
            alignment=ft.alignment.center)


@Plug.register('明码转换')
class CodeTrans(UIPlugin):
    """
    把四位数字的中文商用电码转换为中文

    1. 可以直接在搜索框输入电码
    2. 支持多电码同时转义, 用**空格**分割不同电码
    > `_` 代表码库中无该电码对应字
    """
    ICON = ft.icons.TRANSLATE

    def process(self, data, search_feild: ft.TextField, db, container, **kwargs):
        self.db = db
        self.container = container
        search_feild.on_change = self.on_change
        search_feild.hint_text = "Enter code"

    def on_change(self, e):
        code_list = e.data.split(" ")
        data = [self.db['中文商用电码表'].find_one(key=code) for code in code_list]
        res = []
        for item in data:
            try:
                res.append(item['value'])
            except:
                res.append("_")
        self.container.content = ft.ListView(
            [ft.ResponsiveRow(
                [ft.Text(i, size=30, col={"xs": 1}) for i in res])],
            expand=1, auto_scroll=True)
        self.container.update()


@Plug.register('SWIFT知识库')
class Knowledge(UIPlugin):
    """
    详解SWIFT报文知识库
    """
    ICON = ft.icons.AUTO_STORIES

    def process(self, data, **kwargs):
        return Plug.run(plugins=("_search_base",), data="knowledge", **kwargs)


@Plug.register('User管理')
class UserBase(UIPlugin):
    ICON = ft.icons.MANAGE_ACCOUNTS
    def process(self, data, **kwargs):
        return Plug.run(plugins=("_search_base",), data="user", ui_template="_dictUI", **kwargs)


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
        

@Plug.register('test数据库')
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