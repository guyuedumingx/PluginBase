from decimal import Decimal
from app.plug import *
from functools import partial
import warnings

@Plug.register('大写金额')
class Ccurrency(UIPlugin):
    """
    将小写金额转换为大写金额
    """
    ICON=ft.icons.CABLE_OUTLINED
    VERSION="2.0.2"
    def process(self, data, search_feild, container, page, **kwargs):
        search_feild.hint_text = "请输入小写金额"
        self.page = page
        self.container = container
        search_feild.on_change = self.feild_on_change
        search_feild.update()
        return ft.Text("Enter a money")

    def feild_on_change(self, e):
        try:
            value = self.cncurrency(e.data)
            self.container.content = ft.Text(spans=value)
            self.page.update()
        except Exception as e:
            Plug.run(plugins=("_notice",),data=e,page=self.page)

    def surrend_ui(self, lst):
        return [ft.TextSpan(i, 
        ft.TextStyle(size=40, color=ft.colors.GREY_700)
        ) for i in lst]

    def tips(self, e, idx=0):
        if idx != 0:
            Plug.run(plugins=("_notice",), data=self.INFO[idx].strip(), page=self.page)

    def cncurrency(self, value, prefix=False):
        if not isinstance(value, (Decimal, str, int)):
            msg = '''
            由于浮点数精度问题，请考虑使用字符串，或者 decimal.Decimal 类。
            因使用浮点数造成误差而带来的可能风险和损失作者概不负责。
            '''
            warnings.warn(msg, UserWarning)

        # 汉字金额前缀
        if prefix is True:
            prefix = self.surrend_ui(['人民币'])[0]
        else:
            prefix = ft.TextSpan('')

        # 汉字金额字符定义
        dunit = self.surrend_ui(['角', '分'])
        num = self.surrend_ui(['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖'])
        iunit = self.surrend_ui(['元', '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟'])
        num[0] = ft.TextSpan('零', ft.TextStyle(size=40, color=ft.colors.BLUE_700),on_click=partial(self.tips, idx=2))
        # 转换为Decimal，并截断多余小数
        if not isinstance(value, Decimal):
            value = Decimal(value).quantize(Decimal('0.01'))

        # 转化为字符串
        s = str(value)
        if len(s) > 19:
            raise ValueError('金额太大了，不知道该怎么表达。')
        istr, dstr = s.split('.')  # 小数部分和整数部分分别处理
        istr = istr[::-1]  # 翻转整数部分字符串
        so = []  # 用于记录转换结果

        # 零
        if value == 0:
            return [prefix, num[0], iunit[0]]
        haszero = False  # 用于标记零的使用
        if dstr == '00':
            haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”
        
        # 处理小数部分
        # 分
        if dstr[1] != '0':
            so.append(dunit[1])
            so.append(num[int(dstr[1])])
        elif dstr[0] != '0' and dstr[1] == '0':
            so.append(ft.TextSpan('整', ft.TextStyle(size=40, color=ft.colors.BLUE_700),on_click=partial(self.tips, idx=-1)))
        else:
            so.append(ft.TextSpan('整', ft.TextStyle(size=40, color=ft.colors.RED_700),on_click=partial(self.tips, idx=-1)))
        # 角
        if dstr[0] != '0':
            so.append(dunit[0])
            so.append(num[int(dstr[0])])
        elif dstr[1] != '0':
            so.append(ft.TextSpan('零', ft.TextStyle(size=40, color=ft.colors.RED_700),on_click=partial(self.tips, idx=-2)))  # 无角有分，添加“零”
            haszero = True  # 标记加过零了
            # pass

        # 无整数部分
        if istr == '0':
            if haszero:  # 既然无整数部分，那么去掉角位置上的零
                so.pop()
            so.append(prefix)  # 加前缀
            so.reverse()  # 翻转
            return so

        # 处理整数部分
        for i, n in enumerate(istr):
            n = int(n)
            if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
                if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                    so.pop()  # 去掉万
                so.append(iunit[i])
                if n == 0:  # 处理这些位上为零的情况
                    if not haszero:  # 如果以前没有加过零
                        so.insert(-1, num[0])  # 则在单位后面加零
                        haszero = True  # 标记加过零了
                    pass
                else:  # 处理不为零的情况
                    so.append(num[n])
                    haszero = False  # 重新开始标记加零的情况
            else:  # 在其他位置上
                if n != 0:  # 不为零的情况
                    so.append(iunit[i])
                    so.append(num[n])
                    haszero = False  # 重新开始标记加零的情况
                else:  # 处理为零的情况
                    if not haszero:  # 如果以前没有加过零
                        so.append(ft.TextSpan('零', ft.TextStyle(size=40, color=ft.colors.RED_700),on_click=partial(self.tips, idx=1)))
                        haszero = True
                        pass

        # 最终结果
        so.append(prefix)
        so.reverse()
        return so
    
    INFO = [
        "",
        """
（一）阿拉伯数字中间有“0”时，中文大写金额要写“零”字。如￥1，409.50，应写成人民币壹仟肆佰零玖元伍角。
（二）阿拉伯数字中间连续有几个“0”时，中文大写金额中间可以只写一个“零”字。如￥6，007.14，应写成人民币陆仟零柒元壹角肆分。
        """,
        """
        （三）阿拉伯金额数字万位或元位是“0”，或者数字中间连续有几个“0”，万位、元位也是“0”，但千位、角位不是“0”时，中文大写金额中可以只写一个零字，也可以不写“零”字。如￥1，680.32，应写成人民币壹仟陆佰捌拾元零叁角贰分，或者写成人民币壹仟陆佰捌拾元叁角贰分；又如￥107，000.53，应写成人民币壹拾万柒仟元零伍角叁分，或者写成人民币壹拾万零柒仟元伍角叁分。
        """,
        """
        （四）阿拉伯金额数字角位是“0”，而分位不是“0”时，中文大写金额“元”后面应写“零”字。如￥16，409.02，应写成人民币壹万陆仟肆佰零玖元零贰分；又如￥325.04，应写成人民币叁佰贰拾伍元零肆分。
        """,
        """
        二、中文大写金额数字到“元”为止的，在“元”之后，应写“整”（或“正”）字，在“角”之后可以不写“整”（或“正”）字。大写金额数字有“分”的，“分”后面不写“整”（或“正”）字。
        """
    ]