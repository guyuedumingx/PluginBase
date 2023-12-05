from app.plug import *
from functools import partial

@PlugManager.register("_tips_backbtn")
class TipsViewWithBackButton(UIPlugin):
    def process(self, data, page, **kwargs):
        """
        data: should be a ft compoment
        """
        back_btn = ft.FloatingActionButton(icon=ft.icons.ARROW_BACK,
            scale=0.7,
            opacity=0.5,
            bgcolor=ft.colors.WHITE,
            shape=ft.CircleBorder(),
            on_click=lambda _: page.views.pop() and page.update()
            )
        url = page.views[-1].route + "/tips"
        page.views.append(ft.View(
            url,
            [back_btn, data]
        ))
        page.go(url)
        return data
    
@PlugManager.register('_notice')
class Notice(Plugin):
    def process(self, data, page: ft.Page, **kwargs):
        page.snack_bar = ft.SnackBar(ft.Text(data))
        page.snack_bar.open = True
        page.update()
        return data

@PlugManager.register('_banner')
class Banner(Plugin):
    def process(self, data, page: ft.Page, **kwargs):
        self.page = page 
        self.page.banner = ft.Banner(
            bgcolor=ft.colors.AMBER_100,
            leading=ft.Icon(ft.icons.WARNING_AMBER_ROUNDED, color=ft.colors.AMBER, size=40),
            content=ft.Text(data),
            actions=[
                ft.TextButton("关闭", on_click=self.close_banner),
            ],
        )
        self.page.banner.open = True
        self.page.update()
        return data
    
    def close_banner(self, e):
        self.page.banner.open = False
        self.page.update()

@PlugManager.register('_listUI')
class ListUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.ListView(controls=data, expand=1)


@PlugManager.register('_flowUI')
class FlowUI(UIPlugin):
    def process(self, data: list, counts_per_row=2, **kwargs):
        for item in data:
            item.col = {"sm": 12 / counts_per_row,
                        "xs": 12, "lg": 12 / (counts_per_row*2)}
        return ft.ListView(controls=[ft.ResponsiveRow(controls=data, expand=1)], expand=1)


@PlugManager.register('_tableUI')
class TableUI(UIPlugin):
    def process(self, rows: list, columns=[], **kwargs):
        rowsUI = []
        for row in rows:
            cellsUI = [ft.DataCell(ft.Text(value=i),
                                   on_tap=self.on_tap
                                   ) for i in row]
            rowsUI.append(ft.DataRow(cells=cellsUI))
        columnsUI = [ft.DataColumn(ft.TextField(
            value=col,
            border=ft.InputBorder.NONE,
            )
        ) for col in columns]
        return ft.ListView([ft.DataTable(rows=rowsUI, columns=columnsUI, expand=1)], expand=1)
    
    def on_tap(self, e):
        text = e.control.content.value
        e.control.content = ft.TextField(
            value=text,
            border=ft.InputBorder.NONE,
            on_blur=partial(self.leave_tap,cell=e.control),
            on_submit=partial(self.leave_tap,cell=e.control),
            )
        e.control.update()
        
    def leave_tap(self, e, cell=ft.Text("")):
        text = e.control.value
        cell.content = ft.Text(text)
        cell.update()


@PlugManager.register('_dictUI')
class DictUI(UIPlugin):
    """
    显示key value 的 dict
    mode: show edit
    multiline: enable multiline turn into textarea
    """

    def process(self, data: dict, mode='show', multiline=False, **kwargs):
        def on_change(e):
            data[e.control.hint_text] = e.data
        return ft.ListView([ft.ResponsiveRow(
            controls=[
                ft.ListTile(leading=ft.Icon(ft.icons.KEY), title=ft.Text(
                    item[0], size=ft.FontWeight.W_500), col={"xs": 12, "md": 3}),
                ft.TextField(value=item[1],
                             border=ft.InputBorder.UNDERLINE,
                             hint_text=item[0], col={"xs": 12, "md": 9},
                             on_change=on_change,
                             disabled=mode == 'show',
                             multiline=multiline)
            ],
        ) for item in data.items()], expand=1, spacing=10)


@PlugManager.register('_tocUI')
class TocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        def on_click(e):
            key = e.control.title.value
            main_container.content = data[key]
            main_container.update()

        main_container = ft.Container(expand=1)
        listiles = [ft.ListTile(leading=ft.Icon(ft.icons.BOOKMARK_OUTLINE_ROUNDED),
                    title=ft.Text(i), on_click=on_click)
                    for i in data.keys()]
        return ft.ResponsiveRow(
            controls=[
                ft.ListView(listiles, col={"xs": 12, "md": 3}, expand=1),
                ft.ListView([main_container], col={
                            "xs": 12, "md": 9}, expand=1)
            ],
            expand=True
        )


@PlugManager.register('_markdown_tocUI')
class MarkdownTocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        data = {k: ft.Markdown(
                        value=v,
                        col={"xs": 12, "md": 9},
                        expand=1,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
                        )
                for k, v in data.items()}
        return PlugManager.run(("_tocUI",), data, **kwargs)


@PlugManager.register('_search_base')
class SearchBase(UIPlugin):
    """
    基础知识库样式
    """
    ICON = ft.icons.BOOKMARKS_OUTLINED

    def process(self, data: dict, db, search_feild, container, ui_template="_markdown_tocUI", **kwargs):
        self.db = db
        self.container = container
        search_feild.on_change = self.on_change
        self.table_name = data
        self.ui_template = ui_template
        return self.ui("")

    def on_change(self, e):
        self.container.content = self.ui(e.data)
        self.container.update()

    def ui(self, key):
        data = {}
        table = self.db.get_table(self.table_name, primary_id="key")
        for item in table.find(key={'like': f"%{key}%"}):
            data[item['key']] = item['value']
        return PlugManager.run(plugins=(self.ui_template,), data=data)