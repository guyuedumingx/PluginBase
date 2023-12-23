from app.plug import *

@Plug.register("_plugin_baseUI")
class PluginBaseUI(Plugin):
    """
    插件界面
    """
    def process(self, plugin_name, page, search_onchange=None, **kwargs):
        self.page = page
        plugin = Plug.get_plugin(plugin_name)
        back_btn = ft.Container(
            ft.Icon(name=ft.icons.ARROW_BACK),
            col={"xs": 2, "sm": 1, "md": 1, "xl": 1},
            alignment=ft.alignment.center,
            height=60,
            on_click=lambda _: Plug.run(plugins=("_back",), page=page, plugin_name=plugin_name, **kwargs)
        )
        search_feild = ft.TextField(
            hint_text=plugin_name,
            prefix_icon=plugin.ICON,
            col={"xs": 10, "sm": 11, "md": 11, "xl": 11},
            border_radius=32,
            scale=ft.Scale(scale_x=1.0, scale_y=0.85),
            text_size=18,
            on_change= search_onchange if search_onchange!=None else self.search_feild_onchange
        )
        process_bar = ft.ProgressBar(visible=False,value=2) 
        tips_btn = ft.FloatingActionButton(icon=ft.icons.TIPS_AND_UPDATES,
                scale=0.7,
                opacity=0.5,
                bgcolor=ft.colors.WHITE,
                shape=ft.CircleBorder(),
                on_click= lambda _: Plug.run(
                    plugins=("_tipsview","_tips_backbtn"),
                    data=plugin_name,
                    plugin_obj=plugin,
                    page=page
                    )
                )
        container = Plug.run(plugins=("_defaultbackground",))
        return (back_btn, search_feild, process_bar, container, tips_btn)
    
    def search_feild_onchange(self, e):
        self.page.views.pop() and self.page.update()
        Plug.get_plugin("_index").search_func(e)


@Plug.register("_tips_backbtn")
class TipsViewWithBackButton(UIPlugin):
    """
    有返回键的提示界面，传进来的data应该是一个ft的组件
    data: should be a ft component
    """
    def process(self, data, page, **kwargs):
        back_btn = ft.FloatingActionButton(icon=ft.icons.ARROW_BACK,
            scale=0.7,
            opacity=0.5,
            bgcolor=ft.colors.WHITE,
            shape=ft.CircleBorder(),
            on_click=lambda _: Plug.run(plugins=("_back",), page=page, plugin_name=data)
            )
        url = page.views[-1].route + "/tips"
        page.views.append(ft.View(
            url,
            [back_btn, data]
        ))
        page.go(url)
        return data
    

@Plug.register('_notice')
class Notice(Plugin):
    """
    底部SnackBar弹出式通知，默认显示5秒
    data: 需要显示的数据
    page: ft.Page
    """
    def process(self, data, page: ft.Page, **kwargs):
        page.snack_bar = ft.SnackBar(ft.Text(data))
        page.snack_bar.open = True
        page.update()
        return data


@Plug.register('_banner')
class Banner(Plugin):
    """
    顶部确认形通知，点击关闭键才会关闭
    data: 需要显示的text
    page: ft.Page
    """
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


@Plug.register('_listUI')
class ListUI(UIPlugin):
    def process(self, data: list, **kwargs):
        return ft.ListView(controls=data, expand=1)


@Plug.register('_flowUI')
class FlowUI(UIPlugin):
    """
    瀑布流显示插件 
    data: 需要被显示的ft插件
    counts_per_row: 每行显示多少个
    
    counts_per_row默认情况下是指 sm情况, xs情况下会单行显示一个
    lg情况下会显示为counts_per_row的双倍
    """
    def process(self, data: list, counts_per_row=2, **kwargs):
        for item in data:
            item.col = {"sm": 12 / counts_per_row,
                        "xs": 12, "lg": 12 / (counts_per_row*2)}
        return ft.ListView(controls=[ft.ResponsiveRow(controls=data, expand=1)], expand=1)


@Plug.register('_tableUI')
class TableUI(UIPlugin):
    """
    表格显示插件
    rows: 行数据
    columns: 列标题
    如果行列都没有数据，那么会返回rows
    如果列没有特别指定，那么选择rows的第一行作为columns
    """
    def process(self, rows, columns=[], **kwargs):
        rows, columns = self._rebuild_data(rows, columns)
        if(len(rows) == 0 and len(columns) == 0): return rows
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
    
    def _rebuild_data(self, data, columns):
        #TODO to test
        if isinstance(data, list):
            if(len(columns) == 0): 
                return (data[1:], data[0])
            return (data, columns)
        elif isinstance(data, dict):
            columns = []
            rows = []
            for k, v in data.items():
                columns.append(k)
                rows.append(v)
            return (rows, columns)

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


@Plug.register('_dictUI')
class DictUI(UIPlugin):
    """
    显示key value 的 dict
    mode: show edit
    multiline: enable multiline turn into textarea
    """
    def process(self, data: dict, mode='show', multiline=True, cell_on_change=lambda x:x, key_icon=ft.icons.FIBER_MANUAL_RECORD_OUTLINED,**kwargs):
        def on_change(e):
            data[e.control.hint_text] = e.data
            cell_on_change(e)
        return ft.ListView([ft.ResponsiveRow(
            controls=[
                ft.ListTile(leading=ft.Icon(key_icon), title=ft.Text(
                    item[0], size=ft.FontWeight.W_500), col={"xs": 12, "md": 3}),
                ft.TextField(
                    value=item[1],
                    border=ft.InputBorder.UNDERLINE,
                    hint_text=item[0], col={"xs": 12, "md": 9},
                    on_change=on_change,
                    disabled=mode == 'show',
                    multiline=multiline
                    )
            ],
        ) for item in data.items()], expand=1, spacing=10)


@Plug.register('_tocUI')
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


@Plug.register('_markdown_tocUI')
class MarkdownTocUI(UIPlugin):
    def process(self, data: dict, **kwargs):
        data = {k: ft.Markdown(
                        value=v,
                        col={"xs": 12, "md": 9},
                        expand=1,
                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB
                        )
                for k, v in data.items()}
        return Plug.run(("_tocUI",), data, **kwargs)


@Plug.register('_local_knowledge_base')
class SearchBase(UIPlugin):
    """
    基础知识库样式
    """
    ICON = ft.icons.BOOKMARKS_OUTLINED

    def process(self, data, db, search_feild, page, container, tips_btn, ui_template="_markdown_tocUI", **kwargs):
        self.db = db
        self.container = container
        search_feild.on_change = self.on_change
        self.table_name = data
        self.ui_template = ui_template
        # tips_btn.on_click = partial(self.tips_edit, container=container, page=page)
        return self.ui("")
    
    def tips_edit(self, e, container:ft.Container, page:ft.Page):
        #TODO 
        Plug.run(
            plugins=("_tips_backbtn",),
            data=container.content, page=page)

    def on_change(self, e):
        self.container.content = self.ui(e.data)
        self.container.update()

    def ui(self, key):
        data = {}
        table = self.db.get_table(self.table_name, primary_id="key")
        for item in table.find(key={'like': f"%{key}%"}):
            data[item['key']] = item['value']
        return Plug.run(plugins=(self.ui_template,), data=data)


@Plug.register('_pluginUI_with_search')
class SearchBase(UIPlugin):
    """
    带搜索和保存按钮的插件
    save_handler: 保存操作
    """
    ICON = ft.icons.BOOKMARKS_OUTLINED
    def process(self, data: dict, search_feild, container, tips_btn, mode="show", save_handler=lambda x:x, ui_template="_markdown_tocUI", **kwargs):
        self.container = container
        search_feild.on_change = self.on_change
        self.table_name = data
        self.ui_template = ui_template
        self.data = data
        self.mode = mode
        if mode == "edit":
            tips_btn.icon = ft.icons.SAVE
            tips_btn.on_click = lambda x: save_handler(data)
        self.kwargs = kwargs
        return self.ui("") 

    def on_change(self, e):
        self.container.content = self.ui(e.data)
        self.container.update()

    def ui(self, key: str):
        self.curdata = {}
        for k,v in self.data.items():
            try:
                if key.lower() in str(k).lower() or key.lower() in str(v).lower():
                    self.curdata[k] = v
            except:
                if key in str(k) or key in str(v):
                    self.curdata[k] = v
        return Plug.run(plugins=(self.ui_template,), data=self.curdata, mode=self.mode, cell_on_change=self.cell_on_change, **self.kwargs)
    
    def cell_on_change(self, e):
        if self.mode == "edit":
            self.data.update(self.curdata)
        else:
            pass