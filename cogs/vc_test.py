import discord
from discord.ext import commands

class kimigayo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="join")
    async def vc_join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel.")
            return

        if ctx.voice_client is not None:
            await ctx.send("I'm already connected to a voice channel.")
            return

        channel = ctx.author.voice.channel
        await channel.connect()

        voice_client = ctx.voice_client
        audio_source = discord.FFmpegPCMAudio('./music/kimigayo.mp3')
        voice_client.play(audio_source)

    @commands.command(name="ace")
    async def vc_join(self, ctx):

        voice_client = ctx.voice_client
        audio_source = discord.FFmpegPCMAudio('./music/ace.mp3')
        voice_client.play(audio_source)


    @commands.command(name="leave")
    async def vc_leave(self, ctx):
        if ctx.voice_client is not None:
            await ctx.voice_client.disconnect()

    @commands.command(name="stop")
    async def vc_stop(self, ctx):
        if ctx.voice_client is not None:
            ctx.voice_client.stop()

async def setup(bot):
    await bot.add_cog(kimigayo(bot))
