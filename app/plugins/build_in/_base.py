from app.plug import *
import shutil
import requests

@Plug.register('安装插件')
class InstallPlugin(UIPlugin):
    """
    安装新插件
    """
    ICON = ft.icons.UPLOAD_FILE

    def process(self, data, page, **kwargs):

        def on_dialog_result(e: ft.FilePickerResultEvent):
            if e != None:
                success = []
                plugin_dir = ENV['plugin_dir']
                if not os.path.exists(plugin_dir):
                    os.makedirs(plugin_dir)
                try:
                    for f in e.files:
                        if not f.name.endswith(".py"):
                            continue
                        shutil.copyfile(f.path, plugin_dir+os.sep+f.name)
                        success.append(f)
                    Plug.run(
                        plugins=("_preload_plugin", "_notice"), data=plugin_dir, page=page, **kwargs)
                except Exception as e:
                    Plug.run(plugins=("_notice",), data=e, page=page, **kwargs)

        file_picker = ft.FilePicker(on_result=on_dialog_result)
        page.overlay.append(file_picker)
        page.update()
        return ft.Container(ft.Container(
            ft.Icon(name=ft.icons.UPLOAD_FILE,
                    size=250, color=ft.colors.GREY_400),
            on_click=lambda _: file_picker.pick_files(allow_multiple=True)),
            alignment=ft.alignment.center
        )


@Plug.register('环境信息')
class ENVInformation(UIPlugin):
    """
    查看ENV中的所有信息
    """
    ICON = ft.icons.MISCELLANEOUS_SERVICES

    def process(self, data, **kwargs):
        return Plug.run(plugins=("_pluginUI_with_search",),
                 data=ENV,
                 ui_template="_dictUI",
                 mode="edit",
                 key_icon=ft.icons.FIBER_MANUAL_RECORD_OUTLINED,
                 save_handler = self.save_handler,
                 **kwargs) 
    
    def save_handler(self, data):
        """
        保存函数
        """
        ENV.update(data)
        with open(ENV['config_file'], "w", encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
    
@Plug.register("_env_save")
class ENVSave(Plugin):
    def process(self, data, **kwargs):
        with open(ENV['config_file'], "w", encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False))
        return "Success"

@Plug.register('_person_info')
class PersonInformation(UIPlugin):
    """
    查看的所有信息
    """
    ICON = ft.icons.MISCELLANEOUS_SERVICES

    def process(self, data, page, container, **kwargs):
        self.page = page
        self.container = container
        name = "YOHOYES"
        ehr = ""
        avatar = "assets/icons/BOC.svg"
        theme_color = "blue"
        self.kwargs = kwargs
        if "姓名" in ENV:
            name = ENV['姓名']
        if "EHR" in ENV:
            ehr = ENV['EHR']
        if "头像" in ENV:
            avatar = ENV['头像']
        if "主题颜色" in ENV:
            theme_color = ENV['主题颜色']
        self.data = {
            "姓名": name,
            "EHR": ehr,
            "头像": avatar,
            "主题颜色": theme_color
        }
        return self.ui(avatar)

    def ui(self, avatar):
        avatar_ui = ft.Container(ft.CircleAvatar(
                content=ft.Image(src=avatar,
                                 border_radius=50,
                                 fit=ft.ImageFit.CONTAIN,),
                width=100,
                height=100,
                bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_50),
                ), on_click=self.choose_avatar)
        lst_ui = Plug.run(plugins=("_pluginUI_with_search",),
                 data=self.data,
                 ui_template="_dictUI",
                 mode="edit",
                 key_icon=ft.icons.FIBER_MANUAL_RECORD_OUTLINED,
                 save_handler = self.save_handler,
                 page=self.page,
                 container=self.container,
                 **self.kwargs) 
        return ft.ListView([avatar_ui, lst_ui], expand=1, spacing=10)
    
    def choose_avatar(self, e):
        def chosen(path):
            ENV['头像'] = path
            self.container.content = self.ui(path)
            self.container.update()
            Plug.run(plugins=("_env_save",), data=ENV)
        Plug.run(plugins=("_choose_file",), data=chosen, page=self.page)
    
    def save_handler(self, data):
        """
        保存函数
        """
        ENV.update(data)
        with open(ENV['config_file'], "w", encoding='utf-8') as f:
            f.write(json.dumps(ENV, ensure_ascii=False))
        Plug.run(plugins=("_notice",), data="保存成功", page=self.page)
    

@Plug.register('_back')
class Back(Plugin):
    def process(self, data, page, plugin_name, **kwargs):
        if(len(page.views) == 1):
            return
        if(len(page.views) == 2):
            Plug.get_plugin(plugin_name).on_exit(page=page, data=data, plugin_name=plugin_name, **kwargs)
        page.views.pop() and page.update()
        return super().process(data, page=page, **kwargs)


@Plug.register('重新加载')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    ICON=ft.icons.REFRESH
    def process(self, data, page: ft.Page, **kwargs):
        return Plug.run(plugins=("_preload_plugin",),data=ENV['plugin_dir'])
        # page.controls = []
        # return Plug.run(plugins=("_index",), data=page)


@Plug.register('_load_plugin')
class BasePluginView(UIPlugin):
    """
    加载某个指定的插件
    plugin_name: 要加载的插件名
    page: ft.Page
    """
    def process(self, plugin_name, page, **kwargs):
        self.plugin_name = plugin_name
        self.plugin = Plug.get_plugin(plugin_name)
        self.page = page
        back_btn, search_feild, process_bar, self.container, tips_btn = Plug.run(plugins=("_plugin_baseUI",),page=page,data=plugin_name)
        plugin = Plug.get_plugin(plugin_name)
        func = partial(
            Plug.run,
            search_feild=search_feild,
            page=page,
            container=self.container,
            tips_btn=tips_btn,
            process_bar=process_bar,
            back_btn = back_btn,
            data=plugin_name
            )

        self.plugin.on_load(
            page=page,
            plugin_name=plugin_name,
            search_feild=search_feild,
            container=self.container,
            tips_btn=tips_btn,
            back_btn = back_btn,
            data=plugin_name
            )

        # 如果这不是一个带UI的插件，直接把结果用_notice显示出来
        if(not isinstance(plugin, UIPlugin)):
            func(plugins=(plugin_name,"_notice"))
            page.update()
            return

        page.views.append(
            ft.View(
                "/" + plugin_name,
                [
                    ft.ResponsiveRow([search_feild, back_btn]),
                    process_bar,
                    tips_btn,
                    self.container
                ],
            )
        )
        page.go("/"+plugin_name)
        process_bar.visible = True
        page.update()
        self.container.content = func(plugins=(plugin_name,)) 
        search_feild.focus()
        process_bar.visible = False
        page.update()
        return plugin_name


@Plug.register("软件更新")
class UpdatePlugin(Plugin):
    """
    将软件更新到最新版本
    """
    ICON=ft.icons.ARROW_CIRCLE_UP_ROUNDED
    def process(self, data, page, server_addr=ENV['server_addr'], server_port=ENV['server_port'], **kwargs):
        self.url = f"http://{server_addr}:{server_port}/update"
        self.page = page
        resp = requests.get(self.url)
        if resp.status_code == 200:
            # 获取文件名
            content_disposition = resp.headers.get("Content-Disposition")
            if content_disposition and "filename" in content_disposition:
                filename = content_disposition.split("filename=")[1].strip('"')
            else:
                filename = "downloaded_plugin.zip"  # 默认文件名
            with open(filename, "wb") as f:
                f.write(resp.content)
            # 解压缩到 app 目录
            with open(filename, "rb") as zip_file:
                shutil.unpack_archive(zip_file.name, ENV['update_dir'], format="zip") 
        return "更新完成"
