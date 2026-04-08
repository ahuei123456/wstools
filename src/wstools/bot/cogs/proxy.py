from __future__ import annotations

import tempfile
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from wstools.proxy.service import generate_proxy_pdf


class ProxyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="generate_proxy",
        description="Generate and upload a printable proxy PDF from an EncoreDecks deck code.",
    )
    @app_commands.describe(deck_code="EncoreDecks deck code, for example X6LSRnhEL.")
    async def generate_proxy(self, interaction: discord.Interaction, deck_code: str) -> None:
        await interaction.response.defer(thinking=True)

        safe_name = deck_code.split("/")[-1]
        with tempfile.TemporaryDirectory(prefix="wstools-proxy-") as temp_dir:
            output_path = Path(temp_dir) / f"{safe_name}.pdf"
            pdf_path = generate_proxy_pdf(deck_code, output_path)
            await interaction.followup.send(
                content=f"Generated proxy PDF for `{safe_name}`.",
                file=discord.File(pdf_path, filename=f"{safe_name}.pdf"),
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ProxyCog(bot))
