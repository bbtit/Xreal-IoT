import asyncio
import aiohttp
import aiofiles
from rich import print


async def process_queue(file_path_queue, url):
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


if __name__ == "__main__":
    asyncio.run(main("weather.mp3", "http://192.168.11.53:80/api/transcribe"))
