import discord
from discord.ext import commands
from discord import app_commands
import random
import datetime


class reget(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__()
        self.bot = bot
        self.user_id = user_id
        self.agent = ["フェニックス", "ジェット", "スカイ", "ネオン", "ヨル", "サイファー", "キルジョイ", "チェンバー", "セージ", "KAY/O", "オーメン", "ブリーチ", "ソーヴァ", "アイソ", "ブリーチ", 
              "キルジョイ", "ゲッコー", "ハーバー", "アストラ", "ヴァイパー", "ブリムストーン", "デットロック", "フェイド"]
        self.weapon = ["クラシック", "ショーティー", "フレンジー", "ゴースト", "シェリフ", "スティンガー", "スペクター", "ジャッジ", "バッキー", 
                  "ガーディアン", "ファントム", "ヴァンダル", "オペレーター", "マーシャル", "アレス", "オーディン", "ナイフ"]
        self.server = ["TOKYO", "HongKong", "Sydney", "Mundai", "Singapore"]
        self.map = ["アイスボックス", "サンセット", "アセント", "ブリーズ", "ヘイブン", "ロータス", "バインド", "スプリット", "フラクチャー", "パール"]
        self.gamemode = ["アンレート", "コンペティティブ", "スイフトプレイ", "スパイクラッシュ", "デスマッチ", "エスカレーション", "チームデスマッチ"]

    @discord.ui.button(label="もういっかい！", emoji="🔁", style=discord.ButtonStyle.green)
    async def re_random(self, interaction, button: discord.ui.Button):
      ori_msg = interaction.message
      if interaction.user.id != self.user_id:
        await interaction.response.send_message(f"スラッシュコマンドを実行した人のみボタンを押せます", ephemeral=True)
        return
      if "エージェント" in ori_msg.content:
        choice = random.choice(self.agent)
        await ori_msg.edit(content=f"エージェント：{choice}")
        await interaction.response.send_message(f"もう一回ランダムで選びました\n選択したもの：{choice}", ephemeral=True)
        return
      elif "武器" in ori_msg.content:
        choice = random.choice(self.weapon)
        await ori_msg.edit(content=f"武器：{choice}")
        await interaction.response.send_message(f"もう一回ランダムで選びました\n選択したもの：{choice}", ephemeral=True)
        return
      elif "サーバー" in ori_msg.content:
        choice = random.choice(self.server)
        await ori_msg.edit(content=f"サーバー：{choice}")
        await interaction.response.send_message(f"もう一回ランダムで選びました\n選択したもの：{choice}", ephemeral=True)
        return
      elif "ゲームモード" in ori_msg.content:
        choice = random.choice(self.gamemode)
        await ori_msg.edit(content=f"ゲームモード：{choice}")
        await interaction.response.send_message(f"もう一回ランダムで選びました。\n選択したもの：{choice}", ephemeral=True)
        return
      elif "マップ" in ori_msg.content:
        choice = random.choice(self.map)
        await ori_msg.edit(content=f"マップ：{choice}")
        await interaction.response.send_message(f"もう一回ランダムで選びました。\n選択したもの：{choice}", ephemeral=True)
        return
      elif "感度" in ori_msg.content:
        await ori_msg.edit(content=f"感度：{random.uniform(0.1, 10):.2f}")
        await interaction.response.send_message(f"もう一回ランダムで選びました。\n選択したもの：{choice}", ephemeral=True)
        return
      elif "ランダム結果" == ori_msg.embeds[0].title:
        await ori_msg.edit(embed=discord.Embed(title="ランダム結果", timestamp=datetime.datetime.now()).add_field(
          name="エージェント", value=random.choice(self.agent)
          ).add_field(name="銃", value=random.choice(self.weapon)
          ).add_field(name="サーバー", value=random.choice(self.server)
          ).add_field(name="感度", value=f"{random.uniform(0.1, 10):.2f}"
          ).add_field(name="マップ", value=random.choice(self.map)
          ).add_field(name="ゲームモード", value=random.choice(self.gamemode)))
        await interaction.response.send_message(f"もう一回ランダムで選びました。選んだものは[リプライ先]({ori_msg.jump_url})のものです。", ephemeral=True)


class slash(commands.Cog):
  def __init__(self, bot): 
    self.bot = bot
    self.agent = ["フェニックス", "ジェット", "スカイ", "ネオン", "ヨル", "サイファー", "キルジョイ", "チェンバー", "セージ", "KAY/O", "オーメン", "ブリーチ", "ソーヴァ", "アイソ", "ブリーチ", 
          "キルジョイ", "ゲッコー", "ハーバー", "アストラ", "ヴァイパー", "ブリムストーン", "デットロック", "フェイド"]
    self.weapon = ["クラシック", "ショーティー", "フレンジー", "ゴースト", "シェリフ", "スティンガー", "スペクター", "ジャッジ", "バッキー", 
              "ガーディアン", "ファントム", "ヴァンダル", "オペレーター", "マーシャル", "アレス", "オーディン", "ナイフ"]
    self.server = ["TOKYO", "HongKong", "Sydney", "Mundai", "Singapore"]
    self.map = ["アイスボックス", "サンセット", "アセント", "ブリーズ", "ヘイブン", "ロータス", "バインド", "スプリット", "フラクチャー", "パール"]
    self.gamemode = ["アンレート", "コンペティティブ", "スイフトプレイ", "スパイクラッシュ", "デスマッチ", "エスカレーション", "チームデスマッチ"]


  group = app_commands.Group(name="valorant", description="Valorant関係", guild_only=False)
  # スラッシュコマンド 3    
  @group.command(name="agent", description="エージェントをランダムで選びます")
  async def agent_random(self, interaction):
    await interaction.response.send_message(f"エージェント：{random.choice(self.agent)}", view=reget(self, interaction.user.id))
  @group.command(name="weapon", description="武器をランダムで選びます")
  async def weapon_random(self, interaction):
    await interaction.response.send_message(f"武器：{random.choice(self.weapon)}", view=reget(self, interaction.user.id))
  @group.command(name="server", description="サーバーをランダムで選びます")
  async def server_random(self, interaction):
    await interaction.response.send_message(f"サーバー：{random.choice(self.server)}", view=reget(self, interaction.user.id))
  @group.command(name="sensitivity", description="サーバーをランダムで選びます")
  async def sensitvity_random(self, interaction):
    sensitivity = random.uniform(0.1, 10)
    await interaction.response.send_message(f"感度：{random.uniform(0.1, 10):.2f}", view=reget(self, interaction.user.id))
  @group.command(name="map", description="マップをランダムで選びます")
  async def map_random(self, interaction):
    await interaction.response.send_message(f"マップ：{random.choice(self.map)}", view=reget(self, interaction.user.id))
  @group.command(name="gamemode", description="ゲームモードをランダムで選びます")
  async def gamemode_random(self, interaction):
    await interaction.response.send_message(f"ゲームモード：{random.choice(self.gamemode)}", view=reget(self, interaction.user.id))
  @group.command(name="all", description="すべてをランダムで選びます")
  async def all_random(self, interaction):
    await interaction.response.send_message(embed=discord.Embed(title="ランダム結果", timestamp=datetime.datetime.now()).add_field(
      name="エージェント", value=random.choice(self.agent)
      ).add_field(name="銃", value=random.choice(self.weapon)
      ).add_field(name="サーバー", value=random.choice(self.server)
      ).add_field(name="感度", value=f"{random.uniform(0.1, 10):.1f}"
      ).add_field(name="マップ", value=random.choice(self.map)
      ).add_field(name="ゲームモード", value=random.choice(self.gamemode)), view=reget(self, interaction.user.id))

async def setup(bot: commands.Bot):
  await bot.add_cog(slash(bot))
