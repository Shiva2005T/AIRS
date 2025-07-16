import asyncio
import json
import websockets

async def handler(websocket):
    try:
        async for message in websocket:
            print(f"[WebSocket] Received: {message}")
            with open("received_logs.jsonl", "a") as f:
                f.write(json.dumps({"message": message}) + "\n")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"[x] WebSocket connection closed: {e}")
    except Exception as e:
        print(f"[x] Unexpected error: {e}")

async def main():
    print("[+] Starting WebSocket server...")
    async with websockets.serve(handler, "localhost", 8000):
        print("[✓] WebSocket server running at ws://localhost:8000")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
