import discord
from discord.ext import commands
from discord import app_commands

import sqlite3
from time import sleep
import ast
import datetime

class focus( commands.Cog ):

    bot : commands.Bot
    db : sqlite3.Connection
    focus_role : int
    focusUsers : list[ dict[str, datetime.datetime] ]

    def __init__( self, bot ):
        super().__init__()
        self.bot = bot
        self.db = sqlite3.connect( "focus.db" )
        # 集中ロール
        # debug
        # self.focus_role = 1257999420595769476
        # product
        self.focus_role = 1149630562395496519
        self.focusUsers : list[ dict[str, datetime.datetime] ] = []

        # テーブルがなければ作成
        cursor = self.db.cursor()
        cursor.execute( "CREATE TABLE IF NOT EXISTS focus ( id BIGINT(20) PRIMARY KEY, time FLOAT )" )
        self.db.commit()
    
    focus = app_commands.Group(name="focus", description="フォーカス機能")


    @focus.command(name="start", description="フォーカス機能を有効にします")
    async def give_role(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(interaction.guild.id)
        member = guild.get_member(interaction.user.id)
        role = guild.get_role(self.focus_role)
        if role in member.roles:
            await interaction.response.send_message('既に集中モードが有効です。</focus_end:1156164406246387773>から集中モード終了してください。', ephemeral=True)
        else:
            await member.add_roles(role, reason="フォーカス機能開始")
            await interaction.response.send_message(f'{interaction.user.mention} が集中モードを開始しました！')
            message = await interaction.original_response()
            await message.add_reaction('👍')
            await self.forcus_user_add( member )

    @focus.command(name="end", description="フォーカス機能を無効にします")
    async def remove_role(self, interaction: discord.Interaction):
        guild = self.bot.get_guild(interaction.guild.id)
        member = guild.get_member(interaction.user.id)
        role = guild.get_role(self.focus_role)
        if role not in member.roles:
            await interaction.response.send_message('まだ集中モードが開始されていません。</focus_start:1156164406246387772>から集中モードを開始してください。', ephemeral=True)
        else:
            await member.remove_roles(role, reason="フォーカス機能終了")
            await interaction.response.send_message(f'{interaction.user.mention} が集中モードを終了しました！お疲れ様でした✨')
            message = await interaction.original_response()
            await message.add_reaction('👍')
            await self.focus_end( member )

    @focus.command(name="ranking", description="このサーバーで一番集中している人は誰でしょう？見てみましょう。")
    async def focus_ranking(self, interaction: discord.Interaction):
        focus_list = await self.get_focus_member_list()
        if len(focus_list) == 0:
            embed = discord.Embed(
                title="集中ランキング",
                description="このサーバーで一番集中している人は誰でしょう？",
                timestamp=datetime.datetime.now(),
                color=0x0695f9
            )
            embed.add_field(name="ランキングが存在しません", value="まだ誰も集中していません。（what）", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        else:
            # i love github copilot :)
            focus_list.sort(key=lambda x: x[1], reverse=True)
            embed = discord.Embed(
                title="集中ランキング", 
                description="このサーバーで一番集中している人は誰でしょう？", 
                timestamp=datetime.datetime.now(), 
                color=0x0695f9
            )
            # fieldを追加
            for i in range( len(focus_list) ):
                if i > 5: break
                member = self.bot.get_user(focus_list[i][0])
                embed.add_field(name=f"{i+1}位", value=f'{ f"<@{member.id}>" if ( member is not None ) else "不明なユーザー" } : {self.format_time(float(focus_list[i][1]))}', inline=False)
            
            await interaction.response.send_message(embed=embed)
        pass

    @staticmethod
    def format_time( seconds: float ) -> str:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{int(hours)}時間{int(minutes)}分{int(seconds)}秒"

    async def get_focus_member_list( self ) -> list[ dict[str, float] ]:
        cursor = self.db.cursor()
        cursor.execute( "SELECT * FROM focus" )
        result = cursor.fetchall()
        if result is None:
            return []
        else:
            return result
        pass

    async def focus_end( self, member: discord.Member ):
        timedelta = await self.math_focus_time( member )
        print( f"{member.display_name} さんの集中時間は { round(timedelta) } 秒です。")
        await self.forcus_user_remove( member )

        value = await self.get_focus_value( member )
        value += round(timedelta)
        await self.save_focus_value( member, value )

        pass

    async def math_focus_time(self, member: discord.Member) -> float:
        for user in self.focusUsers:
            if member.id in user:
                date = user[member.id]
                now = datetime.datetime.now()
                delta = now - date
                return delta.total_seconds()
            else: return 0
        
        return 0
    
    async def save_focus_value(self, member: discord.Member, value: float):
        cursor = self.db.cursor()
        cursor.execute( f"SELECT * FROM focus WHERE id = {member.id}" )
        result = cursor.fetchone()
        if result is None:
            cursor.execute( f"INSERT INTO focus (id, time) VALUES ({member.id}, {value})" )
        else:
            cursor.execute( f"UPDATE focus SET time = {value} WHERE id = {member.id}" )
        self.db.commit()
    
    async def get_focus_value(self, member: discord.Member) -> float:
        cursor = self.db.cursor()
        cursor.execute( f"SELECT * FROM focus WHERE id = {member.id}" )
        result = cursor.fetchone()
        if result is None:
            return 0
        else:
            return float( result[1] )

    async def forcus_user_add(self, member: discord.Member):
        date = datetime.datetime.now()
        self.focusUsers.append({ member.id: date })

    async def forcus_user_remove(self, member: discord.Member):
        if len(self.focusUsers) == 1:
            self.focusUsers = []
            return

        for i in len(self.focusUsers):
            if member.id in self.focusUsers[i]:
                self.focusUsers.pop(i)

        # what
        if len(self.focusUsers) == 0:
            self.focusUsers = []
            return
        
        # what
        self.focusUsers = self.focusUsers
        return

        



async def setup(bot: commands.Bot):
    await bot.add_cog( focus(bot) )
