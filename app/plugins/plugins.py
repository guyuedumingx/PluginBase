from app.plug import *
import flet as ft
import datetime
import pandas as pd


@PlugManager.register('计算签证到期日')
class CleanMarkdownItalic(Plugin):
    """
    计算签证到期日
    """
    ICON = ft.icons.DATE_RANGE_OUTLINED
    time_format = "%y%m%d"

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
        start_time.value = datetime.datetime.now().strftime(self.time_format)
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


@PlugManager.register('测试Table')
class TestTableUI(Plugin):
    def process(self, data, **kwargs):
        columns = ["姓名", "编号", "内容的"]
        rows = [[f"森啦 {i}", str(i), f"内容 {i}"] for i in range(1000)]
        return PlugManager.run(plugins=("_tableUI",), data=rows, columns=columns, **kwargs)

@PlugManager.register('_pandas_show')
class PandasShow(Plugin):
    """
    显示一个pandas DataFrame
    data: DataFrame
    """
    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_tableUI",),
                               columns=data.columns.values,
                               data=data.values.tolist(),
                               **kwargs)


@PlugManager.register('加载XLSX')
class LoadXLSX(Plugin):
    def process(self, data, page, container, **kwargs):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                try:
                    f = e.files[0].path
                    data = None
                    if (f.endswith(".xlsx") or f.endswith(".xls")):
                        data = pd.read_excel(f)
                    elif (f.endswith(".csv")):
                        data = pd.read_csv(f)
                    else:
                        PlugManager.run(
                            plugins=("_notice",), data=f"请选择xlsx xls csv文件", page=page, **kwargs)
                        return
                    container.content = PlugManager.run(plugins=("_pandas_show",),
                                                        data=data,
                                                        page=page, **kwargs)
                    page.update()
                except Exception as e:
                    PlugManager.run(plugins=("_notice",),
                                    data=e, page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.CLOUD_UPLOAD_OUTLINED,
                    size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files()),
            alignment=ft.alignment.center)


@PlugManager.register('明码转换')
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


@PlugManager.register('免签国查询')
class Italic(UIPlugin):
    pass


@PlugManager.register('签证类型查询')
class Italic(UIPlugin):
    pass


@PlugManager.register('货币编码查询')
class Italic(UIPlugin):
    pass


@PlugManager.register('SWIFT知识库')
class Knowledge(UIPlugin):
    """
    详解SWIFT报文知识库
    """
    ICON = ft.icons.BOOKMARKS_OUTLINED

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_search_base",), data="knowledge", **kwargs)


@PlugManager.register('User知识库')
class UserBase(UIPlugin):
    ICON = ft.icons.BOOKMARKS_OUTLINED

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_search_base",), data="user", ui_template="_dictUI", **kwargs)
