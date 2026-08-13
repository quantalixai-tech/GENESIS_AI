import asyncio
from services.ai_service import generate_completion

async def test_ai():
    content, stats = await generate_completion(
        model="llama3.2:3b",
        messages=[{"role": "user", "content": "Say 'hello world' and nothing else."}]
    )
    print("Content:", content)
    print("Stats:", stats)

if __name__ == "__main__":
    asyncio.run(test_ai())
