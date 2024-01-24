import os
from pathlib import Path
from dotenv import load_dotenv
import traceback
# discord lib
import discord
from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot as BotBase

load_dotenv()
token = os.getenv("DISCORD_BOT_TOKEN")
unb_token = os.getenv("UNB_TOKEN")



class Bot(BotBase):
    def __init__(self):
        # Botのプレフィックスとインテントを指定
        super().__init__(
            command_prefix="/",
            intents=Intents.all())

    async def on_ready(self):
        # DB関係
        bot.db_ch = bot.get_channel(1134715149215866950)

        # お金関係
        bot.ub_url = 'https://unbelievaboat.com/api/v1/guilds/1198993360694816788/users/'
        bot.ub_header = {"Authorization": unb_token, "Accept": "application/json"}


        # Cogを'./cogs'からロード
        for file in os.listdir(os.getenv("COG_FOLDER")):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    print(f"Loaded cogs: cogs.{file[:-3]}")
                except Exception:
                    traceback.print_exc()
        await self.load_extension("jishaku") # jishakuをロード
        await self.change_presence(activity=discord.Game("色んな人によるこの鯖だけのぼっと"))
        await bot.tree.sync()
        print("起動したよ！！！")



#実行する場所
if __name__ == "__main__":
    bot = Bot()
    bot.run(token=token)
