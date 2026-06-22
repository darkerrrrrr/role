# src/modals.py
import discord

from palette_generator import create_gradient_palette, create_palette_image
from src.views import RoleOptionsButtonsView, ColorPaletteView, PermissionSelectView

# ロール名入力モーダル
class RoleNameModal(discord.ui.Modal, title='ロール名入力'):
    role_name_input = discord.ui.TextInput(
        label='ロール名',
        placeholder='新しいロールの名前を入力してください',
        required=True,
    )

    def __init__(self):
        super().__init__()

    async def on_submit(self, interaction: discord.Interaction):
        role_name = self.role_name_input.value
        
        await interaction.response.send_message(
            embed=discord.Embed(
                title="ロールオプションの選択",
                description="作成するロールの基本的な設定を行います。\n\n"
                            "--- メンション可否 ---\n"
                            "以下のボタンで選択してください。\n\n"
                            "--- 表示の分離 ---\n"
                            "以下のボタンで選択してください。\n\n"
                            "両方選択後、「次へ」ボタンを押してください。",
                color=discord.Color.blue()
            ),
            view=RoleOptionsButtonsView(role_name=role_name),
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