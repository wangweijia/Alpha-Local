import asyncio
from core.emquant_client import EmQuantClient

client = EmQuantClient()
try:
    positions = client.fetch_positions()
    print("Positions:", positions)
except Exception as e:
    print("Error:", e)
