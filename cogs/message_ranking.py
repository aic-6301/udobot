import discord
from discord.ext import commands, tasks
from discord import app_commands

from datetime import datetime, timedelta
import json


class messageranking(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.count = {}
        self.send_ranking.start()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        async for msg in self.bot.get_channel(1199716693874851931).history(after=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=9)):
            if message.author.id in msg.content:
                data = json.dumps(msg.content)
                data.update({"count": data["count"]+1})
                await msg.edit(data)
            else:
                await self.bot.get_channel(1199716693874851931).send(f"{'author': message.author.id, 'count': 1}")
    
    @tasks.loop(seconds=5)
    async def send_ranking(self):
        if datetime.now().strftime("%H:%M") == "00:00":
            try:
                if self.emb is None:
                    async for msg in self.bot.get_channel(1199716693874851931).history(after=datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=9)):
                        data = json.dumps(msg.content)
                        self.count[data["author"]] = (data["author"], data["count"])
                    ranking = sorted(self.count.items(), key=lambda x: x[1][1])
                    top_msg = "> 一番多く送ったメッセージ数ランキング"
                    for i, msg in enumerate(ranking):
                        rank_message += f"{i+1}位. <@{msg[1][0]}> {msg[1][1]}メッセージ"
                        if i == 10:
                            continue
                    embed = discord.Embed(title="メッセージランキングβ", description=rank_message, timestamp=datetime.now(), color=discord.Color.green()).set_footer(text="このランキングはベータです。不具合がある場合があります。")
                    self.emb = await self.bot.get_channel(1198993361152000112).send(embed=embed)
            except Exception as e:
                embed = discord.Embed(title="エラー", description=f"エラーが発生しました。 \n `{e}`", color=discord.Color.red())
        else:
            self.emb = None    
                    

async def setup(bot: commands.Bot):
    await bot.add_cog(messageranking(bot))