import os
from pathlib import Path
from dotenv import load_dotenv
import traceback
from motor import motor_asyncio as motor
import requests
import xmltodict
import json


import discord
from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot as BotBase
from discord.ext import tasks



load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

class Bot(BotBase):
    def __init__(self):
        # Botのプレフィックスとインテントを指定
        super().__init__(
            command_prefix="/",
            intents=Intents.all())

    async def on_ready(self):
        # DB関係
        self.dbclient = motor.AsyncIOMotorClient("mongodb://localhost:27017")
        self.db = self.dbclient["udobot"]
        self.vc_info = self.db.vc_info
        self.status_msg = self.db.status_msg
        # Cogを'./cogs'からロード
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"Loaded cogs: cogs.{file[:-3]}")
                except Exception:
                    traceback.print_exc()
        await self.load_extension("jishaku") # jishakuをロード
        await self.change_presence(activity=discord.Game("色んな人によるこの鯖だけのぼっと"))
        print("起動したよ！！！")
        await jma_get.start()


@tasks.loop(minutes=1)
async def jma_get():
        with open("/data/data.json", "r") as f:
            id = json.load(f)["id"]
            print(id)
        response = requests.get('https://www.data.jma.go.jp/developer/xml/feed/extra.xml')
        if response.status_code == 200:
            to_json = xmltodict.parse(response.text)
            data = json.dumps(to_json,  ensure_ascii=False)
            if data["entry"][0]["id"] != id["id"]:
                print(data)
                embed = discord.Embed(title=data["entry"][0]["title"], description=data["entry"][0]["content"]["#text"], color=0x00ff00)
                await bot.get_channel("1114354017477345330").send(embed=embed)
                with open("/data/data.json", "w") as f:
                    json_data = json.loads(f)
                    json_data["id"] = data["entry"][0]["id"]
            else:
                return
        else:
            return

#実行する場所
if __name__ == "__main__":
    bot = Bot()
    bot.run(token=token)