import discord
import os
import yt_dlp
from discord.ext import commands,tasks
from discord import app_commands
import asyncio # this is included with the latest versions, see issue https://github.com/Rapptz/discord.py/issues/375

song_queue = []

tasker = None


yt_dlp.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.duration = data.get('duration')
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False, play=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(f"ytsearch:{url}", download=not stream or play))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    group = app_commands

    @group.command(name='leave',description='チャンネルから切断します')
    @app_commands.guilds(1111683749969657938)
    async def leave(self, interaction:discord.Interaction):
        voice_client = interaction.guild.voice_client
        if not interaction.user.voice.channel == interaction.guild.voice_client.channel:
            await interaction.response.send_message("あなたはBotのはいっているチャンネルには参加していません")
        if voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("切断しました。")
        else:
            await interaction.response.send_message("どこのVCにも参加していません。", ephemeral=True)

    @group.command(name='play',description='曲を再生するよ')
    @app_commands.guilds(1111683749969657938)
    async def play(self, interaction:discord.Interaction, *, url:str):
        global song_queue
        voice = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)
        try :
            if (voice==None):
                if not interaction.user.voice.channel:
                    await interaction.response.send_message("まずVCに参加してください！", ephemeral=True)
                else:
                    channel = interaction.user.voice.channel
                    await channel.connect()
                voice_client = interaction.guild.voice_client
            if not voice_client.is_playing():
                song_queue.clear()

            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            if len(song_queue) == 0:
                await self.start_playing(interaction, player)
            else:
                song_queue.append(player)
                await interaction.response.send_message(f"{len(song_queue)-1}番目のキュー: {player.title}")
        except Exception as e:
            await interaction.response.send_message(f"エラー発生: {e}", ephemeral=True)

    async def start_playing(self, interaction:discord.Interaction, player):
        global song_queue
        song_queue.append(player)
        global tasker
        if(song_queue[0] == None):
            return
        i = 0
        while i < len(song_queue):
            try:
                interaction.guild.voice_client.play(song_queue[0], after=lambda e: print('Player error: %s' % e) if e else None)
                await interaction.channel.send(f"**現在再生中:** {song_queue[0].title}")
            except Exception as e:
                await interaction.channel.send(f"Something went wrong: {e}")
            #await asyncio.sleep(song_queue[0].duration)
            tasker = asyncio.create_task(self.coro(interaction,song_queue[0].duration))
            try:
                await tasker
            except asyncio.CancelledError:
                print("Task cancelled")
            if(len(song_queue) > 0):
                song_queue.pop(0)

    async def coro(interaction,duration):
        await asyncio.sleep(duration)

    @group.command(name='queue', description='キューの中身を表示するよ')
    @app_commands.guilds(1111683749969657938)
    async def queued(self,interaction:discord.Interaction):
        global song_queue
        a = ""
        i = 0
        for f in song_queue:
            if i > 0:
                a = a + str(i) +". " + f.title + "\n "
            i += 1
        await interaction.response.send_message("キュー内の音楽: \n " + a)

    @group.command(name='pause', description='この曲を一時停止するよ')
    @app_commands.guilds(1111683749969657938)
    async def pause(self, interaction:discord.Interaction):
        voice_client = interaction.message.guild.voice_client
        if voice_client.is_playing():
            await interaction.response.send_message("再生を一時停止しました。")
            await voice_client.pause()
        else:
            await interaction.response.send_message("今は何も再生されてないよ！！", ephemeral=True)
        
    @group.command(name='resume', description='再生を再開するよ')
    @app_commands.guilds(1111683749969657938)
    async def resume(self, interaction:discord.Interaction):
        voice_client = interaction.message.guild.voice_client
        if voice_client.is_paused():
            await interaction.response.send_message("再生を再開しました。")
            await voice_client.resume()
        else:
            await interaction.send("この前に何も再生してなかったみたい。曲を追加してね", ephemeral=True)

    @group.command(name='stop', description='曲を停止するよ')
    @app_commands.guilds(1111683749969657938)
    async def stop(self, interaction:discord.Interaction):
        global tasker
        global song_queue
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            song_queue.clear()
            voice_client.stop()
            try:
                tasker.cancel()
            except Exception:
                pass
            await interaction.response.send_message("再生停止しました。")
        else:
            await interaction.response.send_message("何も再生されてないよ！", ephemeral=True)

    @group.command(name='skip', description='曲をスキップするよ')
    @app_commands.guilds(1111683749969657938)
    async def skip(self, interaction:discord.Interaction):
        global tasker
        voice_client = interaction.guild.voice_client
        if voice_client.is_playing():
            voice_client.stop()
            tasker.cancel()
            await interaction.response.send_message("曲をスキップしました。")
        else:
            await interaction.response.send_message("何も再生されてないよ！", ephemeral=True)


async def setup(bot):
    await bot.add_cog(music(bot))