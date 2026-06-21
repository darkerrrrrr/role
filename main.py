import discord
from discord.ext import commands
from discord import app_commands
import re
import os
from PIL import Image, ImageDraw, ImageFont
import io
import colorsys

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




# グラデーションパレットを生成する関数
def create_gradient_palette():
    palette = {}
    hue_steps = 10  # 色相のステップ数 (行数)
    saturation_steps = 2  # 彩度のステップ数
    lightness_steps = 10  # 明度のステップ数 (列数)

    # 基本の色相を生成 (0.0から1.0まで)
    base_hues = [i / hue_steps for i in range(hue_steps)]
    
    # 彩度と明度を調整してバリエーションを増やす
    s_values = [0.8, 0.5] # 高彩度、中彩度
    l_values = [i / lightness_steps for i in range(1, lightness_steps + 1)] # 明度を0.1から1.0まで

    row_chars = "ABCDEFGHIJ" # 10行分の文字

    color_index = 0
    for r_idx, s in enumerate(s_values):
        for h_idx, h in enumerate(base_hues):
            for l_idx, l in enumerate(l_values):
                # HSLをRGBに変換
                r, g, b = colorsys.hls_to_rgb(h, l, s)
                # 0-255の整数に変換
                r, g, b = int(r * 255), int(g * 255), int(b * 255)
                # 16進数カラーコードに変換
                hex_color = f"#{r:02X}{g:02X}{b:02X}"
                
                # 識別番号を生成 (例: A1, A2, ..., J10)
                # 行は色相と彩度で決まる
                row_char_index = h_idx + (r_idx * hue_steps)
                if row_char_index >= len(row_chars):
                    continue # 定義した行文字数を超えたらスキップ
                row_char = row_chars[row_char_index]
                col_num = l_idx + 1
                
                identifier = f"{row_char}{col_num}"
                palette[identifier] = hex_color
                color_index += 1
                if color_index >= 200: # 約200色で制限
                    return palette
    
    # グレースケールと白黒を追加
    gray_start_char_index = len(row_chars) # Jの次から
    if gray_start_char_index < len(row_chars): # 念のためチェック
        for i in range(10): # 10段階のグレースケール
            l = i / 9.0 # 0.0から1.0まで
            r, g, b = int(l * 255), int(l * 255), int(b * 255)
            hex_color = f"#{r:02X}{g:02X}{b:02X}"
            identifier = f"{row_chars[gray_start_char_index]}{i+1}"
            palette[identifier] = hex_color
            color_index += 1
            if color_index >= 200:
                return palette

    return palette

# 色パレット画像を生成する関数
def create_palette_image():
    COLOR_PALETTE = create_gradient_palette() # 動的にパレットを生成
    cell_size = 60
    margin = 5
    cols = 20 # 20列に変更
    rows = (len(COLOR_PALETTE) + cols - 1) // cols
    
    # 行数が多すぎる場合は調整
    max_rows = 10 # 最大10行に制限
    if rows > max_rows:
        rows = max_rows
        # 表示する色数を調整
        display_colors = cols * rows
        COLOR_PALETTE = dict(list(COLOR_PALETTE.items())[:display_colors])

    img_width = cols * cell_size + (cols + 1) * margin
    img_height = rows * cell_size + (rows + 1) * margin

    img = Image.new('RGB', (img_width, img_height), (54, 57, 63))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    # 識別番号でソートして表示順を安定させる
    sorted_items = sorted(COLOR_PALETTE.items(), key=lambda item: (item[0][0], int(item[0][1:])))

    for i, (code, color_hex) in enumerate(sorted_items):
        if i >= cols * rows: # 表示制限を超えたら終了
            break
        col = i % cols
        row = i // cols
        x0 = margin + col * (cell_size + margin)
        y0 = margin + row * (cell_size + margin)
        x1 = x0 + cell_size
        y1 = y0 + cell_size

        draw.rectangle([x0, y0, x1, y1], fill=color_hex)
        
        r, g, b = tuple(int(color_hex.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        text_color = "black" if (r*0.299 + g*0.587 + b*0.114) > 186 else "white"
        
        text_bbox = draw.textbbox((0, 0), code, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x0 + (cell_size - text_width) / 2
        text_y = y0 + (cell_size - text_height) / 2
        draw.text((text_x, text_y), code, font=font, fill=text_color)

    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer

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
        # 真偽値の変換
        mentionable_str = self.mentionable.value.lower()
        hoist_str = self.hoist.value.lower()

        is_mentionable = mentionable_str in ['はい', 'yes', 'true']
        is_hoist = hoist_str in ['はい', 'yes', 'true']

        # 色パレット画像を生成して送信
        palette_image_buffer = create_palette_image()
        palette_file = discord.File(fp=palette_image_buffer, filename="palette.png")

        palette_embed = discord.Embed(
            title="ステップ2: 色の選択",
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
            success_embed.add_field(name="メンション可否", value="はい" if new_role.mentionable else "いいえ", inline=True)
            success_embed.add_field(name="表示の分離", value="はい" if new_role.hoist else "いいえ", inline=True)
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