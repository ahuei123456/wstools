from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

from wstools import config
from wstools.proxy.service import generate_proxy_pdf

GENERATE_PROXY_RATE_LIMIT = 1
GENERATE_PROXY_COOLDOWN_SECONDS = 60.0
_log = logging.getLogger(__name__)


class ProxyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="generate_proxy",
        description="Generate and upload a printable proxy PDF from an EncoreDecks deck code.",
    )
    @app_commands.describe(deck_code="EncoreDecks deck code, for example X6LSRnhEL.")
    @app_commands.checks.dynamic_cooldown(
        lambda interaction: build_generate_proxy_cooldown(interaction),
        key=lambda interaction: interaction.user.id,
    )
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
            _log.info(
                (
                    "Generated proxy PDF successfully. "
                    "user=%s user_id=%s guild_id=%s channel_id=%s deck_code=%s file=%s"
                ),
                interaction.user,
                interaction.user.id,
                interaction.guild_id,
                interaction.channel_id,
                safe_name,
                pdf_path.name,
            )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ProxyCog(bot))


def build_generate_proxy_cooldown(
    interaction: discord.Interaction,
) -> app_commands.Cooldown | None:
    settings = config.get_config()
    exempt_user_ids = settings.get("RATE_LIMIT_EXEMPT_USER_IDS", [])
    if interaction.user.id in exempt_user_ids:
        return None

    return app_commands.Cooldown(
        GENERATE_PROXY_RATE_LIMIT,
        GENERATE_PROXY_COOLDOWN_SECONDS,
    )
