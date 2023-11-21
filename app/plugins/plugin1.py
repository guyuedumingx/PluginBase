from ..plug import PlugManager

@PlugManager.register('plugin1')
class CleanMarkdownItalic(object):
    def process(self, text, **kwargs):
        return text.replace('--', '')

