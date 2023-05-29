# This example requires the 'message_content' privileged intent to function.

import asyncio

import discord
import yt_dlp

from discord.ext import commands, tasks
from discord import app_commands
import shutil
import os
import datetime
# Suppress noise about console usage from errors
yt_dlp.utils.bug_reports_message = lambda: ''


que = asyncio.Queue()

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
ytdl_format_options_playlist = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)
ytdl_playlist = yt_dlp.YoutubeDL(ytdl_format_options_playlist)

player = None

duration = 0

duration_now = 0

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod # ダウンロード
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        global duration, duration_now
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream or play))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        duration = data['duration']
        duration_now = duration
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        file = shutil.move(filename, f"./music/{filename}")
        return cls(discord.FFmpegPCMAudio(file, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="music", description="音楽関係のコマンド", guild_ids=[1111683749969657938], guild_only=True)
    
    @tasks.loop(seconds=1) # 秒数計算
    async def timer(self):
        global duration_now
        if duration_now <= 0:
            self.timer.stop()
        duration_now = duration_now - 1
    
    async def play_song(self, interaction):
        global player
        if interaction.guild.voice_client.is_playing():
            return
        if que.empty():
            return
        player = await que.get()
        loop = asyncio.get_event_loop()
        interaction.guild.voice_client.play(player, after=lambda _:loop.create_task(self.play_song(interaction)))
        await interaction.channel.send(f"再生中: {player.title}")
        await self.timer.start()


    @group.command()
    async def play(self, interaction:discord.Interaction, *, url:str, stream:bool):
        if not interaction.guild.voice_client:
            await interaction.channel.connect()
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        try:
            os.mkdir("./music/")
        except Exception:
            pass
        player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=stream)
        await que.put(player)
        await interaction.response.send_message(f"キューに追加しました。", ephemeral=True)
        await self.play_song(interaction)
    
    @group.command()
    async def resume(self, interaction):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        interaction.guild.voice_client.resume()
        await interaction.response.send_message("再開しました。", ephemeral=True)
    
    @group.command()
    async def pause(self, interaction):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        interaction.guild.voice_client.pause()
        await interaction.response.send_message("一時停止します。", ephemeral=True)

    @group.command()
    async def volume(self, interaction:discord.Interaction, volume: int):
        """Changes the player's volume"""
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        if 0 > volume < 200:
            await interaction.response.send_message("0〜200の間のみ指定可能です。", ephemeral=True)
        interaction.guild.voice_client.source.volume = volume / 100
        await interaction.response.send_message(f"ボリューム：{volume}%")

    @group.command()
    async def stop(self, interaction:discord.Interaction):
        """Stops and disconnects the bot from voice"""
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        que.empty()
        await interaction.guild.voice_client.disconnect()
        await interaction.response.send_message("切断しました。")
        shutil.rmtree("./music/")

    @group.command(name="skip")
    async def skip(self, interaction:discord.Interaction):
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("曲を飛ばしました。")
        await self.play_song(interaction)
    
    @group.command(name="nowplaying")
    async def nowplaying(self, interaction:discord.Interaction):
        global player, duration, duration_now
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        if interaction.guild.voice_client.is_playing():
            await interaction.response.send_message(f"再生中: {player.title}\n{datetime.timedelta(seconds=duration_now)} / {datetime.timedelta(seconds=duration)}")
        else:
            await interaction.response.send_message("なにも再生されてないよ！")

    """@group.command() # わからん
    async def queue(self, interaction:discord.Interaction):
        global player, duration, duration_now
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        if que.empty():
            await interaction.response.send_message("キューは空です。")
        a=""
        i=0
        for f in await que.get():
            if i > 0:
                a= a + str(i) +":" + f.title + "\n"
            i = i+1
        await interaction.response.send_message(embed=discord.Embed(title="キューリスト", description=a, color=discord.Color.green()))"""

            
        
        
async def setup(bot):
    await bot.add_cog(Music(bot))