from discord.ext import commands
from discord import app_commands
import discord
from ping3 import ping as pinge
import re

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="サーバーの状態を表示します")
    @app_commands.guilds(1111683749969657938)
    async def ping(self, interaction:discord.Interaction,):
            target = 'google.com'

            result = int(pinge(target, unit="ms"))
            if int(result) <= 0:
                await interaction.response.send_message("失敗しました。", ephemeral=True)
            interaction.response.send_message(embed=discord.Embed(title=f'"{target}"へのping',description=str(result) + "ms", color=discord.Colour.from_rgb(128,255,0)))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ping(bot))