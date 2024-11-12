import discord
from discord.ext import commands
from discord import app_commands

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sqlite3
import TOKEN
from utils.typed_spotipy import TypedSpotipy
import utils.Page as Page
import json
import datetime

class spotify(commands.Cog):
    """
    # cog.spotify

    ```
    cog.spotify
    ```

    Spotify APIを使った簡単なコマンド。

    メッセージがSpotifyのURLだった場合、その曲の情報を取得してデータベースに傾向を保存します。
    また、単純なSpotifyの情報（トレンドとか）も取得できるようにする予定。
    """

    spotify_client : spotipy.Spotify
    
    def __init__(self, bot):
        cc_manager = SpotifyClientCredentials(
            client_id=TOKEN.SPOTIFY_CLIENT.get('id'),
            client_secret=TOKEN.SPOTIFY_CLIENT.get('secret')
        )
        self.spotify_client = spotipy.Spotify( client_credentials_manager=cc_manager )
        self.bot = bot
        # self.db = sqlite3.connect( "spotify.db" )
        # cursor = self.db.cursor()
        # cursor.execute( "CREATE TABLE IF NOT EXISTS spotify ( guildId BIGINT(20) PRIMARY KEY, mostTrendCategory STRING )" )
        # self.db.commit()

    spotify_cmd = app_commands.Group(name="spotify", description="Spotifyに関するコマンドです。")

    @spotify_cmd.command(name="search", description="曲を検索します")
    @app_commands.describe(query="検索クエリ")
    async def search( self, interaction : discord.Interaction, query : str):
        result = TypedSpotipy( self.spotify_client ).search( query, 'track', limit=50, market='JP' )

        if not result:
            await interaction.response.send_message("検索結果が見つかりませんでした。", ephemeral=True)
            return
        
        embeds = []

        for track in result.tracks.items:
            embed = discord.Embed(
                title=track.name,
                url=track.external_urls.spotify
            )
            embed.add_field(name="アーティスト", value=f"[{track.artists[0].name}]({track.artists[0].external_urls.spotify})", inline=False)
            embed.add_field(name="アルバム", value=track.album.name, inline=False)
            embed.add_field(name="リリース日", value=self.kireiDateTime(track.album.release_date))
            embed.add_field(name="人気度", value=self.getKansouFromPopularity(track.popularity))
            
            embed.set_thumbnail(url=track.album.images[0].url)
            embeds.append(embed)
        
        await Page.Simple( timeout=( 60 * 5 ) ).start( interaction, embeds )

    @commands.Cog.listener()
    async def on_message( self, message : discord.Message ):
        if message.author.id == "1141736921563934730":
            embed = message.embeds[0].to_dict()
            # えｍべｄから取得するけど正直何来るか知らないからあとで作る
            return

        if message.author.bot:
            return
        if not message.content.startswith("https://open.spotify.com/"):
            return
        
        track_id = message.content.split('/')[-1]
        clear_id = track_id.split('?')[0]
        track = TypedSpotipy( self.spotify_client ).track( clear_id )

        if not track:
            return
        
        # 今はやることないのでリアクションでもしとく
        if track.popularity < 10:
            return
        elif track.popularity < 30:
            await message.add_reaction("😏")
        elif track.popularity < 50:
            await message.add_reaction("😎")
        elif track.popularity < 70:
            await message.add_reaction("🔥")
        else:
            await message.add_reaction("😍")        



    @staticmethod
    def kireiDateTime( date : str ) -> str:
        if len(date) < 10:
            return date
        time = datetime.datetime( int(date[0:4]), int(date[5:7]), int(date[8:10]) )
        return time.strftime("%Y年%m月%d日")
    
    @staticmethod
    def getKansouFromPopularity( popularity : int ) -> str:
        if popularity < 10:
            return "☔ あんま人気なさげ...."
        elif popularity < 30:
            return "😏 まあまあ人気！"
        elif popularity < 50:
            return "😎 結構人気！"
        elif popularity < 70:
            return "🔥 かなり人気！"
        else:
            return "🔥😎😏 マジ人気！ 😏😎🔥"



async def setup(bot: commands.Bot):
    await bot.add_cog( spotify(bot) )