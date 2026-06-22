import discord
from palette_generator import create_palette_image
from .views import RoleOptionsButtonsView, ColorPaletteView

# ロール名入力モーダル
class RoleNameModal(discord.ui.Modal, title='ロール名入力'):
    role_name_input = discord.ui.TextInput(
        label='ロール名',
        placeholder='新しいロールの名前を入力してください',
        required=True,
    )

    def __init__(self, mentionable: bool = None, hoist: bool = None):
        super().__init__()
        self.mentionable = mentionable
        self.hoist = hoist

    async def on_submit(self, interaction: discord.Interaction):
        role_name = self.role_name_input.value
        
        if self.mentionable is None or self.hoist is None:
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
        else:
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
                    role_name=role_name,
                    mentionable=self.mentionable,
                    hoist=self.hoist
                ), 
                ephemeral=True
            )