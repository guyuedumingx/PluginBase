from ..plug import *
import flet as ft
import datetime
import numpy
import pandas as pd

@PlugManager.register('计算签证到期日')
class CleanMarkdownItalic(Plugin):
    """
    计算签证到期日
    """
    ICON=ft.icons.DATE_RANGE_OUTLINED
    def process(self, key_word, page, **kwargs):
        def pick_time(e):
            start_time.value = date_picker.value.strftime("%Y/%m/%d")
            recale(e)

        def recale(e):
            year,month,day = start_time.value.split("/")
            v = datetime.datetime(year=int(year),month=int(month),day=int(day)) + datetime.timedelta(days=int(day_feild.value))
            result.value = v.strftime("%Y-%m-%d")
            page.update()

        date_picker = ft.DatePicker(
            on_change=pick_time,
            first_date=datetime.datetime(2023, 10, 1)
        )
        start_time = ft.TextField(label="初始日期",on_change=recale, value=datetime.datetime.now().strftime("%Y/%m/%d"))
        day_feild = ft.TextField(label="可停留天数", on_change=recale)

        def btn_click(e):
            day_feild.value = e.control.text
            recale(e)
        btn_list = [ft.OutlinedButton(i, on_click=btn_click, col={"md":2}) for i in [30, 45, 60, 90, 120, 180]]

        day_feild.value = 30
        result = ft.Text(weight=ft.FontWeight.BOLD, size=100, color=ft.colors.GREY_600)

        page.overlay.append(date_picker)

        date_button = ft.ElevatedButton(
            "选择日期",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: date_picker.pick_date(),
        )
        return ft.ListView(
            [date_button, start_time, day_feild, ft.ResponsiveRow(btn_list),
            ft.Container(result,
                         alignment=ft.alignment.center,
                         expand=1,
                         padding=20)],expand=1, spacing=20)
    

@PlugManager.register('测试Table')
class TestTableUI(Plugin):
    def process(self, data, **kwargs):
        columns = ["姓名", "编号", "内容的"]
        rows = [[f"森啦 {i}", str(i), f"内容 {i}"] for i in range(1000)] 
        return PlugManager.run(plugins=("_tableUI",),data=rows, columns=columns, **kwargs)
    

@PlugManager.register('_plugin_search_stream')
class PluginSearchStream(Plugin):
    """
    主页搜索插件流
    """
    def process_list(self, key_word, **kwargs):
        return ("_search_plugin", "_build_show_cards", "_listUI")

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
    def process(self, data, page, container,**kwargs):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                try:
                    f = e.files[0].path
                    data = None
                    if(f.endswith(".xlsx") or f.endswith(".xls")):
                        data = pd.read_excel(f)
                    elif(f.endswith(".csv")):
                        data = pd.read_csv(f)
                    else:
                        PlugManager.run(plugins=("_notice",),data=f"请选择xlsx xls csv文件", page=page, **kwargs)
                        return
                    container.content = PlugManager.run(plugins=("_pandas_show",),
                                    data=data,
                                    page=page, **kwargs)
                    page.update()
                except Exception as e:
                    PlugManager.run(plugins=("_notice",),data=f"load fails!!!", page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.CLOUD_UPLOAD_OUTLINED, size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files()),
        alignment=ft.alignment.center
        )