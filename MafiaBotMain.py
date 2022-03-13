#Discord Mafia Bot

from time import sleep
import discord
import asyncio
from MafiaBotInfo import TOKEN, COMMAND, SETUP
from MafiaGameStuffCOPY import startgame,viewroles
from MafiaBotInfo import setup

async def test(dsclient,channel,guild):
    for member in guild.members:
        print(member.name)
    
    pass

intents = discord.Intents.all()
client = discord.Client(intents = intents)

@client.event
async def on_ready():
    print("Let's get this party rolling!")

@client.event
async def on_message(message):

    channel = message.channel
    guild = message.guild

    if message.author == client.user:
        return
    
    if message.content.startswith(f"{COMMAND} TEST"):
        await test(client,channel,guild)

    if message.content.startswith(f"{COMMAND} setup"):
        await setup(client, channel, guild)
        pass
    
    if message.content.startswith(f"{COMMAND} start"):
        await startgame(client,channel,guild,SETUP)
        pass

    elif message.content.startswith(f"{COMMAND} viewroles"):
        await viewroles(channel)
        pass

client.run(TOKEN)