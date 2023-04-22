import asyncio
import json

from motor import motor_asyncio

import database
import dbmodel

setting = json.load(open("setting.json", "r"))

MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(setting["mongo"])
HTTP_DB = database.openClient(setting["httpdb"])
MONGO_DB_NAME = setting["mongodb_name"]

# HTTP_db, Mongo, Class
DATABASES = [
    ("autorole", "autorole", dbmodel.GuildValue),
    ("bump_data", "bump", dbmodel.GuildValue),
    (..., ..., dbmodel.InviteData),
    (..., ..., dbmodel.MessageDM),
    (..., ..., dbmodel.MessageRole),
    (..., ..., dbmodel.Minecraft),
    (..., ..., dbmodel.Mod),
    (..., ..., dbmodel.Pin),
    (..., ..., dbmodel.ExReaction),
    (..., ..., dbmodel.Remind),
    (..., ..., dbmodel.SteamServer),
    (..., ..., dbmodel.AutoSS),
    (..., ..., dbmodel.Siritori),
    (..., ..., dbmodel.Dissoku),
    (..., ..., dbmodel.WelcomeInfo),
    (..., ..., dbmodel.RoleKeeper),
]

async def main():
    mongo = MONGO_CLIENT["nira-bot"]
    for httpdb_name, mongodb_name, cls in DATABASES:
        if isinstance(cls, dbmodel.GuildValue) or isinstance(cls, dbmodel.ChannelValue):
            c = cls(HTTP_DB, mongo, httpdb_name, mongodb_name, cls.http_type)
        else:
            c = cls(HTTP_DB, mongo)
        await c.main()

if __name__ == "__main__":
    asyncio.run(main())
