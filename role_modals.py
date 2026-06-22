import discord
from palette_generator import create_palette_image, create_gradient_palette
from role_views import ColorPaletteView, PermissionSelectView # 後で作成するファイルからインポート
from discord_ui import PERMISSION_TRANSLATIONS # discord_ui.pyからインポート

# ロール名入力モーダル (新しいフロー用)
class RoleNameModal(discord.ui.Modal, title='ロール名入力'):
    role_name = discord.ui.TextInput(
        label='ロール名',
        placeholder='新しいロールの名前を入力してください',
        required=True,
    )

    def __init__(self, mentionable: bool, hoist: bool):
        super().__init__()
        self.mentionable = mentionable
        self.hoist = hoist

    async def on_submit(self, interaction: discord.Interaction):
        # 色パレット画像を生成して送信
        palette_image_buffer = create_palette_image()
        palette_file = discord.File(fp=palette_image_buffer, filename="palette.png")

        palette_embed = discord.Embed(
            title="色の選択",
            description="表示されたパレットから使用したい色の識別番号（例: A1）を覚えて、「色を選択」ボタンを押してください。",
            color=discord.Color.blue()
        )
        palette_embed.set_image(url="attachment://palette.png")
        
        await interaction.response.send_message(
            embed=palette_embed,
            file=palette_file,
            view=ColorPaletteView(
                role_name=self.role_name.value,
                mentionable=self.mentionable,
                hoist=self.hoist
            ), 
            ephemeral=True
        )

# 色選択モーダル
class ColorSelectModal(discord.ui.Modal, title='パレット識別番号入力'):
    color_code = discord.ui.TextInput(
        label='パレットの識別番号',
        placeholder='例: A1',
        required=True,
        max_length=4,
    )

    def __init__(self, role_name: str, mentionable: bool, hoist: bool):
        super().__init__()
        self.role_name = role_name
        self.mentionable = mentionable
        self.hoist = hoist

    async def on_submit(self, interaction: discord.Interaction):
        # 最新のパレットを動的に取得
        current_palette = create_gradient_palette()
        code = self.color_code.value.upper()
        if code in current_palette:
            color_hex = current_palette[code]
            role_color_value = discord.Color.from_str(color_hex)

            # 権限選択ビューを表示
            permission_prompt_embed = discord.Embed(
                title="権限の選択",
                description='次に、ロールに付与する権限を選択してください。',
                color=role_color_value
            )
            await interaction.response.send_message(embed=permission_prompt_embed, view=PermissionSelectView(
                initial_interaction=interaction,
                role_name=self.role_name,
                role_color=role_color_value,
                mentionable=self.mentionable,
                hoist=self.hoist
            ), ephemeral=True)
        else:
            error_embed = discord.Embed(
                title="エラー",
                description="無効な識別番号です。パレットに表示されている番号を入力してください。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)