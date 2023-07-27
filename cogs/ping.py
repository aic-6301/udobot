from discord.ext import commands
from discord import app_commands
import discord
from ping3 import ping as pinge
import re

class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Discordのwebsocketのping測定/サイトへのping測定を行います")
    @app_commands.describe(site="サイトへのpingを試行します")
    @app_commands.guilds(1111683749969657938)
    async def ping(self, interaction:discord.Interaction, site: str =None):
        if site is None:
            await interaction.response.send_message(embed=discord.Embed(title=f":ping_pong:Pong!", 
            description=f"{round(self.bot.latency *1000)}ms" , color=discord.Colour.from_rgb(128,255,0)))
        else:
            try:
                target = site.replace("https://", "") # https://を置き換える
            except Exception:
                pass
            try:
                result = int(pinge(target, unit="ms")) # pingを実行
                if int(result) <= 0:
                    await interaction.response.send_message("失敗しました。本当にそのサイトは存在するか調べてください。", ephemeral=True)
                else:
                    await interaction.response.send_message(embed=discord.Embed(title=f'"{target}"へのping',description=str(result) + "ms", color=discord.Colour.from_rgb(128,255,0)))
            except Exception:
                await interaction.response.send_message("失敗しました。本当にそのサイトは存在するか調べてください。", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ping(bot))