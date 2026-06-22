import discord
from discord_ui import PERMISSION_TRANSLATIONS # discord_ui.pyからインポート

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
        # 選択された権限を親ビューに通知し、Embedを更新
        if self.view: # self.view は PermissionSelectView のインスタンス
            await self.view.update_embed(interaction)