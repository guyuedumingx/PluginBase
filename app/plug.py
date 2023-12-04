import flet as ft
import pypinyin 
import inspect
from fastapi import FastAPI
import logging
import os
import importlib

app = FastAPI()
"""
a global environment
"""
ENV = {
    'initial_plugin_subtitle': "THIS IS A USEFUL PLUGIN"
}

class PlugManager(object):
    """
    插件管理器
    PLUGINS: plugin list
    ENV: a global environment
    """
    PLUGINS = {}
    context = {}

    @classmethod
    def run(icls, plugins: tuple, data="", **kwargs):
        for plugin_name in plugins:
            plugin = icls.PLUGINS[plugin_name]
            data = icls._run_plugin(plugin, data, **{**icls.context, **kwargs})
        return data
    
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
                if cls.compare_versions(new_version, current_version) > 0:
                    cls.PLUGINS.update({plugin_name:cls._build(plugin_name, plugin)})
            else:
                    cls.PLUGINS.update({plugin_name:cls._build(plugin_name, plugin)})
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
        return plugin()
    
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


@PlugManager.register('_preload_plugin')
class PreLoadPlugin(Plugin):
    """
    Reload all module files in the app/plugins
    加载插件库中的所有插件
    """
    def process(self, data, **kwargs):
        if not os.path.exists(data):
            os.makedirs(data)
        plugins_files = os.listdir(data)
        plugins_files.sort()
        for files in plugins_files:
            if not files.endswith(".py"):
                continue
            loader = importlib.machinery.SourceFileLoader(
                files.split(".")[0], data+os.sep+files)
            loader.load_module()
        return f"LOAD SUCCESS!!!"
