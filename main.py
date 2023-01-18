import asyncio
from os import mkdir
from os.path import exists, join
from typing import Generator

import aiohttp


async def get_file_names(
    client: aiohttp.ClientSession,
) -> dict[str, Generator[str, None, None]]:
    async with client.get("https://nekos.best/api/v2/endpoints") as response:
        return {
            tag: (
                "{:0>{}}.{}".format(n, len(data["min"]), data["format"])
                for n in range(int(data["min"]), int(data["max"]))
            )
            for tag, data in (await response.json()).items()
        }


async def download(
    client: aiohttp.ClientSession,
    url: str,
    file: str,
    dir: str,
) -> None:
    file_path = join(dir, file)
    if not exists(file_path):
        async with client.get(f"{url}/{file}") as response:
            with open(file_path, "wb") as write:
                async for chunk in response.content.iter_chunked(1024):
                    write.write(chunk)
        print(f"File downloaded {url}/{file}")
    else:
        print(f"File skipped {url}/{file}")


async def main() -> None:
    download_dir = join("downloads")
    if not exists(download_dir):
        mkdir(download_dir)

    tasks = []

    async with aiohttp.ClientSession() as client:
        for tag, files in (await get_file_names(client)).items():
            tag_dir = join(download_dir, tag)
            if not exists(tag_dir):
                mkdir(tag_dir)

            for file in files:
                tasks.append(
                    asyncio.create_task(
                        download(
                            client,
                            f"https://nekos.best/api/v2/{tag}",
                            file,
                            tag_dir,
                        )
                    )
                )

        for task in tasks:
            await task


if __name__ == "__main__":
    asyncio.run(main())
