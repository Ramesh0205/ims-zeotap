import httpx
import asyncio
import json

BASE_URL = "http://localhost:8000"

async def simulate_rdbms_outage():
    print("🔴 Simulating RDBMS outage...")
    async with httpx.AsyncClient() as client:
        for i in range(120):
            await client.post(f"{BASE_URL}/api/signals/ingest", json={
                "component_id": "POSTGRES_PRIMARY_01",
                "component_type": "RDBMS",
                "error_code": "DB_CONNECTION_REFUSED",
                "message": f"Connection refused on attempt {i+1}",
                "latency_ms": 5000
            })
        print("✅ RDBMS outage simulated - 120 signals sent (1 Work Item created)")

async def simulate_cache_failure():
    print("🟡 Simulating Cache failure...")
    async with httpx.AsyncClient() as client:
        for i in range(50):
            await client.post(f"{BASE_URL}/api/signals/ingest", json={
                "component_id": "CACHE_CLUSTER_01",
                "component_type": "CACHE",
                "error_code": "CACHE_MISS_RATE_HIGH",
                "message": f"Cache miss rate exceeded threshold - attempt {i+1}",
                "latency_ms": 800
            })
        print("✅ Cache failure simulated - 50 signals sent")

async def simulate_mcp_failure():
    print("🟠 Simulating MCP Host failure...")
    async with httpx.AsyncClient() as client:
        for i in range(30):
            await client.post(f"{BASE_URL}/api/signals/ingest", json={
                "component_id": "MCP_HOST_03",
                "component_type": "MCP",
                "error_code": "MCP_TIMEOUT",
                "message": f"MCP host not responding - attempt {i+1}",
                "latency_ms": 3000
            })
        print("✅ MCP failure simulated - 30 signals sent")

async def main():
    print("🚀 Starting failure simulation...")
    await simulate_rdbms_outage()
    await asyncio.sleep(2)
    await simulate_cache_failure()
    await asyncio.sleep(2)
    await simulate_mcp_failure()
    print("\n✅ All simulations complete! Check the dashboard at http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())
