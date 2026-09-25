"""今日人品 (JRRP) command.

Uses the platform-agnostic BotContext / UserInfo abstractions.
Does not depend on any specific chat platform.
Response text is localized via utils.i18n.t (same pattern as VersionCommand).
"""

from __future__ import annotations

from datetime import date
from typing import Optional

try:
    from ...context import BotContext, UserInfo
except ImportError:  # allow direct PYTHONPATH=. usage / unit tests
    from context import BotContext, UserInfo  # type: ignore

from utils.i18n import t

from .service import calculate_daily_luck, generate_identifier


def _level_i18n_key(score: int) -> str:
    """Map score to a stable i18n key (UI only; algorithm returns int)."""
    if score >= 100:
        return "jrrp.level.max"
    if score >= 90:
        return "jrrp.level.excellent"
    if score >= 70:
        return "jrrp.level.good"
    if score >= 50:
        return "jrrp.level.fair"
    if score >= 30:
        return "jrrp.level.average"
    if score >= 10:
        return "jrrp.level.poor"
    return "jrrp.level.terrible"


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
        level = t(_level_i18n_key(score), locale=ctx.locale)

        response_key = "jrrp.response.target" if target is not None else "jrrp.response"

        message = t(
            response_key,
            locale=ctx.locale,
            id=user.id,
            username=user.username or user.id,
            name=user.display_name,
            date=query_date.isoformat(),
            score=score,
            level=level,
            identifier=identifier,
        )

        await ctx.reply(message)
