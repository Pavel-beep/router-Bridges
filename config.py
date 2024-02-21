import json

with open('data/rpc.json') as file:
    RPC = json.load(file)

with open("accounts.txt", "r") as file:
    ACCOUNTS = [row.strip() for row in file]

with open('data/abi/erc20_abi.json') as file:
    ERC20_ABI = json.load(file)

with open('data/abi/router_abi.json') as file:
    ROUTER_ABI = json.load(file)

with open('data/abi/router_abi2.json') as file:
    ROUTER_ABI2 = json.load(file)
