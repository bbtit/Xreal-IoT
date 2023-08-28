import asyncio
import aiohttp
import aiofiles
from rich import print
from queue import Queue


async def process_queue(file_path_queue: Queue, url):
    async with aiohttp.ClientSession() as session:
        while True:
            file_path = await file_path_queue.get()
            asyncio.create_task(post_file(session, url, file_path))
            file_path_queue.task_done()


async def post_file(session, url, file_path):
    async with aiofiles.open(file_path, "rb") as file:
        data = await file.read()
        files = {"file": ("weather.mp3", data)}
        async with session.post(url, data=files) as response:
            json_response = await response.json()
            print(f"{json_response}")


async def main(file_path, url):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, data={"file": open(file_path, "rb")}
        ) as response:
            print(response)
            json_response = await response.json()
            print(
                f"""File Path: {file_path},
                \nStatus Code: {response.status},
                \nJSON Content: {json_response}"""
            )


class FileUploader:
    def __init__(self, file_path_queue, url):
        self.file_path_queue = file_path_queue
        self.url = url

    async def process_queue(self):
        async with aiohttp.ClientSession() as session:
            while True:
                file_path = await self.file_path_queue.get()
                asyncio.create_task(self.post_file(session, file_path))
                self.file_path_queue.task_done()

    async def post_file(self, session, file_path):
        async with aiofiles.open(file_path, "rb") as file:
            data = await file.read()
            files = {"file": ("weather.mp3", data)}
            async with session.post(self.url, data=files) as response:
                json_response = await response.json()
                print(f"{json_response}")

    async def start(self):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.url, data={"file": open(file_path, "rb")}
            ) as response:
                print(response)
                json_response = await response.json()
                print(
                    f"""File Path: {file_path},
                    \nStatus Code: {response.status},
                    \nJSON Content: {json_response}"""
                )


async def main2(file_path, url):
    file_path_queue = asyncio.Queue()
    file_path_queue.put_nowait(file_path)

    uploader = FileUploader(file_path_queue, url)
    await asyncio.gather(
        uploader.process_queue(),
        uploader.start(),
    )


if __name__ == "__main__":
    file_path = "weather.mp3"
    url = "http://192.168.11.53:80/api/transcribe"
    asyncio.run(main(file_path, url))
