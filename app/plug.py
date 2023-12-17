import flet as ft
import pypinyin 
import inspect
from fastapi import FastAPI
import logging
import os
import importlib
from functools import partial

app = FastAPI()
"""
a global environment
"""
ENV = {
    'initial_plugin_subtitle': "THIS IS A USEFUL PLUGIN"
}

class Plug(object):
    """
    插件管理器
    PLUGINS: plugin list
    ENV: a global environment
    """
    PLUGINS = {}
    context = {}

    @classmethod
    def run(icls, plugins: tuple, data="", **kwargs):
        try:
            for plugin_name in plugins:
                plugin = icls.PLUGINS[plugin_name]
                data = icls._run_plugin(plugin, data, **{**icls.context, **kwargs})
            return data
        except Exception as e:
            print(e)
            logging.error(e, exc_info=True)
    
    @classmethod
    def _run_plugin(cls, plugin, data, **kwargs):
        """
        run single plugin
        """
        return plugin.process(data, **kwargs)

    @classmethod
    def register(cls, plugin_name):
        def wrapper(plugin):
            if plugin_name in cls.PLUGINS:
                current_version = cls.PLUGINS[plugin_name].VERSION
                new_version = plugin.VERSION
                if cls.compare_versions(new_version, current_version) >= 0:
                    cls._build(plugin_name, plugin)
            else:
                    cls._build(plugin_name, plugin)
            return plugin
        return wrapper
    
    @classmethod
    def compare_versions(cls, version1, version2):
        # 实际的版本号比较可能会更加复杂，这里简化为字符串比较
        return int(version1.replace('.', '')) - int(version2.replace('.', ''))
    
    @classmethod
    def _build(cls, plugin_name: str, plugin):
        first_letters = "".join(pypinyin.lazy_pinyin(plugin_name, pypinyin.Style.FIRST_LETTER)).lower()
        full_pinyin = "".join(pypinyin.lazy_pinyin(plugin_name)).lower()
        matchs=[plugin_name.lower(), first_letters, full_pinyin]
        plugin.MATCHS = list(set([*matchs, *plugin.MATCHS]))
        try:
            plugin.SOURCEFILE = inspect.getsourcefile(plugin)
            plugin.SOURCE = inspect.getsourcelines(plugin)[0]
            desc = inspect.getdoc(plugin)
        except:
            plugin.SOURCEFILE = ""
            plugin.SOURCE = ""
            desc = ENV['initial_plugin_subtitle']
        plugin.DESC = ENV['initial_plugin_subtitle'] if desc == None else desc
        cls.PLUGINS.update({plugin_name:plugin()})
    
    @classmethod
    def setState(cls, **kwargs):
        cls.context = {**cls.context, **kwargs}

    @classmethod
    def getState(cls, name):
        return cls.context[name]
        
    @classmethod
    def getPlugin(cls, plugin_name):
        return cls.PLUGINS[plugin_name]
    
    @classmethod
    def getPluginDetail(cls, plugin_name):
        db = cls.getState('db')
        table = db.get_table('plugins', primary_id='name')
        return table.find_one(plugin_name)

class Plugin(object):
    ICON = ft.icons.SETTINGS
    AUTHOR = "YOHOYES"
    VERSION = "1.0.0"
    AUTHORITY = "ALL"
    MATCHS = []
    def process(self, data, **kwargs):
        return data

class UIPlugin(Plugin, ft.UserControl):
    """
    THIS IS A UI UIPLUGIN
    
    只要涉及UI的更新，都应该继承这个class
    """
    def process(self, data, **kwargs):
        return ft.Text(data)


@Plug.register('_preload_plugin')
class PreLoadPlugin(Plugin):
    """
    Load all modules
    加载插件库中的所有插件
    """
    def process(self, data, **kwargs):
        if not os.path.exists(data):
            os.makedirs(data)
        self._load("", path=data)
        return f"LOAD COMPLETE!!!"
    
    def _load(self, f, path):
        full_path = path+os.sep+f
        if os.path.isdir(full_path):
            files = os.listdir(full_path)
            files.sort()
            for item in files: 
                self._load(item, full_path)
        elif os.path.isfile(full_path) and f.endswith(".py"):
            loader = importlib.machinery.SourceFileLoader(
                f.split(".")[0], full_path)
            loader.load_module()

