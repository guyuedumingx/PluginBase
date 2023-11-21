import importlib
import os
from app.plug import *  

plugin_dir = os.sep.join([os.curdir,"app", "plugins"])

def load_plugins(plugin_dir):
    """
    load all module files in the app/plugins
    """
    plugins_files = os.listdir(plugin_dir)
    for files in plugins_files:
        plug_path = plugin_dir + os.sep + files.split(".")[0]
        import_path = os.path.relpath(plug_path, os.path.curdir).replace(os.sep, ".")
        plug = importlib.import_module(import_path, package="app")


load_plugins(plugin_dir)
processor = PlugManager()
print(processor.PLUGINS)
processed = processor.run(plugins=("plugin2",), data="##Foo--bar**", google="mian")
print(processed)