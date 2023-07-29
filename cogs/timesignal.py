import discord
from discord.ext import commands, tasks
from discord import app_commands

from datetime import datetime


class timesignal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timesignal.start()
        self.embed = None

    @tasks.loop(seconds=60)
    async def timesignal(self):
        hour = datetime.now().strftime("%H")
        minute = datetime.now().strftime("%M")
        if minute == "00":
            self.embed = discord.Embed(title="時報", description=f"{hour}をお知らせします")
            if hour == "00":
                self.embed.add_field(name="日付が変わったよ！！", value=f"今日は{datetime.now().strftime('%m月%d日')}です")
            if hour == "12":
                self.embed.add_field(name="おひるだよ！！！", value=f"寝てる人はそろそろ起きよう！！\n昼ご飯も食べようね")
            if hour == "15":
                self.embed.add_field(name="おやつ！！！", value=f"おやつのじかんだよ！！")
            if hour == "23":
                self.embed.add_field(name="夜だよ！！", value=f"そろそろ寝ようね")
        
        await self.bot.get_channel(1112706780653424640).send(embed=self.embed)
        self.embed = None

    async def cog_unload(self):
        self.timesignal.stop()
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(timesignal(bot))