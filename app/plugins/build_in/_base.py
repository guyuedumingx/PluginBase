from app.plug import *
import shutil

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
                    Plug.run(plugins=("_notice",),
                                    data=e, page=page, **kwargs)

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
        return Plug.run(plugins=("_dictUI",), data=ENV, mode="show", **kwargs)


@Plug.register('重新加载')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    ICON=ft.icons.REFRESH
    def process(self, data, **kwargs):
        return Plug.run(plugins=("_preload_plugin",),data=ENV['plugin_dir'])
    

@Plug.register('_load_plugin')
class BasePluginView(UIPlugin):
    """
    加载某个指定的插件
    plugin_name: 要加载的插件名
    page: ft.Page
    """
    def process(self, plugin_name, page, **kwargs):
        self.plugin_name = plugin_name
        self.plugin = Plug.getPlugin(plugin_name)
        self.page = page
        home_btn, search_feild, self.container, tips_btn = Plug.run(plugins=("_plugin_baseUI",),page=page,data=plugin_name)
        plugin = Plug.getPlugin(plugin_name)
        func = partial(
            Plug.run,
            search_feild=search_feild,
            page=page,
            container=self.container,
            tips_btn=tips_btn,
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
                    ft.ResponsiveRow([search_feild, home_btn]),
                    tips_btn,
                    self.container
                ]
            )
        )
        page.go("/"+plugin_name)
        page.update()
        self.container.content = func(plugins=(plugin_name,)) 
        search_feild.focus()
        page.update()
        return plugin_name
