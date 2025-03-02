import asyncio
from bot import Bot, Dot

bot1 = Bot()
bot2 = Dot()

async def run_bots():
    await asyncio.gather(bot1.start(), bot2.start())

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_bots())
    loop.run_forever()