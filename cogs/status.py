from discord import app_commands
import discord
from ping3 import ping as ping
import discord.app_commands
from discord.ext import commands, tasks
from discord.utils import get 
from ping3 import ping #ping取得
import asyncio
from dotenv import load_dotenv
import psutil
import os
import time
from datetime import datetime

class status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_system_status.start()

    @tasks.loop(minutes=1)
    async def send_system_status(self):
        msg = await self.bot.get_channel(1112710479874379837).fetch_message(1113079189327843459)
        munesky_status = self.get_status_munesky(self)
        if munesky_status == 0:
            munesky = "<:online_status:1127193009746886656>起動中"
        else:
            if self.bot.munesky_maintenance is False:
                munesky = "<:offline_status:1127193017762189322>ダウン"
                await self.bot.get_channel(1111683751014051962).send("<@&964887498436276305> <@&603948934087311360>", embed=discord.Embed(title="むねすきー稼働情報", 
                                                                                                                                          description=f"むねすきーがダウンしていることを{discord.utils.format_dt(datetime.now())}に検知しました。\n復旧作業が必要な場合は復旧をしてください。"))
            elif self.bot.munesky_maintenance == True:
                munesky = "<:dnd_status:1127193014775853127>メンテナンス中"
        # CPU使用率を取得
        cpu_percent = psutil.cpu_percent(interval=1)

        # メモリ使用率を取得
        mem = psutil.virtual_memory()
        mem_percent = mem.percent

        # メモリの利用可能な容量を取得
        mem_avail = mem.available / 1024 / 1024 / 1024

        # HDD使用率を取得
        hdd = psutil.disk_usage("/")
        hdd_usage = round(hdd.used / hdd.total * 100, 1)

        # 起動時間を取得
        uptime = int(time.time() - psutil.boot_time())
        uptime_hours, uptime_minutes = divmod(uptime // 60, 60)
        uptime_message = f"{uptime_hours}時間{uptime_minutes}分"

        embed = discord.Embed(title='サーバーステータス',description=f"CPU使用率:{cpu_percent}%\n メモリ使用率:{mem_percent} %\nメモリ空き領域:{mem_avail:.2f}GB\n HDD使用率:{hdd_usage}%\n 起動時間:{uptime_message}\n むねすきー稼働情報:{munesky}", color=discord.Colour.from_rgb(128,255,0), timestamp=datetime.now())
        await msg.edit(embed=embed)

    def get_status_munesky(self):
        status = os.system("systemctl is-active --quiet misskey")
        if status == "0":
            return 0
        else:
            return 768
    
    

async def setup(bot: commands.Bot):
    await bot.add_cog(status(bot))
