import discord
from discord.ext import commands, tasks
from discord import app_commands

from datetime import datetime, time, timedelta


class onecomment(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.messages = {}
        self.ranking.start()
        self.embed = None
        self.data = {}


    async def geter(self, message):
        if message.author.id in self.messages:
            return 1
        else:
            return None



    def is_time_in_range(self, start, end, x):
        """Return true if x is in the range [start, end]"""
        if start <= end:
            return start <= x <= end
        else:
            return start <= x or x <= end

    @commands.Cog.listener()
    async def on_message(self, message:discord.Message):
        if message.channel == self.bot.get_channel(1198993361152000112):
            if message.author.bot:
                return
            result = await self.geter(message)
            if result is not None:
                #print("added")
                return
            msg_time = message.created_at + timedelta(hours=9)
            if self.is_time_in_range(time(23, 59), time(0, 1), msg_time.time()):
                self.messages[message.author.id] = (message.author.id, (message.created_at + timedelta(hours=9)).strftime('%H%M%S%f'), message.id)
                await self.bot.get_channel(1180147591338537090).send(message.author.id)
            else:
                # print("not time")
                return

    @tasks.loop(seconds=15)
    async def ranking(self):
        channel = self.bot.get_channel(1198993361152000112)
        now = datetime.now()
        start_day = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        if now.strftime("%H:%M") == "00:01":
            if self.embed is None:
                try:
                    print("いちこめらんきんぐ集計中...")
                    sorted_messages = sorted(self.messages.items(), key=lambda x: abs(int(x[1][1]) - int(start_day.strftime("%H%M%S%f"))))
                    rank_message = "> 0:00に一番近く送ったメッセージランキング\n"
                    for i, msg in enumerate(sorted_messages):
                        rank_message += f"{i+1}位. <@{msg[1][0]}> 送信時間:{msg[1][1][:2]}:{msg[1][1][2:4]}:{msg[1][1][4:6]}.{msg[1][1][7:]} [Link](https://discord.com/channels/867677146260439050/867692303664807946/{msg[1][2]})\n"
                    self.embed = await channel.send(embed=discord.Embed(title="一コメランキング", description=rank_message, timestamp=now,color=discord.Color.blue()
                                                                        ).set_footer(text="この機能はβ版です。不具合等あればあいしぃーまで。" ))
                    await self.bot.get_channel(1198993361152000112).send(self.messages)
                    self.messages = {}
                except Exception as e:
                    self.embed = await channel.send(content="<@964887498436276305>", embed=discord.Embed(title="エラー", description=f"送信する際にエラーが発生しました。\nエラー内容：`{e}`", color=discord.Color.red()))
                    
            else:
                print("sended")
        elif now.strftime("%H:%M") == "23:59":
            if self.embed is None:
                self.embed = await channel.send(embed=discord.Embed(title="一コメランキング", description=f"計測中...結果は重複回避のため{discord.utils.format_dt((now+timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0))}に送信されます。", color=discord.Color.blue()))

        else:
            # print("not time (tasks)")
            self.embed = None
            #print(self.embed)


    async def cog_unload(self):
        self.ranking.stop()
async def setup(bot: commands.Bot):
    await bot.add_cog(onecomment(bot))