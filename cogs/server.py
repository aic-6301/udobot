import discord
from discord.ext import commands
from discord import app_commands


class server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="color_role")
    async def color_role(self, ctx, color:discord.colour):
        role = await self.bot.guild.create_role(name=color, color=color)
        await role.edit_role_positions(positions={role: 5})
        await ctx.author.add_roles(role)
        await ctx.reply("追加したよ")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(server(bot))