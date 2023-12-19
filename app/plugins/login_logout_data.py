import re
import zipfile
from app.plug import *

@Plug.register("存入登入登出信息-0070")
class LoadDayData(UIPlugin):
    """
    导入某日的日流水信息到数据库
    """
    ICON = ft.icons.BLINDS_SHARP
    def process(self, data, db, page, container, **kwargs):
        datas = []
        columns = []
        errs = []
        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                try:
                    f = e.files[0].path
                    if (f.endswith(".txt")):
                        with open(f, mode="r", encoding='gbk') as file:
                            columns, datas, errs = Plug.run(plugins=("_load_login_logout_data",), data=file, has_decode=True)
                    elif (f.endswith(".zip")):
                        with zipfile.ZipFile(f, 'r') as zip_file:
                            file_list = zip_file.namelist()
                            for file in file_list:
                                with zip_file.open(file, mode="r") as file:
                                    columns, datas, errs = Plug.run(plugins=("_load_login_logout_data",), data=file, has_decode=False)
                    else:
                        Plug.run(plugins=("_notice",), data=f"请选择txt、zip文件", page=page, **kwargs)
                        return

                    if len(errs) > 0:
                        with open("errs.txt", encoding='utf-8', mode='w') as err_f:
                            for line in errs:
                                err_f.write(" ".join(line) + "\n")
                    
                    table = db.get_table("login_logout_data")
                    text = ft.Text("加载中...")
                    pb = ft.ProgressBar(width=400)
                    container.content = ft.Column([text, pb])
                    container.update()
                    for idx, line in enumerate(datas):
                        info = dict(zip(columns, line))
                        try:
                            table.insert(info)
                            pbt = (idx+1) / len(datas)
                            text.value = str(pbt)
                            pb.value = pbt
                            text.update()
                            pb.update()
                            container.update()
                        except Exception as err:
                            Plug.run(plugins=("_notice",), data=err, page=page)

                    Plug.run(plugins=("_notice",), data="加载完成", page=page, **kwargs)
                    page.update()
                except Exception as e:
                    Plug.run(plugins=("_notice",), data=e, page=page)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()

        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.CLOUD_UPLOAD_OUTLINED,
                    size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files()),
            alignment=ft.alignment.center)


@Plug.register("_load_login_logout_data")
class LoadDayDataMethod(UIPlugin):
    """
    data是一个文件句柄
    """
    def process(self, data, has_decode=True, **kwargs):
        return self.load_file(data, has_decode)

    def mid_handler(self, mid: list):
        if len(mid) == 10:
            return mid
        time_mid = [len(i.split(":")) == 3 for i in mid]
        time_len = 0
        res = [""] * 10
        for item in time_mid:
            if item:
                res[time_len] = mid[time_len]
                time_len += 1
            else: break
        start_idx = 7
        for i in range(time_len, len(mid)):
            res[start_idx] = mid[i]
            start_idx += 1
        return res

    def load_file(self, f, has_decode=True):
        datas = []
        keys = []
        errs = []
        line = f.readline() if has_decode else f.readline().decode('gbk')
        while line != "":
            if line.startswith("1"):
                titleline = f.readline() if has_decode else f.readline().decode('gbk')
                splitline = f.readline() if has_decode else f.readline().decode('gbk')
                subtitleline = re.split(r'\s+', f.readline().strip() if has_decode else f.readline().decode('gbk').strip())
                columns = re.split(r'\s+', f.readline().strip() if has_decode else f.readline().decode('gbk').strip())
                if keys == [] and len(columns) > 1:
                    keys = columns 
                    keys = [*keys, "年", "月", "日"]
                info = f.readline() if has_decode else f.readline().decode('gbk')
                while not (info.startswith("1") or info == " " or info == ""):
                    lst = re.split(r'\s+', info.strip())
                    info = [*lst, *subtitleline[3].split("/")]
                    if len(info) != 10:
                        errs.append(info)
                    else:
                        datas.append(info)
                    info = f.readline() if has_decode else f.readline().decode('gbk')
                line = info
                continue
            line = f.readline() if has_decode else f.readline().decode('gbk')
        return (keys, datas, errs)