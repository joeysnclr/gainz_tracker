from solana.rpc.api import Client
from discord.ext import commands

from datetime import datetime
import os
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


discord_client = discord.Client()
solana_client = Client("https://explorer-api.mainnet-beta.solana.com/")

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

bot = commands.Bot(command_prefix='!')

@bot.command(name='bal')
async def balance(ctx):
    args = ctx.message.content.split(" ")
    if len(args) < 1:
        await ctx.send("Usage: !bal <wallet address>")
        return
    wallet = args[1]
    balance = convert_int_to_sol(get_data(wallet)["balance"])
    await ctx.send(f"You have {balance} SOL")

bot.run(TOKEN)

# myAddress = "HnwprDDu3ePXtp9cDh5u1zSNSYyVtrszGTrvic9tJqdx"