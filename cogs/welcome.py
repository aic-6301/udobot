import discord
from discord.ext import commands

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.bot:
            await member.add_roles(1111687907892269067) # botロールを付与
        else:
            await self.bot.get_channel(1111705826663616623).send(embed=discord.Embed(
                title="ユーザー入室", 
                description="このユーザーについての情報です。", 
                color=member.accent_color)
                .add_field(name="名前", value=member.name)
                .add_field(name="登録日時", value=member.created_at)
                )
            
async def setup(bot):
    await bot.add_cog(welcome(bot))
    
