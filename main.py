from solana.rpc.api import Client
from discord.ext import commands

from datetime import datetime
import os
import discord
from dotenv import load_dotenv
import json

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


discord_client = discord.Client()
solana_client = Client("https://explorer-api.mainnet-beta.solana.com/")

WALLETS_PATH = "./wallets.json"

def read_json(file):
    with open(file, "r+") as file:
        data = json.load(file)
    return data

def write_json(file, data):
    with open(file, "w+") as file:
        json.dump(data, file)

def get_wallet_transactions(wallet):
    sigs = solana_client.get_signatures_for_address(wallet)['result']
    txs = []
    for i,sig in enumerate(sigs):
        txs.append(get_transaction(sig[ 'signature' ]))
    return txs

def get_transaction(signature):
    tx = solana_client.get_confirmed_transaction(signature)['result']
    return tx

def blockTime_datetimeA(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def convert_int_to_sol(number):
    return number / 1000000000

def get_data(wallet):
    print("Getting data: " + wallet)
    txs = get_wallet_transactions(wallet)
    transactionAmounts = []
    for tx in txs:
        preBalance = tx['meta']['preBalances']
        postBalances = tx['meta']['postBalances']
        addresses = tx['transaction']['message']['accountKeys']
        walletIndex = addresses.index(wallet)
        walletTotalChange = postBalances[walletIndex] - preBalance[walletIndex]
        transactionAmounts.append(walletTotalChange)
    return {
        "balance": sum(transactionAmounts)
    }

    # pprint.pprint(tx)

def magic_eden():
    graphAPI = "hthttps://api-mainnet.magiceden.io/rpc/getActivitiesByQuery?q=%7B%22%24match%22%3A%7B%22collection_symbol%22%3A%22nfbees%22%7D%2C%22%24sort%22%3A%7B%22blockTime%22%3A-1%7D%2C%22%24skip%22%3A0%7Dtps://quickchart.io/chart?c=${encodedChart}"
    transactions = "https://api-mainnet.magiceden.io/rpc/getActivitiesByQuery?q=%7B%22%24match%22%3A%7B%22collection_symbol%22%3A%22nfbees%22%7D%2C%22%24sort%22%3A%7B%22blockTime%22%3A-1%7D%2C%22%24skip%22%3A0%7D"
    listings = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22nfbees%22%7D%2C%22%24sort%22%3A%7B%22takerAmount%22%3A1%2C%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A10000%7D"
    itemDetails = "https://api-mainnet.magiceden.io/rpc/getNFTByMintAddress/67eUtwvwfDfhKjh2WDqkEaer1XPkkSnyhjdMWHpvUqMg"

bot = commands.Bot(command_prefix='!')

@bot.command(name='bal')
async def balance(ctx):
    wallets_data = read_json(WALLETS_PATH)
    username = str(ctx.author)
    if username not in wallets_data:
        await ctx.send("You don't have any wallets saved. Save a wallet with `!save <address>`")
        return
    wallets = wallets_data[username]
    balance = 0
    for w in wallets:
        w_bal = get_data(w)["balance"]
        balance += w_bal
    await ctx.send(f"You have {convert_int_to_sol(balance)} SOL")

@bot.command(name="save")
async def save_wallet(ctx):
    args = ctx.message.content.split(" ")
    if len(args) <= 1:
        await ctx.send("Usage: !save <wallet address>")
        return
    username = str(ctx.author)
    wallet = args[1]
    wallet_data = read_json(WALLETS_PATH)
    if username not in wallet_data:
        wallet_data[username] = []
    wallet_data[username].append(wallet)
    write_json(WALLETS_PATH, wallet_data)
    await ctx.send(f"Saved your wallet! You have {len(wallet_data[username])} wallet(s)")

bot.run(TOKEN)

# myAddress = "HnwprDDu3ePXtp9cDh5u1zSNSYyVtrszGTrvic9tJqdx"