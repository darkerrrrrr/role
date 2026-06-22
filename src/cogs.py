# src/cogs.py
import discord
from discord.ext import commands
from discord import app_commands

from src.modals import RoleNameModal

class RoleCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="createrole", description="新しいロールを作成します。")
    async def createrole(self, interaction: discord.Interaction):
        await interaction.response.send_modal(RoleNameModal())