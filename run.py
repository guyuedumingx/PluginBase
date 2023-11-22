import importlib
import os
from app.plug import *  
import dataset
import flet as ft
from time import sleep
import functools
from functools import partial

plugin_dir = os.sep.join([os.curdir,"app", "plugins"])

# provide a global db
db_name = "sqlite:///plug.db"
ENV['db'] = dataset.connect(db_name)

def load_plugins(plugin_dir):
    """
    load all module files in the app/plugins
    """
    plugins_files = os.listdir(plugin_dir)
    for files in plugins_files:
        plug_path = plugin_dir + os.sep + files.split(".")[0]
        import_path = os.path.relpath(plug_path, os.path.curdir).replace(os.sep, ".")
        plug = importlib.import_module(import_path, package="app")

load_plugins(plugin_dir)

processor = PlugManager()
ENV['processor'] = processor

def main(page):
    key_word = ft.TextField(hint_text="Search Plugins")
    container = ft.Container(expand=1)

    def item_on_click(e):
        plugin_name = e.control.content.controls[0].title.value
        processor.run(plugins=(plugin_name,), 
                      data=key_word.value,
                      page=page,
                      container=container)
        page.update()

    def search(e):
        processed = processor.run(plugins=("_search_plugin", "_build_show_cards"), 
                                item_on_click=item_on_click,
                                data=key_word.value,
                                page=page,
                                container=container)
        container.content = list_ui(processed)
        # key_word.value = ""
        key_word.focus()
        key_word.update()
        page.update()

    page.add(ft.ResponsiveRow([
        ft.Container(
            ft.Icon(name=ft.icons.SEARCH),
            col={"xs":2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
            on_click=search,
        ),
        ft.Container(
            key_word, 
            padding=5,
            col={"xs":10, "sm": 11, "md": 11, "xl": 11},
        ),
    ]))
    page.add(container)
    key_word.on_change = search
    key_word.focus()

ft.app(target=main)