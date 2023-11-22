from functools import wraps
import flet as ft

"""
a global environment
"""
ENV = {}

class PlugManager(object):
    """
    插件管理器
    PLUGINS: plugin list
    ENV: a global environment
    """
    PLUGINS = {}

    def run(self, plugins=(), data="", **kwargs):
        for plugin_name in plugins:
            plugin = self.PLUGINS[plugin_name]()
            data = self._run_plugin(plugin, data, **kwargs)
        return data
    
    def _run_plugin(self, plugin, data, **kwargs):
        """
        run single plugin
        """
        if hasattr(plugin, 'process_list'):
            process_list = plugin.process_list()
            for p_name in process_list:
                data = self._run_plugin(self.PLUGINS[p_name](), data, **kwargs)
        elif hasattr(plugin, 'process'):
            data = plugin.process(data, **kwargs)
        return data 

    @classmethod
    def register(cls, plugin_name):
        def wrapper(plugin):
            cls.PLUGINS.update({plugin_name:plugin})
            return plugin
        return wrapper
    


def to_list(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # fn.__annotations__['type'] = to_list.__name__
        print("before")
        data = fn(*args, **kwargs)
        print(data)
        print("after")
        return data
    return wrapper


def list_ui(data: list):
    lv =ft.ListView(expand=1)
    lv.controls = data
    return lv

def toc_ui(data: dict):
    pass