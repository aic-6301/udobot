import discord
from discord.ext import commands, tasks
from discord import app_commands

import aiohttp
from datetime import datetime, timedelta
import json
import requests


class money(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(name="money", description="お金に関するコマンドです", guild_ids=["1111683749969657938"], guild_only=True)

    @group.command(name="debt", description="お金を借ります")
    @app_commands.describe(amount="何円借りるか(100円から10万円まで選択可能)", day="何日で返すか(1日から21日まで指定可能)")
    async def debt(self, interaction: discord.Interaction, amount: int, day: int):
        user_data = await self.get_debt_user(self, interaction)
        if user_data is None:
            if 100 < amount > 100000:
                if day > 21:
                    date = datetime.now() + timedelta(days=day)
                    date_fix = date.strftime("%Y%M%D%H%M%S")
                    json_data = {"user": interaction.user.id, "amount": amount, "day": f"{date_fix}"}
                    await self.bot.db_ch.send(json_data)
                    date_fi = discord.utils.format_dt(date, style="F")
                    async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                            await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': amount, 'reason': f'借金(返済額:{amount}, 返済期限：{date}日まで )'})
                    await interaction.response.send_message(f"付与が完了しました。{date_fi}までに、{amount}を</money repay:>で返してください。(自動返済機能はついていません。自分でお支払いください。\nまた、返済されなかった場合、自動的に引き落としされますのでご注意ください。)", ephemeral=True)
                else:
                    await interaction.response.send_message(f"21日以内に収めてください。", ephemeral=True)
            else:
                await interaction.response.send_message(f"100円から10万円までの金額を選択してください。", ephemeral=True)
        else:
            await interaction.response.send_message(f"お金を借りているようです。先にそちらをお返し下さい。", ephemeral=True)
    
    @group.command(name="repay", description="お金を返します")
    @app_commands.describe(amount="何円返すか(100円から10万円まで選択可能)")
    async def repay(self, interaction: discord.Interaction, amount: int):
        response = requests.get(self.bot.ub_url, headers=self.bot.ub_header)
        data_response = json.loads(response.text)
        msg = await self.get_debt_user(self, interaction)
        data = json.dump(msg.content)
        if data is None:
            await interaction.response.send_message("お金を借りていないようです。お金を借りているときに使用してください。")
            return
        if data_response["cash"] < amount:
            await interaction.response.send_message(f"お金が足りないようです。`bank`のほうにお金がある場合は、`%withdraw`でお金を`cash`のほうへ移してください。", ephemeral=True)
            return
        if data["amount"] < amount:
            repay_amount = amount - data["amount"]
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{repay_amount}", 'reason': f'返済(完済)'})
            await interaction.response.send_message(f"返済が完了しました。<#1116997608574038126>でご確認ください。\nまた、返済額が多かったので、返済分だけ引きました。", ephemeral=True)
        elif data["amount"] == amount:
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{amount}", 'reason': f'返済(完済)'})
            await msg.delete()
            return await interaction.response.send_message("返済が完了しました。<#1116997608574038126>でご確認ください。")
        elif data["amount"] > amount:
            leftover_amount = data["amount"] - amount
            leftover_date = datetime.now().strftime("%Y%M%D%H%M%S") - data["date"]
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{amount}", 'reason': f'返済(未完済)\n残り:{leftover_amount}'})
            await msg.edit({"user": interaction.user.id, "amount": leftover_amount, "day": f"{data['date']}"})
            return await interaction.response.send_message(f"返済は未完了です。残り{leftover_date}日で{leftover_amount}を返済してください。", ephemeral=True)


    @tasks.loop(minutes=30)
    async def check_debt(self):
        now_day = datetime.now().strftime("%Y%m%d")
        async for msg in self.bot.db_ch.history(limit=None):
            if now_day in msg.content:
                data = json.dumps(msg.content)
                async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{data["user"]}', json={'cash': f"-{data['amount']}", 'reason': f'返済(強制返済)'})


    async def get_debt_user(self, interaction: discord.Interaction):
        async for msg in self.bot.db_ch.history(limit=None):
            if interaction.user.id in msg.content:
                return msg
            else:
                return None


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(money(bot))