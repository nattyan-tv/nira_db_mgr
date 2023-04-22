# from https://github.com/team-i2021/nira_bot/util/database.py
import json
import os
import sys
import HTTP_db

import gspread
from oauth2client.service_account import ServiceAccountCredentials

__version__ = "db_mgr"

class database:
    def __init__(self, jsonFile: str, SPREADSHEET_KEY: str, url: str, password: str or None):
        self.jsonFile = jsonFile
        self.SPREADSHEET_KEY = SPREADSHEET_KEY
        self.url = url
        self.password = password

    def openSheet(self) -> gspread.Worksheet:
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.jsonFile, scope)
        gc = gspread.authorize(credentials)
        worksheet = gc.open_by_key(self.SPREADSHEET_KEY).sheet1
        return worksheet


    def readValue(self, data, cell) -> dict:
        return json.loads(data.acell(cell).value)


    def writeValue(self, data, cell, value) -> None:
        data.update_acell(cell, json.dumps(value))
        return None

    def openClient(self) -> HTTP_db.Client:
        url = self.url
        if self.password is not None:
            password = self.password
            return HTTP_db.Client(url=url, password=password)
        else:
            return HTTP_db.Client(url=url)

    async def database_initialize(self, client: HTTP_db.Client, key, default):
        if await client.exists(key):
            return
        else:
            await client.post(key, default)
            return

# https://qiita.com/164kondo/items/eec4d1d8fd7648217935
# B2:テスト/B3:TTS/B4:Up通知/B5:Reminder/B6:Captcha/B7:InviteURLs
# 予約済み: テスト/TTS/Captcha/InviteURLs
# 使用済み: Dissoku/Reminder


# from https://github.com/team-i2021/nira_bot/util/dict_list.py
def listToDict(source) -> dict:
    """\
[(12345,[(12345,"data"),(54321,"data2")])]
to
{12345:{12345:"data", 54321:"data2"}}"""
    temp = {}
    source = dict(source)
    for i in list(source.keys()):
        if i not in temp:
            temp[i] = {}
        temp[i].update(dict(source[i]))
    return temp


def dictToList(source: dict) -> list:
    """\
{12345:{12345:"data", 54321:"data2"}}
to
[(12345,[(12345,"data"),(54321,"data2")])]"""
    temp = []
    for i in source.keys():
        temp.append((i, list(source[i].items())))
    return 

# if i[:-5] == "force_ss_list" or i[:-5] == "PollViews" or i[:-5] == "PersistentViews" or i[:-5] == "welcome_id_list" or i[:-5] == "steam_server_list" or i[:-5] == "role_keeper":

class Converter:
    def steam_server_list(source: dict) -> list:
        # {guild_id: {"value": 1, "1_ad": ("localhost", 80), "1_nm": "testserver"}}
        tmp = []
        for key, value in source.items():
            tmps = [key, [ ["value", int(value["value"])], ] ]
            svalue = int(value["value"])
            for i in range(svalue):
                tmps[1].append([f"{i+1}_ad", value[f"{i+1}_ad"]])
                tmps[1].append([f"{i+1}_nm", value[f"{i+1}_nm"]])
            tmp.append(tmps)
        return tmp
    
    def force_ss_list(source: dict) -> list:
        # {guild_id: [channel_id, message_id]}
        tmp = []
        for key, value in source.items():
            tmp.append([int(key), value])
        return tmp
    
    def PollViews(source) -> list:
        return source
    
    def PersistentViews(source) -> list:
        return source
    
    def welcome_id_list(source) -> list:
        # {guild_id: channel_id}
        tmp = []
        for key, value in source.items():
            tmp.append([int(key), value])
        return tmp
    
    def role_keeper(source) -> list:
        # {guild_id: {"rk": 1, member_id: [role_ids...]}}
        tmp = []
        for key, value in source.items():
            tmps = [key, [["rk", int(value["rk"])]]]
            for member_id, roles in value.items():
                if member_id == "rk":
                    continue
                tmps[1].append([member_id, roles])
            tmp.append(tmps)
        return tmp


