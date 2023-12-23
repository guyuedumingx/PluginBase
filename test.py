import asyncio

class FilePlugin:
    def __init__(self, host, port, file_path):
        self.host = host
        self.port = port
        self.file_path = file_path
        self.server = None
        self.running = False

    async def start_server(self):
        self.server = await asyncio.start_server(
            self.handle_client, self.host, self.port)
        self.running = True
        print(f"Server started on {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def stop_server(self):
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            print("Server stopped.")
            self.running = False

    async def handle_client(self, reader, writer):
        with open(self.file_path, "wb") as file:
            while True:
                data = await reader.read(1024)
                if not data:
                    break
                file.write(data)
        print("File received successfully.")
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

# 示例使用
receiver_plugin = FilePlugin('localhost', 8888, 'assets/revice.xlsx')

# 启动服务器
# asyncio.run(receiver_plugin.start_server())
# print("Start server success...")

send_plugin = FilePlugin('localhost', 8888, '1.xlsx')
asyncio.run(send_plugin.send_file())
print("send file..")

# 当需要停止服务器时
# asyncio.run(receiver_plugin.stop_server())
