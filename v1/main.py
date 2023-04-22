import asyncio
from genericpath import isfile
import os
import sys
import json
import database
import gspread
import HTTP_db
import pickle
import n_fc

pickle_fetch = {
    "all_reaction_list":"all_reaction_list",
    "autorole":"autorole",
    "bump_list":"bump_list",
    "ex_reaction_list":"autoreply",
    "force_ss_list":"auto_ss_list",
    "mc_server_list":"mc_server_list",
    "mod_list":"mod_list",
    "notify_token":"notify_token",
    "PersistentViews":"rolepanel_view",
    "PollViews":"pollpanel_view",
    "reaction_bool_list":"reaction_bool",
    "role_keeper":"role_keeper",
    "srtr_bool_list":"srtr_list",
    "steam_server_list":"steam_server_list",
    "welcome_id_list":"welcome_id_list",
    "welcome_message_list":"welcome_message_list",
    "pinMessage":"temporary"
}

google_fetch = {
    "dissoku":"dissoku_list",
    "remind":"remind_list"
}

async def main():
    if not os.path.exists("setting.json"):
        print(
            f"""\
設定ファイルが見つかりませんでした。
[temp.setting.json]を参考にして[setting.json]を作って下さい。"""
        )
        return
    SETTING = json.load(open("setting.json"))
    if "nira_bot_dir" not in SETTING:
        print(
            f"""\
設定ファイルが不正です。
[temp.setting.json]を参考にして[setting.json]を作ってください。"""
        )
        return
    BOT_DIR = SETTING["nira_bot_dir"]
    BOT_SETTING: dict = json.load(open(os.path.join(BOT_DIR, "setting.json")))
    DB_SECRET: str = os.path.join(BOT_DIR, "util/gapi.json")
    SPREADSHEET_KEY: str = str(BOT_SETTING["database"])
    if os.path.exists(os.path.join(BOT_DIR, "password")):
        PASSWORD = open(os.path.join(BOT_DIR, "password")).read()
    else:
        PASSWORD = None
    DB = database.database(DB_SECRET, SPREADSHEET_KEY, BOT_SETTING["database_data"]["address"], PASSWORD)
    DATABASE: gspread.Worksheet = DB.openSheet()
    CLIENT: HTTP_db.Client = DB.openClient()
    while True:
        print(
            """\
NIRA Database Manager v1.0

# 選択してください。
1. データのJSON化
2. データのTXT化
3. データの移行
4. 終了
"""
        )
        c = input("> ")
        if c == "1":
            while True:
                print(
                    """\
# 選択してください。
1. pickleデータ
2. Google Spread Sheet
3. HTTP_db
4. 戻る
"""
                )
                d = input("> ")
                if not os.path.exists("exports"):
                    os.mkdir("exports")
                if d == "1":
                    datas = os.listdir(BOT_DIR)
                    print("# Loading files...")
                    for i in datas:
                        ib = os.path.join(BOT_DIR, i)
                        if os.path.isfile(ib) and i[-5:] == ".nira":
                            with open(ib, "rb") as f:
                                print(f"n_fc.{i}", ib, sep="".join([" " for i in range(35-len(i))]))
                                exec(f"n_fc.{i[:-5]} = pickle.load(f)")
                                exec(f"""\
with open("exports/n_fc.{i[:-5]}.json", "w") as f:
    json.dump(n_fc.{i[:-5]}, f, indent=4)
""")
                    print("# All function loaded.")
                    print("# JSONファイル化は終了しました。[n_fc.*.json]")
                elif d == "2":
                    print("# Loading cloud cells...")
                    with open("exports/google.dissoku.json", "w") as f:
                        json.dump(DB.readValue(DATABASE, "B4"), f, indent=4)
                    with open("exports/google.remind.json", "w") as f:
                        json.dump(DB.readValue(DATABASE, "B5"), f, indent=4)
                    print("# All data pulled.")
                    print("# JSONファイル化は終了しました。[google.*.json]")
                elif d == "3":
                    print("# Connecting database server...")
                    print(CLIENT.url)
                    ALL_DATA = await CLIENT.get_all()
                    for key, value in ALL_DATA.items():
                        with open(f"exports/http_db.{key}.json", "w") as f:
                            json.dump(value, f, indent=4)
                    print("# JSONファイル化は終了しました。[http_db.*.json]")
                elif d == "4":
                    break
                else:
                    print("# 選択しなおしてください。")
                    continue
        elif c == "2":
            while True:
                print(
                    """\
# 選択してください。
1. pickleデータ
2. Google Spread Sheet
3. HTTP_db
4. 戻る
"""
                )
                d = input("> ")
                if not os.path.exists("exports"):
                    os.mkdir("exports")
                if d == "1":
                    datas = os.listdir(BOT_DIR)
                    print("# Loading files...")
                    for i in datas:
                        ib = os.path.join(BOT_DIR, i)
                        if os.path.isfile(ib) and i[-5:] == ".nira":
                            with open(ib, "rb") as f:
                                print(f"n_fc.{i}", ib, sep="".join([" " for i in range(35-len(i))]))
                                exec(f"n_fc.{i[:-5]} = pickle.load(f)")
                                exec(f"""\
with open("exports/n_fc.{i[:-5]}.txt", "w") as f:
    f.write(str(n_fc.{i[:-5]}))
""")
                    print("# All function loaded.")
                    print("# TXTファイル化は終了しました。[n_fc.*.txt]")
                elif d == "2":
                    print("# Loading cloud cells...")
                    with open("exports/google.dissoku.txt", "w") as f:
                        f.write(str(DB.readValue(DATABASE, "B4")))
                    with open("exports/google.remind.txt", "w") as f:
                        f.write(str(DB.readValue(DATABASE, "B5")))
                    print("# All data pulled.")
                    print("# TXTファイル化は終了しました。[google.*.txt]")
                elif d == "3":
                    print("# Connecting database server...")
                    print(CLIENT.url)
                    ALL_DATA = await CLIENT.get_all()
                    for key, value in ALL_DATA.items():
                        with open(f"exports/http_db.{key}.txt", "w") as f:
                            f.write(str(value))
                    print("# TXTファイル化は終了しました。[http_db.*.txt]")
                elif d == "4":
                    break
                else:
                    print("# 選択しなおしてください。")
                    continue
        elif c == "3":
            while True:
                print(
                    """\
# 選択してください。
1. pickleデータ->HTTP_db
2. Google Spread Sheet->HTTP_db
3. 戻る
"""
                )
                d = input("> ")
                if d == "1":
                    datas = os.listdir(BOT_DIR)
                    print("# Loading files...")
                    for i in datas:
                        ib = os.path.join(BOT_DIR, i)
                        if os.path.isfile(ib) and i[-5:] == ".nira":
                            with open(ib, "rb") as f:
                                print(f"n_fc.{i}", ib, pickle_fetch[i[:-5]], sep="\t|\t")
                                exec(f"n_fc.{i[:-5]} = pickle.load(f)")
                            print(i[:-5])
                            if i[:-5] == "force_ss_list" or i[:-5] == "PollViews" or i[:-5] == "PersistentViews" or i[:-5] == "welcome_id_list" or i[:-5] == "steam_server_list" or i[:-5] == "role_keeper":
                                await eval(f'CLIENT.post("{pickle_fetch[i[:-5]]}", database.Converter.{i[:-5]}(n_fc.{i[:-5]}))')
                            elif eval(f"n_fc.{i[:-5]}") == {}:
                                await eval(f'CLIENT.post("{pickle_fetch[i[:-5]]}", {[[]]})')
                            else:
                                await eval(f'CLIENT.post("{pickle_fetch[i[:-5]]}", database.dictToList(n_fc.{i[:-5]}))')
                    print("# Data loaded.")
                elif d == "2":
                    
                    pass
                elif d == "3":
                    break
                else:
                    print("# 選択しなおしてください。")
                    continue
        elif c == "4":
            print("# See you again...")
            return
        else:
            print("# 選択しなおしてください。")
            continue



if __name__ == "__main__":
    asyncio.run(main())
