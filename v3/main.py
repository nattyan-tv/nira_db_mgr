from motor import motor_asyncio

import asyncio
import aiofiles
import json

from typing import TypedDict

class NRSetting(TypedDict):
    _id: int
    normal: bool
    extended: bool

async def main():
    async with aiofiles.open("setting.json") as f:
        config = json.loads(await f.read())
    client = motor_asyncio.AsyncIOMotorClient(config["database_url"])
    database = client[config["database_name"]]
    ar_collection: motor_asyncio.AsyncIOMotorCollection = database["ar_setting"]
    nr_collection: motor_asyncio.AsyncIOMotorCollection = database["nr_setting"]

    ar_data_raw = await ar_collection.find({"all": {"$ne": 1}}, {"_id": False}).to_list(length=None)
    ar_data = [d["guild_id"] for d in ar_data_raw]

    nr_data_raw = await nr_collection.find({}, {"_id": False}).to_list(length=None)

    nr_data = []
    for d in nr_data_raw:
        if "all" in d and not d["all"]:
            nr_data.append(int(d["guild_id"]))
        for k, v in d.items():

            if k == "all" or k == "guild_id":
                pass
            else:
                if not v:
                    nr_data.append(int(k))
                else:
                    print(k, v)

    results: dict[int, NRSetting] = {}
    for d in nr_data:
        if d in results:
            results[d]["extended"] = False
        else:
            results[d] = {
                "_id": d,
                "normal": False,
                "extended": True
            }
    for d in ar_data:
        if d in results:
            results[d]["normal"] = False
            results[d]["extended"] = False
        else:
            results[d] = {
                "_id": d,
                "normal": False,
                "extended": False
            }

    async with aiofiles.open("writedata.json", "w") as f:
        await f.write(json.dumps(list(results.values())))




if __name__ == "__main__":
    asyncio.run(main())
