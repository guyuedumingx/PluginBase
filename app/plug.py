import flet as ft
import pypinyin 
import inspect
from fastapi import FastAPI

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
            cls.PLUGINS.update({plugin_name:cls._build(plugin_name, plugin)})
            return plugin
        return wrapper
    
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
    def getPlugin(cls, plugin_name):
        return cls.PLUGINS[plugin_name]
    

class Plugin(object):
    ICON = ft.icons.SETTINGS
    AUTHOR = "YOHOYES"
    VERSION = "1.0.0"
    MATCHS = []
    def process(self, data, **kwargs):
        return data

class UIPlugin(Plugin, ft.UserControl):
    """
    THIS IS A UI PLUGIN
    """
    def process(self, data, **kwargs):
        return ft.Text(data)