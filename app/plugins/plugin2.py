from ..plug import PlugManager

@PlugManager.register('plugin2')
class CleanMarkdownBolds(object):
    def process(self, text, **kwargs):
        return text.replace('**', '')

@PlugManager.register('plugin3')
class CleanMarkdownTitles(object):
    def process(self, text, **kwargs):
        return text.replace('##', '')

@PlugManager.register('plugin4')
class CleanMarkdownTitles(object):
    def process_list(self, **kwargs):
        return ('plugin3', 'plugin1')