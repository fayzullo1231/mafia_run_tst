# utils/deep_link.py
from aiogram.utils.deep_linking import create_start_link, decode_payload

async def make_link(payload: str) -> str:
    return await create_start_link(payload)

def parse_link(payload: str) -> str:
    return decode_payload(payload)
