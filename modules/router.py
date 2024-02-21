import aiohttp
from loguru import logger
from utils.helpers import retry
from .account import Account
from .sync_client import Client
from config import ROUTER_ABI, ROUTER_ABI2


class Router(Account):
    def __init__(self, account_id: int, private_key: str, chain: str) -> None:
        super().__init__(account_id=account_id, private_key=private_key, chain=chain)

    async def get_usdc_balance_bsc(self):
        balance = await self.get_balance(contract_address='0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d')
        return balance

    async def get_usdc_balance(self):
        balance = await self.get_balance(contract_address='0x3c499c542cef5e3811e1192ce70d8cc03d5c3359')
        return balance

    async def approve_usdc(self, rpc: str):
        client = Client(self.private_key, rpc=rpc)
        res = client.approve_interface(
            token_address='0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359',
            spender='0x1396F41d89b96Eaf29A7Ef9EE01ad36E452235aE',
        )
        return res

    async def approve_usdc_bsc(self, rpc: str):
        client = Client(self.private_key, rpc=rpc)
        res = client.approve_interface(
            token_address='0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d',
            spender='0x260687eBC6C55DAdd578264260f9f6e968f7B2A5',
        )
        return res

    @retry
    async def bridge_usdc_to_bnb(self):
        logger.info(f"{self.address} bridge from POLYGON -> BSC")

        contract = self.get_contract(self.w3.to_checksum_address('0x1396F41d89b96Eaf29A7Ef9EE01ad36E452235aE'), abi=ROUTER_ABI)

        tx_data = await self.get_tx_data()

        # TX DATA
        partnerId = 1
        amount = 1100000  # 1.1 USDC
        destAmount = 1100000  # 1.1 USDC в BSC сети
        srcToken = self.w3.to_checksum_address('0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359')
        refundRecipient = self.address
        destChainIdBytes = '0x3536000000000000000000000000000000000000000000000000000000000000'
        destToken = '0x'
        recipient = bytes.fromhex(self.address[2:])

        transaction = await contract.functions.iDeposit(
            (partnerId, amount, destAmount, srcToken, refundRecipient, destChainIdBytes),
            destToken,
            recipient
        ).build_transaction(tx_data)

        signed_txn = await self.sign(transaction)

        txn_hash = await self.send_raw_transaction(signed_txn)

        await self.wait_until_tx_finished(txn_hash.hex())

    async def bridge_all_usdc_to_polygon(self):
        logger.info(f"{self.address} bridge from BSC -> POLYGON")

        contract = self.get_contract(self.w3.to_checksum_address('0x260687eBC6C55DAdd578264260f9f6e968f7B2A5'),
                                     abi=ROUTER_ABI2)

        tx_data = await self.get_tx_data_bsc()

        usdc_balance = await self.get_usdc_balance_bsc()

        # TX DATA
        partnerId = 1
        amount = usdc_balance['balance_wei']
        destAmount = usdc_balance['balance_wei']
        srcToken = self.w3.to_checksum_address('0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d')
        refundRecipient = self.address
        destChainIdBytes = '0x3133370000000000000000000000000000000000000000000000000000000000'
        destToken = '0x'
        recipient = bytes.fromhex(self.address[2:])

        transaction = await contract.functions.iDeposit(
            (partnerId, amount, destAmount, srcToken, refundRecipient, destChainIdBytes),
            destToken,
            recipient
        ).build_transaction(tx_data)

        signed_txn = await self.sign(transaction)

        txn_hash = await self.send_raw_transaction(signed_txn)

        await self.wait_until_tx_finished(txn_hash.hex())
