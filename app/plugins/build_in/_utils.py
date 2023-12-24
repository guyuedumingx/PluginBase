from app.plug import *
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment
import socket

@Plug.register('_pandas_show')
class PandasShow(Plugin):
    """
    显示一个pandas DataFrame
    data: DataFrame
    """
    def process(self, data: pd.DataFrame, **kwargs):
        return Plug.run(plugins=("_tableUI",),
                               columns=data.columns.values,
                               data=data.values.tolist(),
                               **kwargs)

@Plug.register("_choose_file")
class ChooseFile(UIPlugin):
    """
    this plugin choose one file
    data is the func to be call
    """
    def process(self, data, page, **kwargs):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                try:
                    data(e.files[0].path)
                except:
                    pass

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        file_picker.pick_files()
        page.update()


@Plug.register("_save_file")
class SaveFile(UIPlugin):
    def process(self, data, page, **kwargs):
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                data(e.path)
                Plug.run(plugins=("_notice",), data="Save Success", page=page)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        file_picker.save_file()
        page.update()


@Plug.register("_to_excel")
class ToExcel(Plugin):
    def process(self, data, columns=[], rows=[], **kwargs):
        # 创建新的工作簿和工作表
        wb = Workbook()
        ws = wb.active

        # 添加列标题
        ws.append(columns)

        # 添加行数据
        for row in rows:
            ws.append(row)

        # 设置单元格自动换行和调整列宽
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter  # 获取列字母

            for cell in col:
                cell.alignment = Alignment(wrap_text=True)  # 设置自动换行
                try:  # 尝试调整列宽
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass

            adjusted_width = (max_length + 2)
            ws.column_dimensions[column].width = adjusted_width

        # 保存工作簿
        wb.save(data)


@Plug.register("_get_local_ip")
class GetLocalIp(Plugin):
    def process(self, data, **kwargs):
        return self.get_local_ip()

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
            logging.error(e)
            return ""