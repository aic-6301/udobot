import discord
from discord.ext import commands

class welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 1041988027582521404:
            if member.bot:
                await member.add_roles(self.bot.get_guild(1041988027582521404).get_role(1092785086551818291)) # botロールを付与
            else:
                await self.bot.get_channel(1158704822711767080).send(embed=discord.Embed(
                    title="ユーザー入室", 
                    description="このユーザーについての情報です。", 
                    color=member.accent_color)
                    .add_field(name="名前", value=member.name)
                    .add_field(name="登録日時", value=member.created_at)
                    )
        elif member.guild.id == 1199714895848022026:
            if member.bot:
                await member.add_roles(self.bot.get_guild(1198993360694816788).get_role(1199640973165207612)) # botロールを付与
            else:
                await self.bot.get_channel(1158704822711767080).send(embed=discord.Embed(
                    title="ユーザー入室", 
                    description="このユーザーについての情報です。", 
                    color=discord.Color.blue())
                    .add_field(name="名前", value=member.name)
                    .add_field(name="登録日時", value=member.created_at)
                    )

async def setup(bot):
    await bot.add_cog(welcome(bot))

