import os
from pathlib import Path
from dotenv import load_dotenv
import traceback

import discord
from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot as BotBase

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")

class Bot(BotBase):
    def __init__(self):
        # Botのプレフィックスとインテントを指定
        super().__init__(
            command_prefix="/",
            intents=Intents.all())

    async def on_ready(self):
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


#実行する場所
if __name__ == "__main__":
    bot = Bot()
    bot.run(token=token)