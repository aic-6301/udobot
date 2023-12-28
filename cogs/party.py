import discord
from discord.ext import commands
from discord import app_commands

import json
import datetime

class joiner(discord.ui.View):
    def __init__(self):
        super().__init__(
            timeout=None
        )
        self.embed_value = None
        self.add_item(discord.ui.Button(label="参加", emoji="<:Blob_join:1168831929567674418>", style=discord.ButtonStyle.green, custom_id="join"))

class creater(discord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="パーティー作成",
            timeout=None
        )
        self.value=None

        self.name = discord.ui.TextInput(
            label="名前",
            style=discord.TextStyle.short,
            placeholder="まいくら",
            required=True
        )
        self.time = discord.ui.TextInput(
            label="開始時刻",
            style=discord.TextStyle.short,
            placeholder="19時",
            required=True
        )
        self.users = discord.ui.TextInput(
            label="人数 (数字のみ￤0~100人まで)",
            style=discord.TextStyle.short,
            placeholder="0~100",
            max_length=3,
            required=True
        )
        self.add_item(self.name)
        self.add_item(self.time)
        self.add_item(self.users)
    
    async def on_submit(self, interaction:discord.Interaction):
        embed = discord.Embed(title=f"募集:{self.name.value}", description=f"{interaction.user.mention}が{self.name.value}を募集中です！", timestamp=datetime.datetime.now())
        embed.add_field(name="開始時刻", value=f"{self.time.value}", inline=False)
        embed.add_field(name="最大人数", value=f"{self.users.value}人", inline=False)
        embed.add_field(name="参加者", value=f"{interaction.user.mention}", inline=False)
        embed.add_field(name="", value=f"📢 </game:1169850101410308116> で参加者を募集！", inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        await interaction.channel.send(embed=embed, view=joiner())
        self.stop()
        await interaction.response.send_message("作成しました！", ephemeral=True)

class party(commands.Cog):
    def __init__(self, client):
        self.bot = client
        self.embed_value = None
        
    @app_commands.command(name="game", description="ゲームを募集します")
    async def p_create(self, interaction:discord.Interaction):
        await interaction.response.send_modal(creater())

    @commands.Cog.listener()
    async def on_interaction(self, inter:discord.Interaction):
        try:
            if inter.data['component_type'] == 2:
                await self.on_button_click(inter)
            elif inter.data['component_type'] == 3:
                await self.on_dropdown(inter)
        except KeyError:
            pass
    
    async def on_button_click(self, interaction:discord.Interaction):
        custom_id = interaction.data["custom_id"]
        if custom_id == "join":
            ori_msg = interaction.message
            val_list = ori_msg.embeds[0].fields[2].value.split("\n")
            if not interaction.user.mention in val_list:
                embed = ori_msg.embeds[0]
                print(embed)
                embed_dict = embed.to_dict()
                print(embed_dict)

                self.embed_value = embed_dict["fields"][2]["value"]
                print(embed_dict)
                em = embed.set_field_at(2, name="参加者", value=f"{self.embed_value}\n{interaction.user.mention}")
                await ori_msg.edit(embed=embed)
                await interaction.response.send_message("参加しました！",ephemeral=True)
            else:
                await interaction.response.send_message("すでに参加しています！", ephemeral=True)
            self.embed_value = None
        elif custom_id == "create":
            await interaction.response.send_modal(creater())

    async def on_dropdown(self,inter:discord.Interaction):
        custom_id = inter.data["custom_id"]
        select_values = inter.data["values"]
        print(custom_id)
        await inter.response.send_message("Select!",ephemeral=True)

async def setup(bot):
    await bot.add_cog(party(bot))