from types import SimpleNamespace
from typing import cast

import discord

from wstools.bot.cogs.proxy import (
    GENERATE_PROXY_COOLDOWN_SECONDS,
    GENERATE_PROXY_RATE_LIMIT,
    build_generate_proxy_cooldown,
)


def test_build_generate_proxy_cooldown_bypasses_exempt_users(monkeypatch) -> None:
    monkeypatch.setattr(
        "wstools.bot.cogs.proxy.config.get_config",
        lambda: {"RATE_LIMIT_EXEMPT_USER_IDS": [123]},
    )
    interaction = cast(discord.Interaction, SimpleNamespace(user=SimpleNamespace(id=123)))

    cooldown = build_generate_proxy_cooldown(interaction)

    assert cooldown is None


def test_build_generate_proxy_cooldown_returns_default_for_normal_users(monkeypatch) -> None:
    monkeypatch.setattr(
        "wstools.bot.cogs.proxy.config.get_config",
        lambda: {"RATE_LIMIT_EXEMPT_USER_IDS": [999]},
    )
    interaction = cast(discord.Interaction, SimpleNamespace(user=SimpleNamespace(id=123)))

    cooldown = build_generate_proxy_cooldown(interaction)

    assert cooldown is not None
    assert cooldown.rate == GENERATE_PROXY_RATE_LIMIT
    assert cooldown.per == GENERATE_PROXY_COOLDOWN_SECONDS
