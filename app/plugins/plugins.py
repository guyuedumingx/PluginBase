from app.plug import *
import flet as ft
import pandas as pd


@Plug.register('加载EXCEL')
class LoadXLSX(UIPlugin):
    """
    加载EXCEL的XLSX、XLS、XLSM文件
    """
    ICON=ft.icons.GRID_ON_OUTLINED
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
        
