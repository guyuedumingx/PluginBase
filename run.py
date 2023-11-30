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
PlugManager.run(plugins=("_preload_plugin",), data=ENV['plugin_dir'])


# ft.app(target=lambda page:PlugManager.run(plugins=("_index",), data=page, view=ft.AppView.WEB_BROWSER))
ft.app(target=lambda page:PlugManager.run(plugins=("_index",), data=page))
