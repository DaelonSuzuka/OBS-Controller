from qtstrap import *
from pathlib import Path
import json
import importlib
import sys
import os
from codex import SerialDevice
import codex
import zipimport


plugin_folder = OPTIONS.APPLICATION_PATH / 'plugins'


class _Plugins:
    _plugins = {}

    def __init__(self):
        def is_plugin(p):
            return Path(Path(p) / 'plugin.json').exists() or Path(Path(p) / '__init__.py').exists()

        plugins = [Path(d[0]) for d in os.walk(plugin_folder) if is_plugin(d[0])]
        for plugin in plugins:
            self.load_loose_plugin(plugin)

        for plugin in plugin_folder.rglob('*.zip'):
            self.load_zip_plugin(plugin)

    def list_all(self):
        return self._plugins

    def __getattr__(self, name):
        return self._plugins[name]
    
    def __contains__(self, key):
        return key in self._plugins

    def load_zip_plugin(self, plugin):
        plugin_name = plugin.relative_to(OPTIONS.APPLICATION_PATH).as_posix()
        plugin_name = plugin_name.replace('/','.')
        plugin_name = plugin_name[:-len('.zip')]

        if plugin_name not in self._plugins:
            sys.path.append(plugin)
            
            module = importlib.import_module(plugin_name)
            self._plugins[plugin_name] = module

    def load_loose_plugin(self, plugin):
        plugin_name = plugin.relative_to(OPTIONS.APPLICATION_PATH).as_posix()
        plugin_name = plugin_name.replace('/','.')

        if plugin_name not in self._plugins:
            module = importlib.import_module(plugin_name)
            self._plugins[plugin_name] = module


plugins = None


def Plugins():
    global plugins
    if plugins is None:
        plugins = _Plugins()
    return plugins


Plugins()