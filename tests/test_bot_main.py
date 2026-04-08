from wstools.bot.main import format_cooldown_message


def test_format_cooldown_message_rounds_up() -> None:
    assert format_cooldown_message(0.2) == (
        "Rate limit hit. Please wait 1 second before generating another proxy PDF."
    )
    assert format_cooldown_message(12.1) == (
        "Rate limit hit. Please wait 13 seconds before generating another proxy PDF."
    )
