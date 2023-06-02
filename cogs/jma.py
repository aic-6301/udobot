import discord
from discord.ext import commands, tasks
import json
import xmltodict
import requests

class jma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.jma_get.start()

    @tasks.loop(minutes=1)
    async def jma_get(self):
        response = requests.get('https://www.data.jma.go.jp/developer/xml/feed/extra.xml')
        to_json = xmltodict.parse(response.text)
        data = json.dumps(to_json, encoding="utf-8", ensure_ascii=False)
        with open("./data/data.json", "w", encoding="utf-8") as f:
            f.write(data)

async def setup(bot):
    await bot.add_cog(jma(bot))