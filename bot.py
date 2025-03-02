import asyncio
import os
import sys
from datetime import datetime
from aiohttp import web
import pyromod.listen
from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler
from plugins import web_server
from config import *

# Fetch bot tokens from the environment
BOT_TOKENS = os.environ.get(
    "BOT_TOKENS",
    "6403720726:AAH2s38VIkj9TWcxA2ZNlRmnz-G2CSot4MA,7934694179:AAGY4YqNZ-TYq1i3LYohud8a8pTa2LH6HM"
).split(",")

if not BOT_TOKENS or len(BOT_TOKENS) < 2:
    raise Exception("No bot tokens provided!")

BASE_PORT = 3788  # Base port for web servers


class Dot(Client):
    def __init__(self):
        super().__init__(
            name="Dot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        print(f"✅ {usr_bot_me.username} (Dot) Started Successfully!")

        # Force Subscription Setup
        if FORCE_SUB_CHANNEL:
            try:
                chat = await self.get_chat(FORCE_SUB_CHANNEL)
                self.invitelink = chat.invite_link or (await self.export_chat_invite_link(FORCE_SUB_CHANNEL))
            except Exception as e:
                print(f"⚠️ Error fetching invite link: {e}")
                sys.exit()

        # Web Server (Port BASE_PORT)
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", BASE_PORT).start()


class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN_2
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        print(f"✅ {usr_bot_me.username} (Bot) Started Successfully!")

        # Force Subscription Setup
        if FORCE_SUB_CHANNEL:
            try:
                chat = await self.get_chat(FORCE_SUB_CHANNEL)
                self.invitelink = chat.invite_link or (await self.export_chat_invite_link(FORCE_SUB_CHANNEL))
            except Exception as e:
                print(f"⚠️ Error fetching invite link: {e}")
                sys.exit()

        # Web Server (Port BASE_PORT + 1)
        app = web.AppRunner(await web_server())
        await app.setup()
        await web.TCPSite(app, "0.0.0.0", BASE_PORT + 1).start()


# ✅ Run Both Bots in Separate Processes (Fixes Conflicts)
if __name__ == "__main__":
    from multiprocessing import Process

    p1 = Process(target=lambda: asyncio.run(Dot().start()))
    p2 = Process(target=lambda: asyncio.run(Bot().start()))

    p1.start()
    p2.start()

    p1.join()
    p2.join()