from ..plug import *
import flet as ft
# import pandas
# import numpy

@PlugManager.register('prt')
class printToConsole(object):
    def process(self, text, **kwargs):
        print(text)
        return text

@PlugManager.register('_search_plugin')
class SearchPlugin(object):
    def process(self, word, **kwargs):
        plugins = PlugManager.PLUGINS
        return dict(filter(lambda x: x[0].startswith(word), plugins.items()))


@PlugManager.register('_build_show_cards')
class BuildShowCards(object):
    def process(self, plugin_dict, item_on_click, **kwargs):
        return [ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.ALBUM),
                            title=ft.Text(item[0], weight=ft.FontWeight.W_700),
                            subtitle=ft.Text(
                                "Music by Julie Gable. Lyrics by Sidney Stein."
                            ),
                        ),
                    ]
                ),
                padding=2,
                bgcolor=ft.colors.GREY_50,
                on_click=item_on_click
            )
        ) for item in plugin_dict.items()]
