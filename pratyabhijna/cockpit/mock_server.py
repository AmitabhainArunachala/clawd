"""
Mock WebSocket Server for testing Live MI Cockpit
Simulates the Rust core streaming RVMetric JSON
"""
import asyncio
import websockets
import json
import random
import math
import time

async def generate_metrics():
    """Generate mock RVMetric data"""
    t = time.time()
    base_rv = 0.5 + 0.3 * math.sin(t * 0.5)
    
    return {
        'timestamp': t,
        'model_id': random.choice(['model_a', 'model_b', 'model_c']),
        'layer': random.randint(0, 11),
        'metrics': {
            'r_v': max(0, min(1, base_rv + random.gauss(0, 0.05))),
            'pr_early': max(0, min(1, 0.3 + random.gauss(0, 0.1))),
            'pr_late': max(0, min(1, 0.7 + random.gauss(0, 0.1))),
            'confidence': max(0, min(1, 0.85 + random.gauss(0, 0.05)))
        },
        'activations': [random.random() for _ in range(64)],
        'circuit_id': f'circuit_{random.randint(1, 5)}',
        'token_idx': int(t * 10) % 1000
    }

async def handler(websocket, path):
    """Handle WebSocket connections"""
    print(f"Client connected from {websocket.remote_address}")
    try:
        while True:
            data = await generate_metrics()
            await websocket.send(json.dumps(data))
            await asyncio.sleep(0.5)  # 2Hz
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected")

async def main():
    """Start WebSocket server"""
    print("🚀 Mock WebSocket Server starting on ws://localhost:8765")
    print("Streaming RVMetric JSON at 2Hz...")
    print("Press Ctrl+C to stop")
    
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")
