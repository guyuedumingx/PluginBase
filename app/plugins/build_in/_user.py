from app.plug import *
import requests

@Plug.register("_login")
class Login(Plugin):
    def process(self, data, page, state, **kwargs):
        ehr = ENV['EHR']
        data = dict(ehr=ehr, ip=Plug.run(plugins=("_get_local_ip",)))
        try:
            resp = requests.post(f"http://{ENV['server_addr']}:{ENV['server_port']}/login", data=json.dumps(data))
            if resp.status_code == 200:
                state.bgcolor = ft.colors.GREEN
                page.update()
        except:
            Plug.run(plugins=("_notice",), data="连接服务器失败", page=page)
        return super().process(data, **kwargs)