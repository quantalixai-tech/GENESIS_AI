import asyncio
import os
import nats
from nats.errors import ConnectionClosedError, TimeoutError, NoServersError
import genesis_db
from sqlmodel import select

NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4222")

async def message_handler(msg):
    subject = msg.subject
    reply = msg.reply
    data = msg.data.decode()
    print(f"Received a message on '{subject} {reply}': {data}")
    
    # Just a placeholder DB connection check
    try:
        # Example of using the shared db library in worker
        with next(genesis_db.get_session()) as session:
            users = session.exec(select(genesis_db.User)).all()
            print(f"Current number of users in db: {len(users)}")
    except Exception as e:
        print(f"DB Error in worker: {e}")

async def main():
    print(f"Connecting to NATS at {NATS_URL}...")
    try:
        nc = await nats.connect(NATS_URL)
        print("Connected to NATS!")

        # Subscribe to genesis.worker.*
        sub = await nc.subscribe("genesis.worker.>", cb=message_handler)
        print("Listening for messages on genesis.worker.>")

        # Keep alive
        while True:
            await asyncio.sleep(1)

    except Exception as e:
        print(f"Worker Error: {e}")

if __name__ == '__main__':
    asyncio.run(main())
