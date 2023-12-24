from app.plug import *

@Plug.register('数据库')
class SQLQueryPlugin(UIPlugin):
    """
    通过SQL语句操作内部数据库
    """
    ICON = ft.icons.LOCAL_BAR_SHARP
    def process(self, data, page, container, search_feild, db, **kwargs):
        self.db = db
        self.page = page
        self.container = container
        self.rows = []
        self.columns = []
        self.short_output_mode = True
        self.header_mode = True
        self.auto_clear = False
        self.sql_input = search_feild
        search_feild.hindt_text = "Enter SQL query here"
        search_feild.border = ft.InputBorder.UNDERLINE
        search_feild.multiline = True
        search_feild.on_change = None
        search_feild.on_submit = None
        return self.create_ui()
    
    def clear_action(self, e):
        self.result_view.value = None
        self.result_view.update()

    def create_ui(self):
        self.result_view = ft.Markdown(
            selectable=True,
            extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
            expand=1,
            )
        query_button = ft.OutlinedButton(text="查询", on_click=self.execute_query)
        self.clear_button = ft.OutlinedButton(text="清空", on_click=self.clear_action)
        export_button = ft.OutlinedButton(text="导出XLSX", on_click=self.to_excel)
        self.table_button = ft.OutlinedButton(text="简要输出", on_click=self.short_output)
        self.table_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.short_output_mode else None
        self.header_button = ft.OutlinedButton(text="头模式", on_click=self.header_mode_output)
        self.header_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.header_mode else None
        self.auto_clear_button = ft.OutlinedButton(text="自动清空", on_click=self.auto_clear_mode)
        self.auto_clear_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.auto_clear else None
        self.show_tables_button = ft.OutlinedButton(text="表", on_click=self.show_tables)
        self.toggle_remote_local_button = ft.OutlinedButton(text="远程", on_click=self.toggle_remote_local)

        return ft.Column([
            ft.Row([query_button,
                    self.clear_button,
                    export_button,
                    self.auto_clear_button,
                    self.table_button,
                    self.header_button,
                    self.show_tables_button,
                    self.toggle_remote_local_button
                    ]),
            ft.ListView([self.result_view], expand=1)
        ])
    
    def toggle_remote_local(self, e):
        if self.db == Plug.get_state("db"):
            self.db = Plug.get_state("remote_db")
            self.toggle_remote_local_button.text = "本地"
        else:
            self.db = Plug.get_state("db")
            self.toggle_remote_local_button.text = "远程"
        self.toggle_remote_local_button.update()

        
    def execute_query(self, e):
        query = self.sql_input.value
        try:
            result = self.db.query(query)
            self.columns = [str(i) for i in result.keys]
            self.rows = [[str(i) for i in row.values()] for row in result]
            result_md = self.format_result_as_markdown(self.rows)
        except Exception as e:
            result_md = str(e)+ "  \n  \n ----  \n"

        try:
            if self.auto_clear:
                self.result_view.value = result_md
            else:
                self.result_view.value = result_md + self.result_view.value
        except:
            self.result_view.value = result_md
        self.container.update()

    def format_result_as_markdown(self, result):
        result = result[0:10] if self.header_mode else result
        lines = [" | ".join(row) for row in result]
        lines = [f"| {i} |" for i in lines]
        column = " | ".join(self.columns)
        column = "| " + column + " |"
        spliter = "|-" * len(self.columns)
        if self.short_output_mode:
            s = '  \n'.join([column, *lines])
        else:
            s = '  \n'.join([column, spliter+"|", *lines])
        if self.header_mode and len(self.rows) > 10:
            s += f"  \n   \n x {len(self.rows)} rows total..."
        return f"## {self.sql_input.value}  \n{s}  \n   \n  ----  \n"
    
    def to_excel(self, e):
        Plug.run(plugins=("_save_file",),
            data=lambda x:Plug.run(plugins=("_to_excel",), data=x, rows=self.rows, columns=self.columns),
            page=self.page,
        )

    def short_output(self, e):
        self.short_output_mode = not self.short_output_mode
        self.table_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.short_output_mode else None
        self.table_button.update()

    def header_mode_output(self, e):
        self.header_mode = not self.header_mode
        self.header_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.header_mode else None
        self.header_button.update()
    
    def auto_clear_mode(self, e):
        self.auto_clear = not self.auto_clear
        self.auto_clear_button.icon = ft.icons.CHECK_CIRCLE_OUTLINE if self.auto_clear else None
        self.auto_clear_button.update()

    def show_tables(self, e):
        self.sql_input.value = "SELECT name FROM sqlite_master WHERE type='table';"
        self.sql_input.update()
        self.execute_query(e)
