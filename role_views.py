import discord
from palette_generator import create_palette_image
from role_modals import ColorSelectModal # 後で作成するファイルからインポート
from role_components import PermissionSelect # 後で作成するファイルからインポート
from discord_ui import PERMISSION_TRANSLATIONS # discord_ui.pyからインポート

# ロールオプションボタンビュー
class RoleOptionsButtonsView(discord.ui.View):
    def __init__(self, role_name: str):
        super().__init__(timeout=180)
        self.role_name = role_name
        self.mentionable = None
        self.hoist = None

        # Mentionable buttons
        self.mentionable_true_btn = discord.ui.Button(label='@mentionを許可する', style=discord.ButtonStyle.grey, custom_id='mentionable_true', row=0)
        self.mentionable_false_btn = discord.ui.Button(label='@mentionを許可しない', style=discord.ButtonStyle.grey, custom_id='mentionable_false', row=0)
        self.mentionable_true_btn.callback = self.mentionable_true_callback
        self.mentionable_false_btn.callback = self.mentionable_false_callback
        self.add_item(self.mentionable_true_btn)
        self.add_item(self.mentionable_false_btn)

        # Hoist buttons
        self.hoist_true_btn = discord.ui.Button(label='オンラインメンバーとは別にロールメンバーを表示する', style=discord.ButtonStyle.grey, custom_id='hoist_true', row=1)
        self.hoist_false_btn = discord.ui.Button(label='オンラインメンバーとは別にロールメンバーを表示しない', style=discord.ButtonStyle.grey, custom_id='hoist_false', row=1)
        self.hoist_true_btn.callback = self.hoist_true_callback
        self.hoist_false_btn.callback = self.hoist_false_callback
        self.add_item(self.hoist_true_btn)
        self.add_item(self.hoist_false_btn)

        # Next button
        self.next_btn = discord.ui.Button(label='次へ', style=discord.ButtonStyle.primary, row=2)
        self.next_btn.callback = self.next_button_callback
        self.add_item(self.next_btn)

    async def mentionable_true_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.mentionable = True
        self.mentionable_true_btn.style = discord.ButtonStyle.green
        self.mentionable_false_btn.style = discord.ButtonStyle.grey
        await interaction.edit_original_response(view=self)

    async def mentionable_false_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.mentionable = False
        self.mentionable_true_btn.style = discord.ButtonStyle.grey
        self.mentionable_false_btn.style = discord.ButtonStyle.green
        await interaction.edit_original_response(view=self)

    async def hoist_true_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.hoist = True
        self.hoist_true_btn.style = discord.ButtonStyle.green
        self.hoist_false_btn.style = discord.ButtonStyle.grey
        await interaction.edit_original_response(view=self)

    async def hoist_false_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        self.hoist = False
        self.hoist_true_btn.style = discord.ButtonStyle.grey
        self.hoist_false_btn.style = discord.ButtonStyle.green
        await interaction.edit_original_response(view=self)

    async def next_button_callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if self.mentionable is None or self.hoist is None:
            await interaction.followup.send("「メンション可否」と「表示の分離」の両方を選択してください。", ephemeral=True)
            return

        try:
            palette_image_buffer = create_palette_image()
            palette_file = discord.File(fp=palette_image_buffer, filename="palette.png")

            palette_embed = discord.Embed(
                title="色の選択",
                description="表示されたパレットから使用したい色の識別番号（例: A1）を覚えて、「色を選択」ボタンを押してください。",
                color=discord.Color.blue()
            )
            palette_embed.set_image(url="attachment://palette.png")
            
            await interaction.followup.send(
                embed=palette_embed,
                file=palette_file,
                view=ColorPaletteView(
                    role_name=self.role_name,
                    mentionable=self.mentionable,
                    hoist=self.hoist
                ), 
                ephemeral=True
            )
        finally:
            self.stop()

# 色選択ビュー
class ColorPaletteView(discord.ui.View):
    def __init__(self, role_name: str, mentionable: bool, hoist: bool):
        super().__init__(timeout=180) # タイムアウトを180秒に設定
        self.role_name = role_name
        self.mentionable = mentionable
        self.hoist = hoist

    @discord.ui.button(label='色を選択', style=discord.ButtonStyle.primary)
    async def select_color_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ColorSelectModal(
            role_name=self.role_name,
            mentionable=self.mentionable,
            hoist=self.hoist
        ))

# 権限選択ビュー
class PermissionSelectView(discord.ui.View):
    def __init__(self, initial_interaction: discord.Interaction, role_name: str, role_color: discord.Color, mentionable: bool, hoist: bool):
        super().__init__(timeout=180)
        self.initial_interaction = initial_interaction
        self.role_name = role_name
        self.role_color = role_color
        self.mentionable = mentionable
        self.hoist = hoist
        self.selected_permissions = set() # 選択された権限を保持するセット

        # Discordで利用可能な権限リストをソート
        all_permissions = sorted([p for p, v in discord.Permissions.all()])
        
        # 権限を25個ずつのチャンクに分割
        chunk_size = 25
        permission_chunks = [all_permissions[i:i + chunk_size] for i in range(0, len(all_permissions), chunk_size)]

        # チャンクごとにSelectメニューを作成
        for i, chunk in enumerate(permission_chunks):
            if i < 5:  # Viewには最大5つのSelectメニューしか追加できない
                self.add_item(PermissionSelect(chunk, placeholder=f'権限を選択 ({i+1}/{len(permission_chunks)})'))

    async def update_embed(self, interaction: discord.Interaction):
        # 現在選択されているすべての権限を収集
        current_selected_permissions = set()
        for component in self.children:
            if isinstance(component, PermissionSelect):
                current_selected_permissions.update(component.values)
        self.selected_permissions = current_selected_permissions

        # Embedを再構築
        updated_embed = discord.Embed(
            title="権限の選択",
            description='次に、ロールに付与する権限を選択してください。\n\n**選択中の権限:**',
            color=self.role_color
        )
        if self.selected_permissions:
            translated_perms_list = []
            for perm_name in sorted(list(self.selected_permissions)):
                translated_perms_list.append(PERMISSION_TRANSLATIONS.get(perm_name, perm_name.replace('_', ' ').title()))
            updated_embed.add_field(name="権限リスト", value="\n".join(translated_perms_list), inline=False)
        else:
            updated_embed.add_field(name="権限リスト", value="なし", inline=False)
        
        # 元のメッセージを編集してEmbedを更新
        await interaction.response.edit_message(embed=updated_embed, view=self)

    @discord.ui.button(label='ロール作成', style=discord.ButtonStyle.primary, row=4)
    async def create_role_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True, thinking=True)

        guild = interaction.guild
        if not guild:
            error_embed = discord.Embed(
                title="エラー",
                description="サーバー内でのみロールを作成できます。",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return

        # すべてのSelectメニューから選択された権限を集約
        selected_permissions = set()
        for component in self.children:
            if isinstance(component, discord.ui.Select):
                selected_permissions.update(component.values)

        try:
            # 権限オブジェクトの作成
            perms = discord.Permissions.none()
            for perm_name in selected_permissions:
                setattr(perms, perm_name, True)

            # ロールの作成
            new_role = await guild.create_role(
                name=self.role_name,
                color=self.role_color,
                permissions=perms,
                mentionable=self.mentionable,
                hoist=self.hoist
            )

            # ロール作成成功メッセージをEmbedで送信
            success_embed = discord.Embed(
                title="ロール作成完了！",
                description=f"ロール `{new_role.name}` が正常に作成されました。",
                color=new_role.color
            )
            success_embed.add_field(name="ロール名", value=new_role.name, inline=True)
            success_embed.add_field(name="カラー", value=str(new_role.color), inline=True)
            success_embed.add_field(name="メンション可否", value="`@mentionを許可する`" if new_role.mentionable else "`@mentionを許可しない`", inline=True)
            success_embed.add_field(name="表示の分離", value="`オンラインメンバーとは別にロールメンバーを表示する`" if new_role.hoist else "`オンラインメンバーとは別にロールメンバーを表示しない`", inline=True)
            success_embed.add_field(name="付与された権限数", value=f"{len(selected_permissions)}個", inline=False)

            # 選択された権限のリストを作成
            translated_perms_list = []
            if selected_permissions:
                for perm_name in sorted(list(selected_permissions)):
                    translated_perms_list.append(PERMISSION_TRANSLATIONS.get(perm_name, perm_name.replace('_', ' ').title()))
                perms_display = "\n".join(translated_perms_list)
            else:
                perms_display = "なし"

            success_embed.add_field(name="付与された権限", value=perms_display, inline=False)
            
            await interaction.followup.send(embed=success_embed, ephemeral=True)

        except discord.Forbidden:
            error_embed = discord.Embed(
                title="エラー",
                description="ロールを作成するための権限がありません。",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        except Exception as e:
            error_embed = discord.Embed(
                title="エラー",
                description=f"ロールの作成中にエラーが発生しました: {e}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=error_embed, ephemeral=True)
        finally:
            self.stop()