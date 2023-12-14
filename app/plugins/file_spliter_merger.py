from app.plug import * 
import os

@Plug.register("文件分割合并器")
class FileSpliter(UIPlugin):
    """
    将大文件切割成小文件传输到内网
    """
    ICON=ft.icons.FILE_PRESENT_OUTLINED
    def process(self, data, page, **kwargs):
        self.page = page
        self.single_size = 100
        return self.build()
    
    def build(self):
        file_picker = ft.FilePicker(on_result=self.spliter_pick)
        self.page.overlay.append(file_picker)
        merge_picker = ft.FilePicker(on_result=self.merge_pick)
        self.page.overlay.append(merge_picker)
        self.page.update()
        self.spliter_feild = ft.TextField(disabled=True, expand=1, border=ft.InputBorder.UNDERLINE)
        self.merge_feild = ft.TextField(multiline=True, disabled=True,  expand=1, border=ft.InputBorder.UNDERLINE)
        self.size_feild = ft.Ref[ft.Text]()
        self.save_filename_feild = ft.TextField(border=ft.InputBorder.UNDERLINE, expand=1)

        return ft.ListView([
            ft.Text("分割", size=30, color=ft.colors.GREY_400),
            ft.Row([
                ft.OutlinedButton("打开文件", on_click=lambda _: file_picker.pick_files()),
                self.spliter_feild
                ]),
            ft.Row([
                ft.Text(f"每个文件将被分割为{self.single_size}M", ref=self.size_feild),
                ft.Container(ft.Slider(min=0, max=100, value=self.single_size, on_change=self.slider_changed, label="{value}%"), expand=1),
            ]),
            ft.OutlinedButton("分割", on_click=self.split_file),
            ft.Text("合并", size=30, color=ft.colors.GREY_400),
            ft.Row([
                ft.OutlinedButton("打开文件", on_click=lambda _:merge_picker.pick_files(allow_multiple=True)),
                self.merge_feild
                ]),
            ft.Row([
                ft.Text("合并后文件名:"),
                self.save_filename_feild,
            ]),
            ft.OutlinedButton("合并", on_click=self.merge_file),
        ], expand=1, spacing=10)
                
    def slider_changed(self, e):
        self.single_size = int(e.control.value)
        self.size_feild.current.value = f"每个文件将被分割为{self.single_size}M"
        self.page.update()
    
    def spliter_pick(self, e:ft.FilePickerResultEvent):
        if e != None:
            try:
                f = e.files[0]
                self.spliter_feild.value = f.path
                self.spliter_feild.update()
            except:
                pass
    
    def merge_pick(self, e:ft.FilePickerResultEvent):
        if e != None:
            try:
                paths = [f.path for f in e.files]
                paths.sort()
                self.merge_feild.value = "\n".join(paths)
                self.merge_feild.update()
            except:
                pass
    
    def merge_file(self, e):
        input_files = self.merge_feild.value.split("\n")
        filename = self.save_filename_feild.value
        if len(input_files) == 1 and input_files[0] == "":
            Plug.run(plugins=("_notice",), data="请选择需要被合并的文件", page=self.page)
            return
        if filename == "":
            Plug.run(plugins=("_notice",), data="请输入合并后的文件名", page=self.page)
            return
        with open(filename, 'wb') as output:
            for file in input_files:
                try:
                    with open(file, 'rb') as file:
                        chunk = file.read()
                    # 将数据写入合并文件
                    output.write(chunk)
                except FileNotFoundError:
                    pass

    def split_file(self, e):
        input_file = self.spliter_feild.value
        if input_file == "":
            Plug.run(plugins=("_notice",), data="请选择将要被分割的文件!!!", page=self.page)
            return
        chunk_size = self.single_size
        filename = os.path.basename(input_file)
        name, suffix = filename.split(".")
        with open(input_file, 'rb') as file:
            chunk_number = 1
            while True:
                # 读取指定大小的数据块
                chunk = file.read(chunk_size*1024*1024)
                if not chunk:
                    Plug.run(plugins=("_notice",), data="分割完成", page=self.page)
                    break  
                # 构建输出文件名
                output_file = f"{os.path.dirname(input_file)+os.path.sep+name}_part{chunk_number}.{suffix}"
                # 将数据块写入新文件
                with open(output_file, 'wb') as output:
                    output.write(chunk)
                chunk_number += 1