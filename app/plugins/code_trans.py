from app.plug import *


@Plug.register('明码转换')
class CodeTrans(UIPlugin):
    """
    将中文商用电码转换为中文

    1. 可以直接在搜索框输入电码
    2. 支持多电码同时转义, 用**空格**分割不同电码
    > `_` 代表码库中无该电码对应字
    """
    ICON = ft.icons.TRANSLATE

    def process(self, data, search_feild: ft.TextField, db, container, **kwargs):
        self.db = db
        self.container = container
        search_feild.on_change = self.on_change
        search_feild.hint_text = "输入电码"

    def on_change(self, e):
        code_list = e.data.split(" ")
        data = [self.db['中文商用电码表'].find_one(key=code) for code in code_list]
        res = []
        for item in data:
            try:
                res.append(item['value'])
            except:
                res.append("_")
        self.container.content = ft.ListView(
            [ft.ResponsiveRow(
                [ft.Text(i, size=30, col={"xs": 1}) for i in res])],
            expand=1, auto_scroll=True)
        self.container.update()