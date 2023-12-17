from app.plug import *

@Plug.register("月份简写")
class Month(UIPlugin):
    """
    月份各语言简写对应表
    """
    ICON=ft.icons.HOURGLASS_BOTTOM
    def process(self, data, **kwargs):
        return Plug.run(plugins=("_pluginUI_with_search",),
                 data=self.DATA,
                 ui_template="_dictUI",
                 key_icon=ft.icons.FIBER_MANUAL_RECORD_OUTLINED,
                 **kwargs) 
    
    DATA = {
      "1": "Jan/ene/janv/一月",
      "2": "Feb/feb/févr/二月",
      "3": "Mar/mar/mars/三月",
      "4": "Apr/abr/avril/四月",
      "5": "May/may/mai/五月",
      "6": "Jun/jun/juin/六月",
      "7": "Jul/jul/juil/七月",
      "8": "Aug/ago/août/八月",
      "9": "Sep/sep/sept/九月",
      "10": "Oct/oct/oct/十月",
      "11": "Nov/nov/nov/十一月",
      "12": "Dec/dic/déc/十二月"
    }
