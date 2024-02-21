import asyncio
import time

from modules import *
from loguru import logger
from config import RPC


async def start_bridges(account_id, key):
    router = Router(account_id, key, "polygon")
    usdc_balance: dict = await router.get_usdc_balance()
    usdc_ether_balance: float = usdc_balance['balance']

    logger.info(f'Start usdc balance: {usdc_ether_balance} USDC')

    # апрув всех usdc, если они еще не апрувнуты
    await router.approve_usdc(rpc=RPC['polygon']['rpc'][0])

    while usdc_ether_balance >= 1.1:
        await router.bridge_usdc_to_bnb()
        usdc_balance = await router.get_usdc_balance()
        usdc_ether_balance = usdc_balance['balance']
        logger.info(f"balance Polygon USDC after bridge: {usdc_ether_balance}")

    logger.warning(f'Polygon USDC balance < 1.1')
    logger.info('Wait 60 sec before bridge BSC -> POLYGON')
    time.sleep(60)

    bscrouter = Router(account_id, key, "bsc")
    await bscrouter.approve_usdc_bsc(rpc=RPC['bsc']['rpc'][0])
    await bscrouter.bridge_all_usdc_to_polygon()
    logger.info('Wait 60 sec for success bridge BSC -> POLYGON')
    time.sleep(60)

    await start_bridges(account_id, key)


def get_tx_count():
    asyncio.run(check_tx())
