from app.plug import *
import shutil

@PlugManager.register('安装插件')
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
                    PlugManager.run(
                        plugins=("_preload_plugin", "_notice"), data=plugin_dir, page=page, **kwargs)
                except Exception as e:
                    PlugManager.run(plugins=("_notice",),
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

@PlugManager.register('环境信息')
class ENVInformation(UIPlugin):
    """
    查看ENV中的所有信息
    """
    ICON = ft.icons.MISCELLANEOUS_SERVICES

    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_dictUI",), data=ENV, mode="show", **kwargs)


@PlugManager.register('重新加载')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    ICON=ft.icons.REFRESH
    def process(self, data, **kwargs):
        return PlugManager.run(plugins=("_preload_plugin",),data=ENV['plugin_dir'])
    

@PlugManager.register('_load_plugin')
class BasePluginView(UIPlugin):
    def process(self, plugin_name, page, **kwargs):
        self.plugin_name = plugin_name
        self.plugin = PlugManager.getPlugin(plugin_name)
        self.page = page
        home_btn, search_feild, tips_btn = self.base_ui(
            page, plugin_name, self.plugin.ICON)
        self.container = PlugManager.run(plugins=("_defaultbackground",))
        plugin = PlugManager.getPlugin(plugin_name)
        func = partial(
            PlugManager.run,
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

    def search_feild_onchange(self, e):
        self.page.views.pop() and self.page.update()
        PlugManager.getPlugin("_index").search_func(e)

    def base_ui(self, page, plugin_name, icon=ft.icons.SETTINGS):
        home_btn = ft.Container(
            ft.Icon(name=ft.icons.HOME),
            col={"xs": 2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
            on_click=lambda _: page.views.pop() and page.update()
        )
        search_feild = ft.TextField(
            hint_text=plugin_name,
            prefix_icon=icon,
            border_radius=40,
            col={"xs": 10, "sm": 11, "md": 11, "xl": 11},
            on_change=self.search_feild_onchange
        )
        tips_btn = ft.FloatingActionButton(icon=ft.icons.TIPS_AND_UPDATES,
                scale=0.7,
                opacity=0.5,
                bgcolor=ft.colors.WHITE,
                shape=ft.CircleBorder(),
                on_click= lambda _: PlugManager.run(
                    plugins=("_tipsview","_tips_backbtn"),
                    data=self.plugin_name,
                    plugin_obj=self.plugin,
                    page=self.page
                    )
                )
        return (home_btn, search_feild, tips_btn)
