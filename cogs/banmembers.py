import discord
from discord.ext import commands
from discord import app_commands

from utils.Page import Simple


class banmembers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban_members", description="BANされたメンバーを表示します")
    async def ban_members(self, interaction:discord.Interaction):
        if interaction.user.guild_permissions.administrator == False:
            embed = discord.Embed(title="権限エラー", description="あなたはこのコマンドを実行する権限を所持していません。", color=0xff0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        banMembers : list[ discord.BanEntry ] = [ x async for x in interaction.guild.bans( limit=None ) ]
        if not banMembers:
            embed = discord.Embed(title="BANされたメンバーはいません", color=0x00ff00)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        pass

        embeds : list[discord.Embed] = []
        
        # inital embed
        embed = discord.Embed(title=f"BANされたメンバー｜計{len(banMembers)}人", color=0xff0000)
        pages = 1

        for i in range(len(banMembers)):
            embed.add_field(name="> ユーザー名", value=banMembers[i].user.name)
            embed.add_field(name="> ID", value=banMembers[i].user.id)
            embed.add_field(name="> BAN理由", value=banMembers[i].reason if banMembers[i].reason else "特に理由なし")

            if ( i + 1 ) % 6 == 0:
                embed.set_footer(text=f"Page {pages} - shizengakari bot")
                pages += 1
                embeds.append(embed)
                embed = discord.Embed(title=f"BANされたメンバー", color=0xff0000)
        
        embed.set_footer(text=f"Page {pages} - shizengakari bot")
        embeds.append(embed)
            
        if len( embed.fields ) > 0:
            embed.set_footer(text=f"Page {pages} - shizengakari bot")
            embeds.append(embed)

        await Simple( ephemeral=True , timeout=( 60 * 2 ) ).start( interaction, embeds )

    # 使ってない....
    def getPageLength( listObject : list[ discord.BanEntry ], devideBy : int = 10 ):
        result : float = len( listObject ) / devideBy
        return result if result.is_integer() else result + 1
    

async def setup(bot: commands.Bot):
    await bot.add_cog( banmembers(bot) )