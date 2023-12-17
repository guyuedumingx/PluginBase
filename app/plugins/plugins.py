from app.plug import *
import flet as ft
import pandas as pd


@Plug.register('加载EXCEL')
class LoadXLSX(UIPlugin):
    """
    加载EXCEL的XLSX、XLS、XLSM文件
    """
    ICON=ft.icons.GRID_4X4_OUTLINED
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


@Plug.register('SWIFT知识库')
class Knowledge(UIPlugin):
    """
    详解SWIFT报文知识库
    """
    ICON = ft.icons.AUTO_STORIES

    def process(self, data, **kwargs):
        return Plug.run(plugins=("_search_base",), data="knowledge", **kwargs)
