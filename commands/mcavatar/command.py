from typing import Optional

from ...context import BotContext
from .service import AvatarProcessingError, McAvatarOptions, McAvatarService


class McAvatarCommand:
    def __init__(self, service: McAvatarService):
        self.service = service

    async def execute(
        self,
        ctx: BotContext,
        *,
        player: Optional[str] = None,
        image_data: Optional[bytes] = None,
        options: McAvatarOptions,
        success_content: str,
    ) -> None:
        result = await self.service.generate(
            player=player,
            image_data=image_data,
            options=options,
        )
        await ctx.reply_file(
            result.image_bytes,
            filename="avatar.png",
            content=success_content,
        )
