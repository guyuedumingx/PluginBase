import flet as ft
import pypinyin 
import inspect

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

    @classmethod
    def run(icls, plugins=(), data="", **kwargs):
        for plugin_name in plugins:
            plugin = icls.PLUGINS[plugin_name]
            data = icls._run_plugin(plugin, data, **kwargs)
        return data
    
    @classmethod
    def _run_plugin(cls, plugin, data, **kwargs):
        """
        run single plugin
        """
        if hasattr(plugin, 'process_list'):
            process_list = plugin.process_list(data, **kwargs)
            for p_name in process_list:
                data = cls._run_plugin(cls.PLUGINS[p_name], data, **kwargs)
        elif hasattr(plugin, 'process'):
            data = plugin.process(data, **kwargs)
        return data 

    @classmethod
    def register(cls, plugin_name):
        def wrapper(plugin):
            first_letters = "".join(pypinyin.lazy_pinyin(plugin_name, pypinyin.Style.FIRST_LETTER)).lower()
            full_pinyin = "".join(pypinyin.lazy_pinyin(plugin_name)).lower()
            matchs=[plugin_name.lower(), first_letters, full_pinyin]
            plugin.MATCHS = [*list(set(matchs)), plugin.MATCHS]
            desc = inspect.getdoc(plugin)
            plugin.DESC = ENV['initial_plugin_subtitle'] if desc == None  else desc
            cls.PLUGINS.update({plugin_name:plugin()})
            return plugin
        return wrapper
    
class Plugin(object):
    ICON = ft.icons.SETTINGS
    MATCHS = []
    def process(self, data, **kwargs):
        return data

class UIPlugin(Plugin):
    pass