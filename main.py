import discord
from discord.ext import commands
from discord import app_commands
import re
import os

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

# ロール作成モーダル
class RoleCreateModal(discord.ui.Modal, title='ロール作成'):
    role_name = discord.ui.TextInput(
        label='ロール名',
        placeholder='新しいロールの名前を入力してください',
        required=True,
    )
    role_color = discord.ui.TextInput(
        label='ロールカラー (Hex)',
        placeholder='例: #FF5733',
        required=False,
        max_length=7,
    )
    mentionable = discord.ui.TextInput(
        label='メンション可否',
        placeholder='はい または いいえ を入力',
        required=False,
        max_length=3,
    )
    hoist = discord.ui.TextInput(
        label='表示の分離',
        placeholder='はい または いいえ を入力',
        required=False,
        max_length=3,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # カラーコードのバリデーション
        color_hex = self.role_color.value
        if color_hex and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color_hex):
            await interaction.response.send_message('無効なカラーコードです。Hex形式（例: #FF5733）で入力してください。', ephemeral=True)
            return

        # 真偽値の変換
        mentionable_str = self.mentionable.value.lower()
        hoist_str = self.hoist.value.lower()

        is_mentionable = mentionable_str in ['はい', 'yes', 'true']
        is_hoist = hoist_str in ['はい', 'yes', 'true']
        
        color = discord.Color.default()
        if color_hex:
            color = discord.Color(int(color_hex.lstrip('#'), 16))

        # 権限選択ビューを表示
        await interaction.response.send_message('次に、ロールに付与する権限を選択してください。', view=PermissionSelectView(
            role_name=self.role_name.value,
            role_color=color,
            mentionable=is_mentionable,
            hoist=is_hoist
        ), ephemeral=True)

# 権限選択ドロップダウン
class PermissionSelect(discord.ui.Select):
    def __init__(self, permissions):
        options = [
            discord.SelectOption(
                label=PERMISSION_TRANSLATIONS.get(perm, perm.replace('_', ' ').title()),
                value=perm
            )
            for perm in permissions
        ]
        super().__init__(placeholder='権限を選択...', min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        # 選択された権限をビューに保存
        self.view.selected_permissions = self.values
        await interaction.response.defer()


# 権限選択ビュー
class PermissionSelectView(discord.ui.View):
    def __init__(self, role_name: str, role_color: discord.Color, mentionable: bool, hoist: bool):
        super().__init__()
        self.role_name = role_name
        self.role_color = role_color
        self.mentionable = mentionable
        self.hoist = hoist
        self.selected_permissions = []

        # Discordで利用可能な権限リスト
        all_permissions = [p for p in dir(discord.Permissions) if not p.startswith('_') and p not in ['none', 'all', 'value']]
        
        self.add_item(PermissionSelect(all_permissions))

    @discord.ui.button(label='ロール作成', style=discord.ButtonStyle.primary)
    async def create_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("サーバー内でのみロールを作成できます。", ephemeral=True)
            return

        try:
            # 権限オブジェクトの作成
            perms = discord.Permissions.none()
            for perm_name in self.selected_permissions:
                setattr(perms, perm_name, True)

            # ロールの作成
            new_role = await guild.create_role(
                name=self.role_name,
                color=self.role_color,
                permissions=perms,
                mentionable=self.mentionable,
                hoist=self.hoist
            )
            await interaction.response.send_message(f'ロール「{new_role.name}」を作成しました！', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('ボットにロールを管理する権限がありません。', ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f'エラーが発生しました: {e}', ephemeral=True)
        
        self.stop()


# Botが起動したときのイベント
@bot.event
async def on_ready():
    print(f'{bot.user} がログインしました')
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)}個のコマンドを同期しました")
    except Exception as e:
        print(f"コマンドの同期に失敗しました: {e}")


# スラッシュコマンドの定義
@bot.tree.command(name="createrole", description="新しいロールを作成します。")
async def createrole(interaction: discord.Interaction):
    await interaction.response.send_modal(RoleCreateModal())


# Botの実行
bot.run(TOKEN)