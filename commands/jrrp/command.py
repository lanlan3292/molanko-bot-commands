"""今日人品 (JRRP) command.

Uses the platform-agnostic BotContext / UserInfo abstractions.
Does not depend on any specific chat platform.
"""

from __future__ import annotations

from datetime import date
from typing import Optional

try:
    from ...context import BotContext, UserInfo
except ImportError:  # allow direct PYTHONPATH=. usage / unit tests
    from context import BotContext, UserInfo  # type: ignore

from .service import calculate_daily_luck, generate_identifier, luck_level


class JrrpCommand:
    """Command handler for /jrrp (今日人品)."""

    async def execute(
        self,
        ctx: BotContext,
        *,
        target: Optional[UserInfo] = None,
        on_date: Optional[date] = None,
    ) -> None:
        """Execute the daily luck query.

        Parameters
        ----------
        ctx:
            Platform-agnostic command context.
        target:
            Optional target user. Defaults to the invoking user
            (``ctx.user``). Adapters may resolve mentions into a
            ``UserInfo`` and pass it here.
        on_date:
            Optional date override (mainly for testing). Defaults to
            today in the local calendar.
        """
        user = target or ctx.user
        query_date = on_date or date.today()

        score = calculate_daily_luck(user.id, query_date)
        identifier = generate_identifier(user.id)
        level = luck_level(score)

        # Prefer Chinese presentation; fall back to a neutral English form
        # when the locale is clearly English.
        locale = (ctx.locale or "").lower()
        if locale.startswith("en"):
            message = (
                f"**Daily Luck**\n"
                f"User: {user.name}\n"
                f"Date: {query_date.isoformat()}\n"
                f"Luck: **{score}** ({level})\n"
                f"ID: `{identifier}`"
            )
        else:
            message = (
                f"**今日人品**\n"
                f"用户：{user.name}\n"
                f"日期：{query_date.isoformat()}\n"
                f"人品：**{score}**（{level}）\n"
                f"识别码：`{identifier}`"
            )

        await ctx.reply(message)
