from ..plug import *
import flet as ft
import datetime

@PlugManager.register('cal_date')
@PlugManager.register('签证到期日')
class CleanMarkdownItalic(object):
    def process(self, key_word, container, page, **kwargs):
        def pick_time(e):
            start_time.value = date_picker.value.strftime("%Y/%m/%d")
            recale(e)

        def recale(e):
            year,month,day = start_time.value.split("/")
            v = datetime.datetime(year=int(year),month=int(month),day=int(day)) + datetime.timedelta(days=int(day_feild.value))
            result.value = v.strftime("%Y-%m-%d")
            page.update()

        date_picker = ft.DatePicker(
            on_change=pick_time,
            first_date=datetime.datetime(2023, 10, 1)
        )
        start_time = ft.TextField(label="初始日期",on_change=recale)
        day_feild = ft.TextField(label="可停留天数", on_change=recale)
        day_feild.value = 30
        result = ft.Text(weight=ft.FontWeight.BOLD, size=100, color=ft.colors.GREY_600)

        page.overlay.append(date_picker)

        date_button = ft.ElevatedButton(
            "选择日期",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: date_picker.pick_date(),
        )
        container.content = ft.ResponsiveRow(
            [date_button, start_time, day_feild, 
            ft.Container(result,
                         alignment=ft.alignment.center,
                         expand=1,
                         padding=20)],
            alignment=ft.alignment.bottom_center,
            run_spacing=20,
        )
        page.update()
        return key_word
    
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
        return ('_search_plugin', 'prt')
    