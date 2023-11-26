import os
from app.plug import *  
import flet as ft
from functools import partial
from app.build_in import *


plugin_dir = os.sep.join([os.curdir,"app", "plugins"])
ENV['plugin_dir'] = os.path.abspath(plugin_dir)
ENV['update_dir'] = os.path.abspath(os.sep.join([os.curdir, "app"]))
ENV['app_dir'] = os.path.abspath(os.curdir)

db = PlugManager.run(plugins=("_setDB",), data="sqlite:///plug.db")
PlugManager.run(plugins=("_preload_plugin",), data="load plugins success")


def main(page: ft.Page):
    search_feild = ft.TextField(hint_text="Search Plugins", border_radius=40)
    search_btn = ft.Container(
            ft.Icon(name=ft.icons.SEARCH),
            col={"xs":2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
        )
    container = ft.Container(PlugManager.run(plugins=("_mainshow",),data=""),expand=1)
    func = partial(PlugManager.run, 
                   page=page,
                   container=container,
                   search_btn=search_btn,
                   search_feild=search_feild)

    def load_plugin(e):
        plugin_name = e.control.title.value
        container.content = func(plugins=("_load_plugin",),
                                 data=plugin_name,
                                 search=search)
        container.update()
        search_feild.update()
        page.update()
    
    def back_to_home(e):
        container.content = PlugManager.run(plugins=("_exit_plugin",),data="",
                        search_feild=search_feild,
                        search_btn=search_btn,
                        search=search)
        search_feild.value = ""
        container.update()
        search_feild.update()
        search_btn.update()
        page.update()

    def search(e):
        container.content = func(plugins=("_plugin_search_stream",),
                                 data=search_feild.value,
                                 search=search,
                                 item_on_click=load_plugin)
        search_feild.focus()
        search_feild.update()
        page.update()

    page.add(ft.ResponsiveRow([
        ft.Container(
            ft.Icon(name=ft.icons.HOME),
            col={"xs":2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
            on_click=back_to_home,
        ),
        ft.Container(
            search_feild, 
            padding=5,
            col={"xs":8, "sm": 10, "md": 10, "xl": 10},
        ),
        search_btn
    ]))
    page.add(container)
    search_feild.on_change = search
    search_feild.focus()
    

# ft.app(target=main, view=ft.AppView.WEB_BROWSER)
ft.app(target=main)
