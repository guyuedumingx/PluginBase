import asyncio
from app.plug import *
import os


# @Plug.register("文件传输")
class FileTransferPluginUI(UIPlugin):
    """
    传输文件给对方
    """
    ICON=ft.icons.FILE_COPY
    def process(self, data, **kwargs):
        
        return super().process(data, **kwargs)


@Plug.register("_file_trans")
class FileTransferPlugin(Plugin):

    def process(self, data, host, port=36908, mode="client", file_path="", **kwargs):
        self.host = host
        self.port = port
        self.file_path = file_path
        if mode == "server":
            asyncio.run(self.start_server())
        elif mode == "client":
            asyncio.run(self.send_file())
    

    async def start_server(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port)
        async with server:
            await server.serve_forever()

    async def handle_client(self, reader, writer):
        # 文件重组逻辑
        with open(self.file_path, "wb") as file:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                file.write(data)
        writer.close()

    async def send_file(self):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        # 文件发送逻辑
        with open(self.file_path, "rb") as file:
            while True:
                data = file.read(1024)
                if not data:
                    break
                writer.write(data)
                await writer.drain()
        writer.close()
