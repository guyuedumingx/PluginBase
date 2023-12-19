import flet as ft
import dataset
import pypinyin 
import inspect
import json
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
    PLUGINS: plugin list 全局的所有插件都会被统一注册到这里进行管理{plugin_name: plugin()}
    ENVS: 环境堆栈，每一次到用run函数都会生成一个新栈帧，存储调用过程除data外的所有参数
    context: 统一上下文，用于植入全局对象到plugins的执行过程中
    """
    PLUGINS = {}
    context = {}
    ENVS = []

    @classmethod
    def run(icls, plugins: tuple, data="", **kwargs):
        try:
            icls.ENVS.append(kwargs)
            for plugin_name in plugins:
                plugin = icls.PLUGINS[plugin_name]
                data = icls._run_plugin(plugin, data, **{**icls.context, **icls.ENVS[-1]})
            icls.ENVS.pop()
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

    """
    插件注册入口装饰器，当某个对象使用该装饰器时，表示该对象是一个插件，其中传入的参数表示
    注册的全局插件名，如果该插件名存在于当前环境中，则对比环境中的插件版本号和需要注册的插件
    版本号，只有版本号>=当前环境中该插件的版本号才会被重新导入
    """
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
    
    """
    注册构建函数，主要用于构建插件注册后续需要使用的关键字列表
    支持首字母，全拼音，原单词匹配插件
    """
    @classmethod
    def _build(cls, plugin_name: str, plugin):
        first_letters = "".join(pypinyin.lazy_pinyin(plugin_name, pypinyin.Style.FIRST_LETTER)).lower()
        full_pinyin = "".join(pypinyin.lazy_pinyin(plugin_name)).lower()
        matchs=[plugin_name.lower(), first_letters, full_pinyin]
        plugin.MATCHS = list(set([*matchs, *plugin.MATCHS]))
        plugin.NAME = plugin_name
        try:
            plugin.SOURCEFILE = inspect.getsourcefile(plugin)
            plugin.SOURCE = inspect.getsourcelines(plugin)[0]
            plugin.HAS_SOURCE = True
            desc = inspect.getdoc(plugin)
        except:
            plugin.SOURCEFILE = ""
            plugin.SOURCE = ""
            plugin.HAS_SOURCE = False
            desc = ENV['initial_plugin_subtitle']
        plugin.DESC = ENV['initial_plugin_subtitle'] if desc == None else desc
        plugin_obj = plugin()
        plugin_obj.on_register(**cls.context)
        cls.PLUGINS.update({plugin_name: plugin_obj})
    
    @classmethod
    def set_state(cls, **kwargs):
        cls.context = {**cls.context, **kwargs}

    @classmethod
    def get_state(cls, name):
        return cls.context[name]
        
    @classmethod
    def get_plugin(cls, plugin_name):
        return cls.PLUGINS[plugin_name]
    
    """
    每次调用Plug.run都会使得ENVS产生新的环境栈帧，如果需要在同一次run的不同plugins
    之间传递额外的参数，则可以使用add_args函数把需要传递的参数植入ENVS中，后续的plugins
    执行过程会得到该参数
    """
    @classmethod
    def add_args(cls, args:dict):
        cls.ENVS[-1].update(args)
    
    @classmethod
    def get_plugin_detail(cls, plugin_name):
        db = cls.get_state('db')
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
    
    """
    #TODO
    only run when a plugin be installed
    """
    def on_install(self, **kwargs):
        pass
    
    """
    #TODO
    only run when a plugin be uninstalled
    """
    def on_uninstall(self, **kwargs):
        pass
    
    """
    only run when a plugin be register
    """
    def on_register(self, **kwargs):
        pass
    
    """
    only run when a plugin be load
    """
    def on_load(self, **kwargs):
        pass
    
    """
    only run when a plugin be exit
    """
    def on_exit(self, **kwargs):
        pass


class UIPlugin(Plugin, ft.UserControl):
    """
    THIS IS A UI UIPLUGIN
    
    只要涉及UI的更新，都应该继承这个class
    """
    def process(self, data, **kwargs):
        return ft.Text(data)


@Plug.register("_load_config")
class LoadConfig(Plugin):
    def process(self, data, **kwargs):
        with open(data, "r") as f:
            config = json.loads(f.read())
            ENV.update(config)
        db = dataset.connect(ENV['db_url'])
        Plug.set_state(db=db)
        return ENV['plugin_dir']
            

@Plug.register('_preload_plugin')
class PreLoadPlugin(Plugin):
    """
    Load all modules
    加载插件库中的所有插件
    file: 指定加载的文件
    data: 路径，不包含文件名
    """
    def process(self, data, file="", **kwargs):
        if not os.path.exists(data):
            os.makedirs(data)
        self._load(file, path=data)
        return f"LOAD COMPLETE!!!"
    
    """
    f: 文件名
    path: 路径不包含文件名
    """
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

