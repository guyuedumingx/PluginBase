import os
from app.plug import *
import flet as ft
import dataset

# 配置日志
logging.basicConfig(filename='plug.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 创建一个将控制台输出写入到日志的处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建一个格式化器，并将其添加到处理器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 获取默认的根日志记录器，并将处理器添加到其中
root_logger = logging.getLogger()
root_logger.addHandler(console_handler)

curdir = os.curdir
plugin_dir = os.sep.join([curdir, "app", "plugins"])
ENV['plugin_dir'] = os.path.abspath(plugin_dir)
ENV['update_dir'] = os.path.abspath(os.sep.join([curdir, "app"]))
ENV['app_dir'] = os.path.abspath(curdir)

# https://dataset.readthedocs.io/en/latest/
url = "///".join(["sqlite:", "plug.db"])
db = dataset.connect(url)
Plug.setState(db=db)

Plug.run(plugins=("_preload_plugin",), data=ENV['plugin_dir'])

# ft.app(target=lambda page:PlugManager.run(plugins=("_index",), data=page, view=ft.AppView.WEB_BROWSER))
ft.app(target=lambda page: Plug.run(plugins=("_index",), data=page), assets_dir="assets")
