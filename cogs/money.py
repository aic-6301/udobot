import ast
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
        self.check_debt.start()

    group = app_commands.Group(name="money", description="お金に関するコマンドです", guild_ids=[1111683749969657938], guild_only=True)

    @group.command(name="debt", description="お金を借ります")
    @app_commands.describe(amount="何円借りるか(100円から10万円まで選択可能)", day="何日で返すか(1日から21日まで指定可能)")
    async def debt(self, interaction: discord.Interaction, amount: int, day: int):
        user_data = await self.get_debt_user(interaction)
        if user_data is None:
            if 100 <= amount <= 100000:
                if day <= 21:
                    await interaction.response.defer() # interactionの送信を送れることを送信(考え中に変える)
                    date = datetime.now() + timedelta(days=day)
                    date_fix = date.strftime("%Y/%m/%d")
                    json_data = {"user": interaction.user.id,'amount': amount, "day": date_fix}
                    await self.bot.db_ch.send(json_data)
                    date_fi = discord.utils.format_dt(date, style="d")
                    async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                            await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': amount, 'reason': f'借金(返済額:{amount}, 返済期限：{date_fix}日まで )'})
                    await interaction.followup.send(f"付与が完了しました。{date_fi}の0:00までに、{amount}を</money repay:1134815192769896451>で返してください。(自動返済機能はついていません。自分でお支払いください。\nまた、返済されなかった場合、自動的に引き落としされますのでご注意ください。)", delete_after=10)
                    # 遅らせたものを送信する(自分だけ表示は不可なため、10秒後に削除)
                else:
                    await interaction.response.send_message("21日以内に収めてください。", ephemeral=True)
            else:
                await interaction.response.send_message(f"100円から10万円までの金額を選択してください。\nselected_money={amount}", ephemeral=True)
        else:
            await interaction.response.send_message("お金を借りているようです。先にそちらをお返し下さい。", ephemeral=True)

    @group.command(name="repay", description="お金を返します")
    @app_commands.describe(amount="何円返すか(100円から10万円まで選択可能)")
    async def repay(self, interaction: discord.Interaction, amount: int):
        response = requests.get(f"{self.bot.ub_url}{interaction.user.id}", headers=self.bot.ub_header)
        data_response = json.loads(response.text)
        print(data_response)
        msg = await self.get_debt_user(interaction)
        if msg is None:
            await interaction.response.send_message("お金を借りていないようです。お金を借りているときに使用してください。", ephemeral=True)
            return
        load_json = ast.literal_eval(msg.content)
        js = json.dumps(load_json)
        data = json.loads(js)
        print(data)
        if data_response["cash"] < amount:
            await interaction.response.send_message("お金が足りないようです。`bank`のほうにお金がある場合は、`%withdraw`でお金を`cash`のほうへ移してください。", ephemeral=True)
            return
        if data['amount'] < amount:
            await interaction.response.defer() # interactionの送信を送れることを送信(考え中に変える)
            repay_amount = data['amount']
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{repay_amount}", 'reason': '返済(完済)'})
            await interaction.followup.send("返済が完了しました。<#1116997608574038126>でご確認ください。\nまた、返済額が多かったので、返済分だけ引きました。", delete_after=10)
            # 遅らせたものを送信する(自分だけ表示は不可なため、10秒後に削除)
        elif data['amount'] == amount:
            await interaction.response.defer() # interactionの送信を送れることを送信(考え中に変える)
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{amount}", 'reason': '返済(完済)'})
            await msg.delete()
            await interaction.followup.send("返済が完了しました。<#1116997608574038126>でご確認ください。", delete_after=10)
            # 遅らせたものを送信する(自分だけ表示は不可なため、10秒後に削除)
        elif data['amount'] > amount:
            await interaction.response.defer() # interactionの送信を送れることを送信(考え中に変える)
            leftover_amount = data['amount'] - amount
            async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{interaction.user.id}', json={'cash': f"-{amount}", 'reason': f'返済(未完済)\n残り:{leftover_amount}'})
            data.update({"amount": leftover_amount})
            send_data = json.dumps(data)
            await msg.edit(content=send_data)
            await interaction.followup.send(f"{amount}円を返済しました。{datetime.strftime(data['day'], '%y/%m/%d')}までに{leftover_amount}を返済してください。", delete_after=10)
            # 遅らせたものを送信する(自分だけ表示は不可なため、10秒後に削除)


    @tasks.loop(seconds=30)
    async def check_debt(self):
        now_day = datetime.now().strftime("%Y/%m/%d")
        async for msg in self.bot.db_ch.history(limit=None):
            if now_day in msg.content:
                data = json.dumps(msg.content)
                async with aiohttp.ClientSession(headers=self.bot.ub_header) as session:
                    await session.patch(url=f'{self.bot.ub_url}{data["user"]}', json={'cash': f"-{data['amount']}", 'reason': '返済(強制引き落とし)'})
                await self.bot.get_channel(1111683751014051962).send(f"<@{data['user']}> 返済期間が過ぎたため、強制的に引き落としが行われました。\n引き落とし金額：{data['amount']}, 引き落とし時刻:{discord.utils.format_dt(datetime.now(), style='F')}({discord.utils.format_dt(datetime.now(), style='R')})")
            else:
                pass


    async def get_debt_user(self, interaction: discord.Interaction):
        async for msg in self.bot.db_ch.history(limit=None):
            try:
                if str(interaction.user.id) in msg.content:
                    return msg
            except:
                return None



async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(money(bot))
