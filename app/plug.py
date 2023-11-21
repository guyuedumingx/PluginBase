
class PlugManager(object):
    """
    插件管理器
    """
    PLUGINS = {}

    def run(self, plugins=(), data="", **kwargs):
        for plugin_name in plugins:
            data = self._run(plugin_name, data, **kwargs)
        return data
    
    def _run(self, plugin_name: str, data, **kwargs):
        plug = self.PLUGINS[plugin_name]()
        if hasattr(plug, 'process_list'):
            process_list = plug.process_list()
            for p_name in process_list:
                data = self._run_plugin(p_name, data, **kwargs)
        elif hasattr(plug, 'process'):
            data = plug.process(data, **kwargs)
        return data 

    @classmethod
    def register(cls, plugin_name):
        def wrapper(plugin):
            cls.PLUGINS.update({plugin_name:plugin})
            return plugin
        return wrapper
    

