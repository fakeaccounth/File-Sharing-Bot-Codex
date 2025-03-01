import asyncio
from aiohttp import web
from plugins import web_server

import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
import sys
from datetime import datetime

from config import *


class Bot(Client):
    def __init__(self, bot_token):
        super().__init__(
            name=f"Bot-{bot_token[:5]}",  # Unique name for each bot instance
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=bot_token,
        )
        self.LOGGER = LOGGER
        self.bot_token = bot_token

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as a:
                self.LOGGER(__name__).warning(f"[{self.bot_token[:5]}] {a}")
                self.LOGGER(__name__).warning(f"[{self.bot_token[:5]}] Bot can't Export Invite link from Force Sub Channel!")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"[{self.bot_token[:5]}] {e}")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"[{self.bot_token[:5]}] Bot Running..!\n")

        self.username = usr_bot_me.username
        # Web Server
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", PORT).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"[{self.bot_token[:5]}] Bot stopped.")


async def main():
    bot1 = Bot(TG_BOT_TOKEN_1)
    bot2 = Bot(TG_BOT_TOKEN_2)

    await asyncio.gather(bot1.start(), bot2.start())


if __name__ == "__main__":
    asyncio.run(main())