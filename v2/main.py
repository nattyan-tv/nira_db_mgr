import asyncio
import json

from motor import motor_asyncio

import database
import dbmodel

setting = json.load(open("setting.json", "r"))

MONGO_CLIENT = motor_asyncio.AsyncIOMotorClient(setting["mongodb"])
HTTP_DB = database.openClient(setting["httpdb"])
MONGO_DB_NAME = setting["mongodb_name"]

# HTTP_db, Mongo, Class
DATABASES = [
    ("autorole", "autorole", dbmodel.GuildValue),
    ("bump_data", "bump", dbmodel.GuildValue),
    (..., "INVITE", dbmodel.InviteData),
    (..., "MESSAGEDM", dbmodel.MessageDM),
    (..., "MESSAGEROLE", dbmodel.MessageRole),
    (..., "MINECRAFT", dbmodel.Minecraft),
    (..., "MOD", dbmodel.Mod),
    (..., "PIN", dbmodel.Pin),
    (..., "EXREACTION", dbmodel.ExReaction),
    (..., "REMIND", dbmodel.Remind),
    (..., "STEAM", dbmodel.SteamServer),
    (..., "AUTOSS", dbmodel.AutoSS),
    (..., "SIRITORI", dbmodel.Siritori),
    (..., "DISSOKU", dbmodel.Dissoku),
    (..., "WELCOMEINFO", dbmodel.WelcomeInfo),
    (..., "ROLEKEEPER", dbmodel.RoleKeeper),
]

async def main():
    mongo = MONGO_CLIENT[MONGO_DB_NAME]
    for httpdb_name, mongodb_name, cls in DATABASES:
        print(httpdb_name, mongodb_name, issubclass(cls, dbmodel.GuildValue) or issubclass(cls, dbmodel.ChannelValue))
        if issubclass(cls, dbmodel.GuildValue) or issubclass(cls, dbmodel.ChannelValue):
            c = cls(HTTP_DB, mongo, httpdb_name, mongodb_name, cls.http_type, value="role_id" if httpdb_name == "bump_data" or httpdb_name == "autorole" else "")
        else:
            c = cls(HTTP_DB, mongo)
        await c.main()
        await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
