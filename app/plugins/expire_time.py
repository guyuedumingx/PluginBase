from app.plug import *
import datetime

@Plug.register('计算签证到期日')
class CleanMarkdownItalic(UIPlugin):
    """
    计算签证到期日
    """
    ICON = ft.icons.DATE_RANGE_OUTLINED
    time_format = "%y%m%d"
    VERSION="1.2.0"
    def process(self, data, page, search_feild: ft.TextField, **kwargs):
        def pick_time(e):
            start_time.value = date_picker.value.strftime(self.time_format)
            recale(e)

        def recale(e):
            date_str = start_time.value
            year = '20' + date_str[:2]  # 取前两位作为年份
            month = date_str[2:4]       # 取第三和第四位作为月份
            day = date_str[4:]          # 取最后两位作为日期
            try:
                v = datetime.datetime(year=int(year), month=int(month), day=int(
                    day)) + datetime.timedelta(days=int(day_feild.value))
                result.value = v.strftime("%Y-%m-%d")
                page.update()
            except:
                pass

        date_picker = ft.DatePicker(
            on_change=pick_time,
            first_date=datetime.datetime.now()
        )
        start_time = search_feild
        start_time.label = "开始日期"
        start_time.on_change = recale
        start_time.input_filter=ft.NumbersOnlyInputFilter()
        # start_time.value = datetime.datetime.now().strftime(self.time_format)
        start_time.value = ""
        start_time.suffix_text = "YEAR-MONTH-DAY"
        day_feild = ft.TextField(
            label="可停留天数", on_change=recale, suffix_text="DAYS")

        def btn_click(e):
            day_feild.value = e.control.text
            recale(e)
        btn_list = [ft.OutlinedButton(i, on_click=btn_click, col={"md": 2}) for i in [
            30, 45, 60, 90, 120, 180]]

        day_feild.value = 30
        result = ft.Text(weight=ft.FontWeight.BOLD,
                         size=100, color=ft.colors.GREY_600)

        page.overlay.append(date_picker)

        date_button = ft.ElevatedButton(
            "选择日期",
            icon=ft.icons.CALENDAR_MONTH,
            on_click=lambda _: date_picker.pick_date(),
        )
        return ft.ListView(
            [date_button, day_feild, ft.ResponsiveRow(btn_list),
             ft.Container(result,
                          alignment=ft.alignment.center,
                          expand=1,
                          padding=20)], expand=1, spacing=20)
