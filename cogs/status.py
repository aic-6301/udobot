from discord import app_commands
import discord
from ping3 import ping
from discord.ext import commands, tasks
from discord.utils import get 
import asyncio
from dotenv import load_dotenv
import psutil
import os
import time
from datetime import datetime

# コントロールボタン
class Controlbutton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="メンテナンス開始", style=discord.ButtonStyle.green, row=1)
    async def start_maintenance(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.munesky_maintenance = True
        await interaction.response.send_message("メンテナンスモードに切り替えました")
    
    @discord.ui.button(label="メンテナンス終了", style=discord.ButtonStyle.red, row=1)
    async def end_maintenance(self, interaction: discord.Interaction, button:discord.ui.Button):
        self.munesky_maintenance = False
        await interaction.response.send_message("通常モードに切り替えました")
class status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_system_status.start()
        self.message = None
        self.munesky_maintenance = False

    # cogを読み込んだ際に、ボタンのセットアップをする。
    async def cog_load(self):
        msg = await self.bot.get_channel(1127194229018472520).fetch_message(1127197198296297522)
        await msg.edit(embed=discord.Embed(title="むねすきー管理", description="メンテナンスモードの管理が可能です。メンテナンス開始＝停止時通知が飛びません。\nメンテナンス終了=通常モードなります"), view=Controlbutton())
        print("button ready")

    @tasks.loop(seconds=30)
    async def send_system_status(self):
        msg = await self.bot.get_channel(1145568259870044170).fetch_message(1145717456858534080)
        # TODO:きれいにする
        munesky_status = self.get_status_munesky() # munesky稼働情報を取得
        db_status = self.get_status_db() # postgresqlの稼働情報を取得
        if munesky_status == 0:
            munesky = "<:online_status:1145719512767934607>起動中"
            color = discord.Colour.from_rgb(128,255,0)
            if self.message:
                self.message.edit(embed=discord.Embed(title="むねすきー稼働情報", description="むねすきーが復活しました。"))
                self.message = None
        elif munesky_status or db_status == 768:
            if self.munesky_maintenance is False:
                munesky = "<:offline_status:1145719503997644800>ダウン"
                color = discord.Color.yellow()
                if self.message is None:
                    self.message = await self.bot.get_channel(1145593830998016070).send("<@&1111875162548220014>", embed=discord.Embed(title="むねすきー稼働情報", 
                    description=f"むねすきーがダウンしていることを{discord.utils.format_dt(datetime.now())}に検知しました。\n復旧作業が必要な場合は復旧をしてください。"))
            if self.munesky_maintenance is True:
                munesky = "<:dnd_status:1145719509181796445>メンテナンス中"

        # CPU使用率を取得
        cpu_percent = psutil.cpu_percent(interval=1)
        # メモリ使用率を取得
        mem = psutil.virtual_memory()
        mem_percent = mem.percent
        # メモリの利用可能な容量を取得
        mem_avail = mem.available / 1024 / 1024 / 1002
        # HDD使用率を取得
        hdd = psutil.disk_usage("/")
        hdd_usage = round(hdd.used / hdd.total * 100, 1)
        # 起動時間を取得
        uptime = int(time.time() - psutil.boot_time())
        uptime_hours, uptime_minutes = divmod(uptime // 60, 60)
        uptime_message = f"{uptime_hours}時間{uptime_minutes}分"

        embed = discord.Embed(title='サーバーステータス'
        ,description=f"CPU使用率:{cpu_percent}%\n メモリ使用率:{mem_percent} %\nメモリ空き領域:{mem_avail:.2f}GB\n HDD使用率:{hdd_usage}%\n 起動時間:{uptime_message}\n むねすきー稼働情報:{munesky}",
        color=color, timestamp=datetime.now())
        await msg.edit(embed=embed)


    # systemctlからmuneskyの稼働情報を取得
    def get_status_munesky(self):
        status = os.system("systemctl is-active misskey")
        if status == 0:
            return 0
        else:
            return 768

    # systemdからdbが起動してるか確認
    def get_status_db(self):
        status = os.system("systemctl is-active postgresql@13-main")
        if status == 0:
            return 0
        else:
            return 768
        

# cogがアンロードされたときにステータス更新を止める。
    async def cog_unload(self):
        self.send_system_status.stop()
        msg = await self.bot.get_channel(1145568259870044170).fetch_message(1145717456858534080)
        await msg.edit(embed=discord.Embed(title="サーバーステータス",description="更新停止中", timestamp=datetime.now(), color=discord.Color.red()))
    
    

async def setup(bot: commands.Bot):
    await bot.add_cog(status(bot))
