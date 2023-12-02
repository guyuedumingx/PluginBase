import os
from app.plug import *
import flet as ft
from app.build_in import *

# import numpy
# import pandas
# import requests
# import openpyxl

# curdir = os.path.dirname(__file__)
curdir = os.curdir
plugin_dir = os.sep.join([curdir, "app", "plugins"])
ENV['plugin_dir'] = os.path.abspath(plugin_dir)
ENV['update_dir'] = os.path.abspath(os.sep.join([curdir, "app"]))
ENV['app_dir'] = os.path.abspath(curdir)
ENV['app_host'] = '0.0.0.0'
ENV['app_port'] = 36909

# https://dataset.readthedocs.io/en/latest/
url = "///".join(["sqlite:", "plug.db"])
db = dataset.connect(url)
PlugManager.setState(db=db)

PlugManager.run(plugins=("_preload_plugin",), data=ENV['plugin_dir'])

# ft.app(target=lambda page:PlugManager.run(plugins=("_index",), data=page, view=ft.AppView.WEB_BROWSER))
ft.app(target=lambda page: PlugManager.run(plugins=("_index",), data=page), assets_dir="assets")
