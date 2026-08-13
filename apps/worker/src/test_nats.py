import asyncio
import nats

async def main():
    nc = await nats.connect("nats://localhost:4222")
    await nc.publish("genesis.agent.invoke", b'{"test": "data"}')
    print("Published message to NATS")
    await nc.close()

if __name__ == '__main__':
    asyncio.run(main())
