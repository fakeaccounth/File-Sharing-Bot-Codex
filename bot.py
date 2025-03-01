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
            name=f"Bot_{bot_token.split(':')[0]}",  # Unique session name
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=bot_token
        )
        self.LOGGER = LOGGER
        self.bot_token = bot_token
        self.port = port

    async def start(self):
        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()

        self.LOGGER(__name__).info(f"Bot @{usr_bot_me.username} is running on port {self.port}!")

        if FORCE_SUB_CHANNEL:
            try:
                link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                if not link:
                    await self.export_chat_invite_link(FORCE_SUB_CHANNEL)
                    link = (await self.get_chat(FORCE_SUB_CHANNEL)).invite_link
                self.invitelink = link
            except Exception as e:
                self.LOGGER(__name__).warning(f"Force Sub Error: {e}")
                sys.exit()

        try:
            db_channel = await self.get_chat(CHANNEL_ID)
            self.db_channel = db_channel
            test = await self.send_message(chat_id = db_channel.id, text = "Test Message")
            await test.delete()
        except Exception as e:
            self.LOGGER(__name__).warning(e)
            self.LOGGER(__name__).warning(f"Make Sure bot is Admin in DB Channel, and Double check the CHANNEL_ID Value, Current Value {CHANNEL_ID}")
            self.LOGGER(__name__).info("\nBot Stopped. Join https://t.me/CodeXBotzSupport for support")
            sys.exit()

        self.set_parse_mode(ParseMode.HTML)

        # Web server setup for each bot
        app = web.AppRunner(await web_server())
        await app.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app, bind_address, self.port).start()

    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info(f"Bot on port {self.port} stopped.")

async def main():
    bots = []
    for index, token in enumerate(BOT_TOKENS):
        port = BASE_PORT + index  # Assign unique port for each bot
        bot = Bot(token, port)
        bots.append(bot)

    await asyncio.gather(*(bot.start() for bot in bots))

if __name__ == "__main__":
    asyncio.run(main())