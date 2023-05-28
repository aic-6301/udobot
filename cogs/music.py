# This example requires the 'message_content' privileged intent to function.

import asyncio

import discord
import yt_dlp

from discord.ext import commands, tasks
from discord import app_commands
import shutil
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

ffmpeg_options = {
    'options': '-vn',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

player = None

duration = 0

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        global duration
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream or play))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        duration = data['duration']
        filename = data['url'] if stream else ytdl.prepare_filename(data)
        file = shutil.move(filename, f"./music/{filename}")
        return cls(discord.FFmpegPCMAudio(file, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="music", description="音楽関係のコマンド", guild_ids=[1111683749969657938], guild_only=True)
    
    @tasks.loop(seconds=1)
    async def timer(self):
        global duration
        if duration <= 0:
            self.timer.stop()
        duration = duration - 1
    
    async def play_song(self, interaction, stream=None):
        global player
        if interaction.guild.voice_client.is_playing():
            return
        if que.empty():
            return
        result = await que.get()
        url = result
        if stream is True:
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
        else:
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
        loop = asyncio.get_event_loop()
        interaction.guild.voice_client.play(player, after=lambda _:loop.create_task(self.play_song(interaction, url)))
        await interaction.channel.send(f"再生中: {player.title}")
        await self.timer.start()


    @group.command()
    async def play(self, interaction:discord.Interaction, *, url:str, stream:bool):
        if not interaction.guild.voice_client:
            await interaction.channel.connect()
        elif interaction.guild.voice_client is not None and interaction.guild.voice_client.channel != interaction.channel:
            await interaction.response.send_message("すでに別のチャンネルに接続しています！")
        await que.put(url)
        await interaction.response.send_message(f"キューに追加しました。", ephemeral=True)
        await self.play_song(interaction, stream)
        

    @group.command()
    async def volume(self, interaction:discord.Interaction, volume: int):
        """Changes the player's volume"""

        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていません！")
        if 0 > volume < 200:
            await interaction.response.send_message("0〜200の間のみ指定可能です。", ephemeral=True)
        interaction.guild.voice_client.source.volume = volume / 100
        await interaction.response.send_message(f"ボリューム：{volume}%")

    @group.command()
    async def stop(self, interaction:discord.Interaction):
        """Stops and disconnects the bot from voice"""
        que.empty()
        await interaction.guild.voice_client.disconnect()
        await shutil.rmtree("/music/")
        await interaction.response.send_message("切断しました。")

    @group.command(name="skip")
    async def skip(self, interaction:discord.Interaction):
        interaction.guild.voice_client.stop()
        await interaction.response.send_message("曲を飛ばしました。")
        await self.play_song(interaction)
    
    @group.command(name="nowplaying")
    async def nowplaying(self, interaction:discord.Interaction):
        global player, duration
        if interaction.guild.voice_client is None:
            return await interaction.response.send_message("VCに接続されていないよ！")
        if interaction.guild.voice_client.is_playing():
            await interaction.response.send_message(f"再生中: {player.title}, 残り{duration}秒")
        else:
            await interaction.response.send_message("なにも再生されてないよ！")



async def setup(bot):
    await bot.add_cog(Music(bot))