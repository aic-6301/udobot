import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from ping3 import ping

class googleping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
@app_commands.command(name="google-ping")
@app_commands.describe()
@app_commands.guilds('1111683749969657938')
async def hoge(ctx:discord.Interaction):
    target = 'google.com' 
    result = int(ping(target, unit="ms")) 
    embed = discord.Embed(title="googleのping",description=str(result) + "ms", color=discord.Colour.from_rgb(128,255,0))
    await ctx.response.send_message(embed=embed)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(googleping(bot))