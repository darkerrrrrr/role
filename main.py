import discord
from discord.ext import commands
from discord import app_commands
import re
import os

from palette_generator import create_gradient_palette, create_palette_image
from discord_ui import PERMISSION_TRANSLATIONS, ColorSelectModal, ColorPaletteView, PermissionSelect, PermissionSelectView, RoleCommands

# ボットのトークン
TOKEN = os.environ.get('DISCORD_TOKEN')
if not TOKEN:
    raise ValueError("DISCORD_TOKENが設定されていません。環境変数を確認してください。")

# Intentsの設定
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True

# Botのインスタンスを作成
bot = commands.Bot(command_prefix='/', intents=intents)
# Botが起動したときのイベント
@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました")
        await bot.add_cog(RoleCommands(bot)) # RoleCommands Cog を追加
        print("RoleCommands Cog をロードしました")
    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")


# Botの実行
bot.run(TOKEN)