import asyncio
import aiohttp
import aiofiles
from rich import print
from queue import Queue
from threading import Thread
from time import sleep


class FileUploader:
    def __init__(
        self, file_path_queue: Queue, transcribed_text_queue: Queue, url: str
    ):
        self.file_path_queue = file_path_queue
        self.transcribed_text_queue = transcribed_text_queue
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

    async def run(self):
        async with aiohttp.ClientSession() as session:
            while True:
                file_path: str = (
                    self.file_path_queue.get_nowait()
                    if not self.file_path_queue.empty()
                    else None
                )
                if file_path is None:
                    continue

                async with session.post(
                    self.url, data={"file": open(file_path, "rb")}
                ) as response:
                    print(response)
                    json_response = await response.json()
                    self.transcribed_text_queue.put(json_response["text"])
                    print(
                        f"""File Path: {file_path},
                            \nStatus Code: {response.status},
                            \nJSON Content: {json_response}"""
                    )


if __name__ == "__main__":
    file_path = "weather.mp3"
    url = "http://192.168.11.53:80/api/transcribe"
    # asyncio.run(main(file_path, url))

    file_path_queue = Queue()
    transcribed_text_queue = Queue()

    file_uploader = FileUploader(file_path_queue, transcribed_text_queue, url)
    file_upload_thread = Thread(
        target=asyncio.run, args=(file_uploader.run(),)
    )
    file_upload_thread.start()

    while True:
        file_path_queue.put(file_path)
        sleep(1)

    # print(type(file_uploader.start()))
