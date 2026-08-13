import asyncio
import nats
from core.config import settings

async def main():
    nc = await nats.connect(settings.nats_url)
    await nc.publish("genesis.agent.invoke", b'{"test": "data"}')
    print(f"Published message to NATS at {settings.nats_url}")
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
