import discord
from discord.ext import commands, tasks
import json
import xmltodict
import requests

class jma(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(minutes=1)
    async def jma_get(self):
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
                await self.bot.get_channel("1114354017477345330").send(embed=embed)
                with open("/data/data.json", "w") as f:
                    json_data = json.loads(f)
                    json_data["id"] = data["entry"][0]["id"]
            else:
                return
        else:
            return
        
    @commands.Cog.listener()
    async def on_ready(self):
        self.jma_get.start()
    
    async def cog_unload(self):
        self.jma_get.stop()

async def setup(bot):
    await bot.add_cog(jma(bot))