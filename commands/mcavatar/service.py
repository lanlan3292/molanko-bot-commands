import asyncio
import base64
import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import aiohttp


class AvatarProcessingError(Exception):
    pass


@dataclass
class McAvatarOptions:
    scale: int = 10
    outline: int = 2
    outline_color: str = "auto"
    bg_color: str = "auto"
    fill_background: bool = True
    upscale48: bool = True
    average_color: Optional[dict[str, int]] = None

    def to_nodejs_options(self) -> dict[str, Any]:
        opts: dict[str, Any] = {
            "scale": self.scale,
            "outlineMode": self.outline,
            "outlineColor": self.outline_color,
            "bgColor": self.bg_color,
            "fillBackground": self.fill_background,
            "upscale48": self.upscale48,
        }
        if self.average_color:
            opts["averageColor"] = self.average_color
        return opts


@dataclass
class McAvatarResult:
    image_bytes: bytes
    source_label: str


class McAvatarService:
    def __init__(self, CORE_SCRIPTS_DIR: Path):
        self.CORE_SCRIPTS_DIR = CORE_SCRIPTS_DIR

    def check_environment(self) -> tuple[bool, str]:
        if not shutil.which("node"):
            return False, "Node.js executable not found in system PATH"
        if not self.CORE_SCRIPTS_DIR.exists():
            return False, f"Script file not found at '{self.CORE_SCRIPTS_DIR}'"
        return True, ""

    async def fetch_skin(self, username: str) -> bytes:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.mojang.com/users/profiles/minecraft/{username}"
            ) as resp:
                if resp.status != 200:
                    raise ValueError(f"Player '{username}' not found")
                data = await resp.json()
                uuid = data["id"]

            async with session.get(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{uuid}"
            ) as resp:
                if resp.status != 200:
                    raise ValueError("Failed to fetch profile from Mojang")
                profile = await resp.json()

            textures = next(
                (
                    prop
                    for prop in profile.get("properties", [])
                    if prop.get("name") == "textures"
                ),
                None,
            )
            if not textures:
                raise ValueError("No textures found in profile")

            decoded = base64.b64decode(textures["value"]).decode("utf-8")
            texture_data = json.loads(decoded)
            skin_url = texture_data.get("textures", {}).get("SKIN", {}).get("url")
            if not skin_url:
                raise ValueError("Skin URL missing in texture data")

            async with session.get(skin_url) as resp:
                if resp.status != 200:
                    raise ValueError("Failed to download skin image")
                return await resp.read()

    async def process(self, image_data: bytes, options: McAvatarOptions) -> bytes:
        proc = await asyncio.create_subprocess_exec(
            "node",
            str(self.CORE_SCRIPTS_DIR),
            json.dumps(options.to_nodejs_options()),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(input=image_data)

        if proc.returncode != 0:
            error_msg = stderr.decode().strip() or "Unknown Node.js execution error"
            raise AvatarProcessingError(f"Node.js processing failed: {error_msg}")

        return stdout

    async def generate(
        self,
        *,
        player: Optional[str] = None,
        image_data: Optional[bytes] = None,
        options: McAvatarOptions,
    ) -> McAvatarResult:
        if not player and not image_data:
            raise ValueError("need_player_or_image")

        if image_data is None:
            assert player is not None
            image_data = await self.fetch_skin(player)
            source_label = player
        else:
            source_label = player or "attachment"

        result = await self.process(image_data, options)
        return McAvatarResult(image_bytes=result, source_label=source_label)
