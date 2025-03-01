import asyncio
import os
import sys
from datetime import datetime
from aiohttp import web
import pyromod.listen
from pyrogram import Client
from pyrogram.enums import ParseMode
from plugins import web_server
from config import *

# Fetch bot tokens from the environment
BOT_TOKENS = os.environ.get(
    "BOT_TOKENS",
    "6403720726:AAH2s38VIkj9TWcxA2ZNlRmnz-G2CSot4MA,7934694179:AAGoY4YqNZ-TYq1i3LYohud8a8pTa2LH6HM"
).split(",")

if not BOT_TOKENS:
    raise Exception("No bot tokens provided!")

# Base port for web server (increments for each bot)
BASE_PORT = 3788  

class Bot(Client):
    def __init__(self, bot_token, port):
        super().__init__(
            name=f"Bot_{bot_token.split(':')[0]}",  # Unique name per bot
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=bot_token
        )
        self.LOGGER = LOGGER
        self.bot_token = bot_token
        self.port = port  # Unique port for each bot

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.LOGGER(__name__).info(f"Bot @{usr_bot_me.username} is running on port {self.port}!")

        # Force Subscription Check
        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(f"Error exporting invite link: {e}")
                sys.exit()

        # Database Channel Check
        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id=db_channel.id, text="Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Database channel error: {e}")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)
        print(f"Bot @{usr_bot_me.username} started on port {self.port}")

        # Web server setup (each bot gets a different port)
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            await web.TCPSite(app, "0.0.0.0", self.port).start()
        except Exception as e:
            self.LOGGER(__name__).warning(f"Failed to start web server on port {self.port}: {e}")

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"Bot @{self.bot_token} stopped.")

async def main():
    bots = [Bot(token, BASE_PORT + i) for i, token in enumerate(BOT_TOKENS)]
    await asyncio.gather(*(bot.start() for bot in bots))

if __name__ == "__main__":
    asyncio.run(main())