import discord
from discord.ext import commands
from discord import app_commands

from palette_generator import create_gradient_palette, create_palette_image

# 権限の日本語訳
PERMISSION_TRANSLATIONS = {
    "add_reactions": "リアクションの追加",
    "administrator": "管理者",
    "attach_files": "ファイルを添付",
    "ban_members": "メンバーをBAN",
    "change_nickname": "ニックネームの変更",
    "connect": "接続",
    "create_events": "イベントを作成",
    "create_guild_expressions": "エクスプレッションを作成",
    "create_expressions": "エクスプレッションを作成",
    "create_instant_invite": "招待を作成",
    "create_private_threads": "非公開スレッドを作成",
    "create_public_threads": "公開スレッドを作成",
    "deafen_members": "メンバーのスピーカーをミュート",
    "embed_links": "埋め込みリンク",
    "external_emojis": "外部の絵文字を使用する",
    "external_stickers": "外部のスタンプを使用する",
    "kick_members": "メンバーをキック",
    "manage_channels": "チャンネルの管理",
    "manage_emojis_and_stickers": "絵文字の管理",
    "manage_events": "イベントの管理",
    "manage_guild": "サーバーの管理",
    "manage_guild_expressions": "絵文字・スタンプ・サウンドの管理",
    "manage_expressions": "絵文字・スタンプ・サウンドの管理",
    "manage_messages": "メッセージの管理",
    "manage_nicknames": "ニックネームの管理",
    "manage_roles": "ロールの管理",
    "manage_threads": "スレッドの管理",
    "manage_webhooks": "ウェブフックの管理",
    "mention_everyone": "@everyone、@here、すべてのロールにメンション",
    "moderate_members": "メンバーをタイムアウト",
    "move_members": "メンバーを移動",
    "mute_members": "メンバーをミュート",
    "pin_messages": "メッセージをピン留め",
    "priority_speaker": "優先スピーカー",
    "read_message_history": "メッセージ履歴を読む",
    "read_messages": "チャンネルを見る",
    "request_to_speak": "スピーカー参加をリクエスト",
    "send_messages": "メッセージを送信",
    "send_messages_in_threads": "スレッドでメッセージを送信",
    "send_polls": "投票の作成",
    "send_tts_messages": "テキスト読み上げメッセージを送信する",
    "send_voice_messages": "ボイスメッセージを送信",
    "set_voice_channel_status": "ボイスチャンネルのステータスを設定",
    "speak": "発言",
    "stream": "WEBカメラ",
    "use_application_commands": "アプリケーションコマンドを使う",
    "use_embedded_activities": "ユーザーアクティビティ",
    "use_external_apps": "外部のアプリを使用",
    "use_external_emojis": "外部の絵文字を使用する",
    "use_external_sounds": "外部のサウンドを使用する",
    "use_external_stickers": "外部のスタンプを使用する",
    "use_soundboard": "サウンドボードを使用",
    "use_slowmode": "低速モードを回避",
    "bypass_slowmode": "低速モードを回避",
    "use_voice_activation": "音声検出を使用",
    "view_audit_log": "監査ログを表示",
    "view_channel": "チャンネルを見る",
    "view_creator_monetization_analytics": "サーバーの収益化分析を表示",
    "view_guild_insights": "サーバーインサイトを表示",
}

# 色選択モーダル
class ColorSelectModal(discord.ui.Modal, title='カラーコード入力'):
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
        self.stop() # モーダルを開いたらビューは役目を終える

# ロール作成モーダル
class RoleCreateModal(discord.ui.Modal, title='ロール作成'):
    role_name = discord.ui.TextInput(
        label='ロール名',
        placeholder='新しいロールの名前を入力してください',
        required=True,
    )
    mentionable = discord.ui.TextInput(
        label='このロールに対して@mentionを許可する',
        placeholder='許可する または 許可しない を入力',
        required=False,
        max_length=10,
    )
    hoist = discord.ui.TextInput(
        label='オンラインメンバーとは別にロールメンバーを表示する',
        placeholder='表示する または 表示しない を入力',
        required=False,
        max_length=10,
    )

    async def on_submit(self, interaction: discord.Interaction):
        # 真偽値の変換
        mentionable_str = self.mentionable.value.lower()
        hoist_str = self.hoist.value.lower()

        is_mentionable = False
        if mentionable_str in ['はい', 'yes', 'true', '許可する']:
            is_mentionable = True
        elif mentionable_str in ['いいえ', 'no', 'false', '許可しない']:
            is_mentionable = False
        is_hoist = False
        if hoist_str in ['はい', 'yes', 'true', '表示する']:
            is_hoist = True
        elif hoist_str in ['いいえ', 'no', 'false', '表示しない']:
            is_hoist = False

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
                mentionable=is_mentionable,
                hoist=is_hoist
            ), 
            ephemeral=True
        )


# 権限選択ドロップダウン
class PermissionSelect(discord.ui.Select):
    def __init__(self, permissions, placeholder: str):
        options = [
            discord.SelectOption(
                label=PERMISSION_TRANSLATIONS.get(perm, perm.replace('_', ' ').title()),
                value=perm
            )
            for perm in permissions
        ]
        super().__init__(placeholder=placeholder, min_values=0, max_values=len(options), options=options)

    async def callback(self, interaction: discord.Interaction):
        # 選択を承認するだけで、集約はボタンで行う
        await interaction.response.defer()


# 権限選択ビュー
class PermissionSelectView(discord.ui.View):
    def __init__(self, role_name: str, role_color: discord.Color, mentionable: bool, hoist: bool):
        super().__init__()
        self.role_name = role_name
        self.role_color = role_color
        self.mentionable = mentionable
        self.hoist = hoist

        # Discordで利用可能な権限リストをソート
        all_permissions = sorted([p for p, v in discord.Permissions.all()])
        
        # 権限を25個ずつのチャンクに分割
        chunk_size = 25
        permission_chunks = [all_permissions[i:i + chunk_size] for i in range(0, len(all_permissions), chunk_size)]

        # チャンクごとにSelectメニューを作成
        for i, chunk in enumerate(permission_chunks):
            if i < 5:  # Viewには最大5つのSelectメニューしか追加できない
                self.add_item(PermissionSelect(chunk, placeholder=f'権限を選択 ({i+1}/{len(permission_chunks)})'))

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
            success_embed.add_field(name="このロールに対して@mentionを許可する", value="許可する" if new_role.mentionable else "許可しない", inline=True)
            success_embed.add_field(name="オンラインメンバーとは別にロールメンバーを表示する", value="表示する" if new_role.hoist else "表示しない", inline=True)
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