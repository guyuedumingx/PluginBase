from app.plug import *
import flet as ft
from functools import partial
import requests


@Plug.register('_search_plugin')
class SearchPlugin(Plugin):
    """
    data: word: the search key word
    """
    def process(self, word, show_build_in=False, show_no_source=True, **kwargs):
        plugins = Plug.PLUGINS
        func = partial(self.match_rules, word=word, show_build_in=show_build_in, show_no_source=show_no_source)
        return dict(filter(lambda x: func(x=x), plugins.items()))

    def match_rules(self, word, x, show_build_in=False, show_no_source=True):
        name, plug = x[0], x[1]
        if (not show_build_in and name.startswith("_")):
            return False
        if not show_no_source and not plug.HAS_SOURCE:
            return False
        matchs = plug.MATCHS
        for item in matchs:
            if (word in item):
                return True


@Plug.register('_plugin_cards')
class BuildShowCards(Plugin):
    def process(self, data: dict, plugin_onclick: lambda e: e, **kwargs):
        tile_lst = [ft.ListTile(
                leading=ft.Icon(item[1].ICON),
                title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                subtitle=ft.Text(
                    item[1].DESC.strip().split("\n")[0]
                ),
                on_click=plugin_onclick,
                ) for item in data.items()]
        return tile_lst


@Plug.register('_plugin_search_stream')
class PluginSearchStream(UIPlugin):
    """
    主页搜索插件流
    data: word: the search key word
    """
    def process(self, key_word, plugin_onclick, **kwargs):
        return Plug.run(plugins=("_search_plugin", "_plugin_cards", "_flowUI"),
                               data=key_word,
                               plugin_onclick=plugin_onclick,
                               **kwargs)


@Plug.register('_mainbackground')
class MainShowBackground(UIPlugin):
    """
    显示在主页的初始背景
    """
    def process(self, data, **kwargs):
        return Plug.run(plugins=("_plugin_search_stream",),
                               data=data,
                               plugin_onclick=Plug.get_plugin("_index").load_plugin)


@Plug.register('_defaultbackground')
class DefaultBackground(UIPlugin):
    """
    默认背景
    """
    def process(self, data, **kwargs):
        return ft.Container(content=ft.Icon(
            ft.icons.SETTINGS,
            size=300,
            color=ft.colors.GREY_200),
            expand=1,
            alignment=ft.alignment.center)


@Plug.register('_tipsview')
class TipsView(UIPlugin):
    def process(self, data, plugin_obj, **kwargs):
        ui = [
            ft.Text(data, size=30),
            ft.Text(plugin_obj.VERSION),
            ft.Markdown(plugin_obj.DESC,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB),
            ft.Text("SOURCE", size=30),
            ft.Text("".join(plugin_obj.SOURCE), size=15)
        ]
        return ft.ListView(ui, expand=1, spacing=10)


@Plug.register('_index')
class IndexPlugin(UIPlugin):
    """
    首页插件：项目起始页
    page: the page to load in
    search_feild: the search area showed in all page
    container: the main container that developer can change and also
               the main area to show all information of the plugin
    """
    ICON = ft.icons.SEARCH
    HINT_TEXT = "Search Plugins"
    def process(self, page: ft.Page, **kwargs):
        # 页面的宽高字体
        page.window_height = 600
        page.window_width = 800 
        page.title = "插件工具箱"
        page.fonts = {
            "LXGWWenKai-Regular": "fonts/LXGWWenKai-Regular.ttf",
        }

        theme_color = "blue"
        if '主题颜色' in ENV:
            theme_color = ENV['主题颜色']
        page.theme = ft.Theme(font_family="LXGWWenKai-Regular", color_scheme_seed=theme_color)
        self.page = page
        self.search_feild = ft.TextField(
            hint_text=self.HINT_TEXT,
            prefix_icon=self.ICON,
            border_radius=32,
            scale=ft.Scale(scale_x=1.0, scale_y=0.85),
            text_size=18,
            on_change=self.search_func
        )
        self.state = ft.CircleAvatar(bgcolor=ft.colors.YELLOW, radius=5)
        image_src = ENV['头像'] if "头像" in ENV else "assets/icons/BOC.svg"
        self.avatar = ft.Stack(
            [
                ft.CircleAvatar(
                    # foreground_image_url="https://avatars.githubusercontent.com/u/5041459?s=88&v=4"
                    content=ft.Image(src=image_src, width=30, height=30, fit=ft.ImageFit.CONTAIN),
                    bgcolor=ft.colors.with_opacity(0.5, ft.colors.GREY_50),
                ),
                ft.Container(
                    content=self.state,
                    alignment=ft.alignment.bottom_left,
                ),
            ],
            width=40,
            height=40,
            scale=1.2
        )
        self.container = ft.Container(Plug.run(plugins=("_plugin_search_stream",),
                                                      plugin_onclick=self.load_plugin), expand=1)
        self.page.add(
            ft.ResponsiveRow([
                ft.Container(self.search_feild, padding=5,col={"xs":11}),
                ft.Container(
                    self.avatar,
                    on_click=lambda x: Plug.run(plugins=("_load_plugin",), data="_person_info", page=self.page),
                    col={"xs":1}
                )],
                vertical_alignment=ft.CrossAxisAlignment.CENTER),
            self.container
        )
        self.search_feild.focus()
        self.page.on_keyboard_event = self.keyboard_event
        self.page.update()
        Plug.run(plugins=("_on_load_index_success",), page=self.page)
        self.login_and_start_server(state=self.state)
        return page
    
    def login_and_start_server(self, state):
        Plug.run(plugins=("_login","_server"), state=state, page=self.page, port=36908, host="0.0.0.0")
    
    def logout(self, e: ft.ControlEvent):
        ehr = ENV['EHR']
        requests.post(f"http://{ENV['server_addr']}:{ENV['server_port']}/logout?ehr={ehr}")

    def keyboard_event(self, e:ft.KeyboardEvent):
        pass
        # keys = set(e.key.lower())
        # if e.shift:         # shift
        #     keys.add("shift") 
        # if e.meta:          # command
        #     keys.add("meta")        
        # if e.ctrl:          # control
        #     keys.add("ctrl")
        # if e.alt:           # alt/option
        #     keys.add("alt")
        # plugin = dict(filter(lambda x: set(x[0].lower().split("+")) == keys, Plug.KEYBOARDS.items()))
        # if plugin != {}:
        #     self.search_feild.value = ""
        #     self.search_feild.update()
        #     Plug.run(plugins=("_load_plugin",),
        #             data=list(plugin.values())[0], page=self.page)

    def load_plugin(self, e):
        plugin_name = e.control.title.value
        Plug.run(plugins=("_load_plugin",),
                        data=plugin_name, page=self.page)

    def search_func(self, e):
        self.search_feild.value = e.data
        self.container.content = Plug.run(
            plugins=("_plugin_search_stream",),
            plugin_onclick=self.load_plugin,
            data=e.data)
        self.search_feild.focus()
        self.page.update()
        return True


@Plug.register("_on_load_index_success")
class OnLoadIndexSuccess(Plugin):
    """
    主页面加载成功后调用这个插件
    """
    def process(self, data, **kwargs):
        return super().process(data, **kwargs)
