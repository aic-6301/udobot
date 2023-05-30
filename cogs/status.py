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
import time
from datetime import datetime

class status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_system_status.start()

    @tasks.loop(minutes=10)
    async def send_system_status(self):
        msg_id = await self.bot.status_msg.find_one({"guild_id": "1112710479874379837"}, {"_id":None})
        try:
            msg = await self.bot.get_channel(1112710479874379837).fetch_message(msg_id['message_id'])
        except Exception: 
            msg = await self.bot.get_channel(1112710479874379837).send(embed=discord.Embed(title="Loading..."))
            self.bot.status_msg.replace_one(
                {"guild_id": "1112710479874379837"},
                {
                    "message_id": msg.id
                }
            )
        target = 'google.com'

        result = int(ping(target, unit="ms"))
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

        # SSD使用率を取得
        ssd = psutil.disk_usage("C:")
        ssd_usage = round(ssd.used / ssd.total * 100, 1)

        # 起動時間を取得
        uptime = int(time.time() - psutil.boot_time())
        uptime_hours, uptime_minutes = divmod(uptime // 60, 60)
        uptime_message = f"{uptime_hours}時間{uptime_minutes}分"

        # メッセージの送信
        message = f"CPU使用率: {cpu_percent}%\n"
        message += f"メモリ使用率: {mem_percent}%\n"
        message += f"利用可能なメモリ容量: {mem_avail:.2f} GB\n"
        message += f"HDD使用率: {hdd_usage}%\n"
        message += f"SSD使用率: {ssd_usage}%\n"
        message += f"起動時間: {uptime_message}\n"
        embed = discord.Embed(title='サーバーステータス',description=f"CPU使用率:{cpu_percent}%\n メモリ使用率:{mem_percent} %\nメモリ空き領域:{mem_avail:.2f}GB\n HDD使用率:{hdd_usage}%\n 起動時間:{uptime_message}\n ping:{result}ms", color=discord.Colour.from_rgb(128,255,0), timestamp=datetime.now())
        await msg.edit(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(status(bot))
