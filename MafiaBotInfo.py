import discord

#Mafia Bot Info

TOKEN = ""
COMMAND = "!mafia"
SETUP = False

async def setup(dsclient, channel, guild):

    global SETUP
    
    textchannels = []

    for tc in guild.text_channels:
        textchannels.append(tc.name)

    if 'mafia-discussion' not in textchannels:
        mafiachat = await guild.create_text_channel(name = 'Mafia Discussion')
        mafiachatinfo = await mafiachat.send("This is a text channel for mafia to chat and discuss during the game.\n\n1. Mafia 🔪 and the Host 🎩 can both read and send messages here\n2.Ghosts 👻 who were killed during the game can read messages but cannot send any.\n3. Other roles are unable to view this chat.")
        await mafiachatinfo.pin()
    if 'ghost-discussion' not in textchannels:
        ghostchat = await guild.create_text_channel("Ghost Discussion")
        ghostchatinfo = await ghostchat.send("This is a text channel for ghosts to chat and discuss after they are killed in the game. \n\nOnly ghosts 👻 can read and message here")
        await ghostchatinfo.pin()
    
    SETUP = True

    
