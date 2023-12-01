import os
from app.plug import *
import flet as ft
from app.build_in import *

# curdir = os.path.dirname(__file__)
curdir = os.curdir
plugin_dir = os.sep.join([curdir, "app", "plugins"])
ENV['plugin_dir'] = os.path.abspath(plugin_dir)
ENV['update_dir'] = os.path.abspath(os.sep.join([curdir, "app"]))
ENV['app_dir'] = os.path.abspath(curdir)

# https://dataset.readthedocs.io/en/latest/
# db = PlugManager.run(plugins=("_setDB",), data=os.sep.join(
#     ["sqlite:", curdir, "plug.db"]))
url = "///".join(["sqlite:", "plug.db"])
db = PlugManager.run(plugins=("_setDB",), data=url)
PlugManager.run(plugins=("_preload_plugin",), data=ENV['plugin_dir'])


# ft.app(target=lambda page:PlugManager.run(plugins=("_index",), data=page, view=ft.AppView.WEB_BROWSER))
ft.app(target=lambda page: PlugManager.run(plugins=("_index",), data=page))
