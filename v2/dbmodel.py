import asyncio
import database
import traceback

from motor import motor_asyncio

import HTTP_db
import dict_list

class Database:
    http_name: str
    mongo: str
    http_type: database.HttpDBType
    mongo_db: motor_asyncio.AsyncIOMotorClient
    client: HTTP_db.Client
    pulled_data: dict

    def __init__(self, client: HTTP_db.Client, mongo_db, **kwargs):
        self.client = client # HTTP_dbのクライアント
        self.mongo_db = mongo_db # MongoDBのデータベース（client["nira"]）

    async def _pull(self):
        """Pull from database."""
        if self.http_type == database.HttpDBType.CHANNEL_VALUE:
            try:
                data = dict_list.listToDict(await self.client.get(self.http_name))
                return data
            except Exception:
                print("Error", traceback.format_exc())
                return {}
        elif self.http_type == database.HttpDBType.GUILD_VALUE:
            try:
                data = dict(await self.client.get(self.http_name))
                return data
            except Exception:
                print("Error", traceback.format_exc())
                return {}
        elif self.http_type == database.HttpDBType.SAME_VALUE:
            try:
                data = await self.client.get(self.http_name)
                return data
            except Exception:
                print("Error", traceback.format_exc())
                return {}

    async def _push(self, d):
        self.mongo_db[self.mongo].insert_many(d)

    async def main(self):
        self.pulled_data = await self._pull()
        if len(self.pulled_data) == 0:
            print("Skip (NOT STORED)")
            return
        conved = self.conv(self.pulled_data)
        if len(conved) == 0:
            print("Skip (CONVERTED)")
            return
        await self._push(conved)

    def conv(self, v: dict) -> list:
        raise NotImplementedError


    def nlong(self, number: int):
        return number

    def asLong(self, value: int | str) -> str | int | dict[str, str]:
        if isinstance(value, str):
            try:
                value = int(value)
            except ValueError:
                return value
        if value > 2**31-1 or value < -2**31:
            return self.nlong(value)
        else:
            return value

class GuildValue(Database):
    http_name: str
    mongo: str
    http_type: database.HttpDBType = database.HttpDBType.GUILD_VALUE
    value: str

    def __init__(
            self,
            client,
            mongo_db,
            http_name = "",
            mongo = "",
            http_type = database.HttpDBType.GUILD_VALUE,
            value = "",
            **kwargs
        ):
        self.client = client
        self.mongo_db = mongo_db
        self.http_name = http_name
        self.mongo = mongo
        self.http_type = http_type
        self.value = value

    def conv(self, v):
        result = []
        for key, value in v.items():
            result.append({"guild_id": self.nlong(key), self.value: self.nlong(value)})
        return result

class ChannelValue(Database):
    http_name: str
    mongo: str
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def __init__(self, client, mongo_db, http_name = "", mongo = "", http_type = database.HttpDBType.CHANNEL_VALUE, **kwargs):
        self.client = client
        self.mongo_db = mongo_db
        self.http_name = http_name
        self.mongo = mongo
        self.http_type = http_type

    def conv(self, v):
        result = []
        for key, value in v.items():
            r = {"guild_id": self.nlong(key)}
            for channel, vl in value.items():
                r[str(channel)] = self.asLong(vl)
        return result

class InviteData(Database):
    http_name: str = "invite_data"
    mongo: str = "invite_data"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            r = {"guild_id": self.nlong(key)}
            for url, use in value.items():
                r[url] = use
            result.append(r)
        return result

class MessageDM(Database):
    http_name: str = "message_dm"
    mongo: str = "message_dm"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            for channel, vl in value.items():
                result.append({"guild_id": self.nlong(key), "channel_id": self.nlong(channel), "regex": vl[0], "message": vl[1]})
        return result

class MessageRole(Database):
    http_name: str = "message_role"
    mongo: str = "message_role"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            for channel, vl in value.items():
                result.append({"guild_id": self.nlong(key), "channel_id": self.nlong(channel), "regex": vl[0], "action_type": vl[1], "role_id": self.nlong(vl[2])})
        return result

class Minecraft(Database):
    http_name: str = "minecraft"
    mongo: str = "minecraft"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            for c, vl in value.items():
                if c == "value":
                    continue
                else:
                    result.append(
                        {
                            "guild_id": self.nlong(key),
                            "name": vl[0],
                            "host": vl[1].split(":", 1)[0],
                            "port": int(vl[1].split(":", 1)[1]),
                            "server_type": vl[2],
                            "server_id": int(c)
                        }
                    )
        return result

class Mod(Database):
    http_name: str = "mod_data"
    mongo: str = "mod"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            r = {"guild_id": self.nlong(key), "counter": value["counter"], "role": self.nlong(value["role"]), "remove_role": value["remove_role"]}
            result.append(r)
        return result

class Pin(Database):
    http_name: str = "bottom_up"
    mongo: str = "bottom_pin"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for _, value in v.items():
            for channel, mesd in value.items():
                result.append({"_id": self.nlong(channel), "text": mesd[0], "last_message": self.nlong(mesd[1])})
        return result

class ExReaction(Database):
    http_name: str = "ex_reaction_list"
    mongo: str = "ex_reaction"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            r = {}
            for k, mesd in value.items():
                if k == "value":
                    continue
                n = k.split("_", 1)[0]
                t = k.split("_", 1)[1]
                if t == "tr":
                    if n not in r:
                        r[n] = {"guild_id": self.nlong(key), "trigger": mesd, "mention": True}
                    else:
                        r[n]["trigger"] = mesd
                        result.append(r[n])
                elif t == "re":
                    if n not in r:
                        r[n] = {"guild_id": self.nlong(key), "return": mesd, "mention": True}
                    else:
                        r[n]["return"] = mesd
                        result.append(r[n])
        return result

# そのほかのリアクションは復元しません。

# NotifyTokenも復元しません

class Remind(Database):
    http_name: str = "remind_data"
    mongo: str = "remind_data"
    http_type: database.HttpDBType = database.HttpDBType.OTHER_VALUE

    async def _pull(self):
        if not await self.client.exists(self.http_name):
            return {}
        try:
            TEMP_DATA = await self.client.get(self.http_name)
            if TEMP_DATA == []:
                return {}
            return {i[0]: {i[1][0]: i[1][1]} for i in TEMP_DATA}
        except Exception as err:
            print(err)
            return {}

    def conv(self, v):
        result = []
        for key, value in v.items():
            for time, content in value.items():
                result.append({"channel_id": self.nlong(key), "time": time, "content": content})
        return result

class SteamServer(Database):
    http_name: str = "steam_server"
    mongo: str = "steam_server"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            r = {}
            for k, mesd in value.items():
                if k == "value":
                    continue
                n = k.split("_", 1)[0]
                t = k.split("_", 1)[1]
                if t == "nm":
                    if n not in r:
                        r[n] = {"guild_id": self.nlong(key), "sv_nm": mesd, "server_id": int(n)}
                    else:
                        r[n]["sv_nm"] = mesd
                        result.append(r[n])
                elif t == "ad":
                    if n not in r:
                        r[n] = {"guild_id": self.nlong(key), "sv_ad": mesd, "server_id": int(n)}
                    else:
                        r[n]["sv_ad"] = mesd
                        result.append(r[n])
        return result

class AutoSS(Database):
    http_name: str = "autoss_check"
    mongo: str = "auto_ss"
    http_type: database.HttpDBType = database.HttpDBType.GUILD_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            result.append({"guild_id": self.nlong(key), "channel_id": self.nlong(value[0]), "message_id": self.nlong(value[1])})
        return result

class Siritori(Database):
    http_name: str = "srtr_data"
    mongo: str = "siritori_game"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for guild, channels in v.items():
            result.append({"guild_id": self.nlong(guild), "channels": [self.nlong(channel) for channel in channels]})
        return result

# TTSは復元しません

class Dissoku(Database):
    http_name: str = "dissoku_data"
    mongo: str = "up_notify"
    http_type: database.HttpDBType = database.HttpDBType.GUILD_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            result.append({"guild_id": self.nlong(key), "role_id": (self.nlong(value) if value is not None else None)})
        return result

class WelcomeInfo(Database):
    http_name: str = "welcome_info"
    mongo: str = "welcome_info"
    http_type: database.HttpDBType = database.HttpDBType.GUILD_VALUE

    def conv(self, v):
        result = []
        for key, value in v.items():
            result.append({"guild_id": self.nlong(key), "channel_id": self.nlong(value)})
        return result

class RoleKeeper(Database):
    http_name: str = "role_keeper"
    mongo: str = "role_keeper"
    http_type: database.HttpDBType = database.HttpDBType.CHANNEL_VALUE

    def conv(self, v):
        result = []
        for guild, settings in v.items():
            r = {"guild_id": self.nlong(guild)}
            for user, roles in settings.items():
                r[str(user) if user != "rk" else "setting"] = roles
            result.append(r)
        return result
