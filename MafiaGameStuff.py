#Mafia Game Stuff

import discord
import asyncio
import random
from MafiaBotInfo import COMMAND,setup

debug = True

class Role: #Defines the different roles in the game

    def __init__(self, title, description,emoji,status):
        self.title = title
        self.desc = description
        self.emoji = emoji
        self.status = status

    def toggle(self):
        if self.status == True:
            self.status = False
        else:
            self.status = True

#Listing all roles
host = Role("Host", "The host is responsible for running the entire game. They are aware of everyone's roles and guides the other players along the narrative. The host cannot give away any information ragarding the identities of any of the other roles",'🎩',True)
mafia = Role("Mafia", "The big bad crew in town, the mafia must choose a person to be killed everynight. When there is an equal number of mafia and non-mafia, they win",'🔪',True)
townsperson = Role("Townsperson", "This role has no significance except to vote who to be sacrificed",'👔',True)
doctor = Role("Doctor","Every night, the doctor is able to choose one living player, including themselves, to be saved. If the mafia chooses to kill the same person, they will be spared",'💊',True)
detective = Role("Detective","Every night, the doctor may choose one person, and the host will tell them if that person is a Mafia or not",'🔍',True)
cupid = Role("Cupid","Every night, the cupid can choose two people to link together until the next night. If one of the pair is killed, the other dies as well.","💘",False)
traitor = Role("Traitor","The traitor's goal is to help the mafia win. The traitor knows who the mafia are, but does not kill at night with the mafia. The mafia are not told who the traitor is.",'🐍',False)
judge = Role("Judge","When the judge reveals themselves, they are given the ability to vote twice for a person TWICE! This can only be done once.",'⚖️',False)
silencer = Role("Silencer","Every night, the silencer may choose one person to silence. The chosen person will not be allowed to speak during the next day's discussion.","🔇",False)

normroles = [host,mafia,townsperson,doctor,detective]

specialroletoggle = True
specialroles = [cupid,traitor,judge,silencer]

#Assigning mafia-text channel permissions
#Mafia and host can read and send messages in mafia chat.
#Ghosts can read and send messages in ghost chat.
fullperm = discord.PermissionOverwrite()
fullperm.send_messages = True
fullperm.read_messages = True

#Ghosts can read but not send messages in mafia chat.
readperm = discord.PermissionOverwrite()
readperm.send_messages = False
readperm.read_messages = True

#Other people cannot read or send messages in mafia or ghost chat.
hideperm = discord.PermissionOverwrite()
hideperm.send_messages = False
hideperm.read_messages = False

async def startgame(dsclient,channel,guild,SETUP):

    global normroles
    global specialroles
    global specialroletoggle

    global fullperm
    global readperm
    global hideperm

    playerlist = ""
    playercount = 0
    playerqueue = []

    allplayerroles = ""

    if SETUP == False:
        await setup(dsclient, channel, guild)

    mafiachat = discord.utils.get(dsclient.get_all_channels(), name='mafia-discussion')
    ghostchat = discord.utils.get(dsclient.get_all_channels(), name='ghost-discussion')

    #Get all players message
    mssg = await channel.send("It's time to begin the game of Mafia! First, all players react to the 👍 in the next 10 seconds")
    await mssg.add_reaction("👍")

    #Sleeps for 10 seconds while players react to the message
    await asyncio.sleep(10)

    #Collects information about users who reacted and stores them in a list of players
    mssg = await channel.fetch_message(mssg.id)
    users = await mssg.reactions[0].users().flatten()

    for user in users:
        playerqueue.append(user)
        playerlist = playerlist + " \n " + user.name
        playercount+=1

    #Removing the bot user from the player queue
    playerqueue.remove(dsclient.user)
    playercount-=1

    print(playerqueue)

    #Checking for sufficient number of players
    if playercount == 0:
        await channel.send("Oops, looks like I'm the only one playing!")
        return
    elif playercount < 5 and debug == False:
        await channel.send("Oops, not enough people joined the game. You will need atleast 5 people to play!")
        return

    await channel.send(f"The players of this game of Mafia are: \n{playerlist}\n")

    #Deciding the host of the game
    mssg = await channel.send(f"\nWho is the host of the game? React {host.emoji}")
    await mssg.add_reaction(host.emoji)

    i = 1
    while( True ):
        mssg = await channel.fetch_message(mssg.id)

        #The first person who reacts and is also a player will be the host. If the first reactor is not a player, the second reactor will be the host, and so on.
        if mssg.reactions[0].count > i:
            reactors = await mssg.reactions[0].users().flatten()
            candidate = reactors[i] #Choosing first person to react

            if candidate in playerqueue: #Checking if they are a player
                gamehost = candidate
                playerqueue.remove(gamehost)
                playercount-=1
                break
            else:
                i+=1 #Try next person who reacted

    await channel.send(f"The host of the game is: {gamehost.name}")

    #Host has full access to both the mafiachat and ghostchat
    await setperm(gamehost, fullperm, mafiachat)
    await setperm(gamehost, fullperm, ghostchat)

    mafiacount = playercount//4 + 1
    specialcyclecount = playercount//16 + 1

    #Decide special roles for the game
    roleslist = "⭕: Add ALL Special Roles\n❌: Remove ALL Special Roles\n\nCUSTOM OPTIONS\n"
    opcount = 1

    for role in specialroles:
        roleslist = roleslist + f"{role.emoji}: Add {role.title}\n"
        opcount+=1

    roleslist = roleslist + "\n\n✅: Confirm Custom Roles"
    opcount+=1

    await channel.send(f"Host {gamehost.name}, confirm special roles for this game. Use command '!mafia viewroles' to see role descriptions")
    chooseroles = await channel.send(roleslist)
    
    await chooseroles.add_reaction('⭕')
    await chooseroles.add_reaction('❌')
    

    for role in specialroles:
        await chooseroles.add_reaction(role.emoji)

    await chooseroles.add_reaction('✅')

    while True:

        chooseroles = await channel.fetch_message(chooseroles.id)

        if gamehost in await chooseroles.reactions[0].users().flatten():
                for role in specialroles:
                    role.status = True
                print("SPECIAL ROLES ON")
                break

        if gamehost in await chooseroles.reactions[1].users().flatten():
                for role in specialroles:
                    role.status = False
                print("SPECIAL ROLES OFF")
                break
        
        if gamehost in await chooseroles.reactions[opcount].users().flatten():
            for i in range(2,opcount):
                if gamehost in await chooseroles.reactions[i].users().flatten():
                    print("ROLE ->" , i)
                    specialroles[i-2].status = True
                    print(f"{specialroles[i-2].title} ROLE ON")
            break

    #Randomising and Assigning Roles
    random.shuffle(playerqueue)
    piter = 0

    #Assigning mafia
    for i in range( mafiacount ):
        if( piter < playercount ):
            allplayerroles += f"\n{playerqueue[piter].name} -> Mafia"

            #Send player their role
            await dmrole( playerqueue[piter] , mafia)

            #Mafia can read and send messages in mafiachat.
            #Mafia cannot interact with ghostchat
            print("Assigning Mafia Permissions")
            await setperm(playerqueue[piter], fullperm, mafiachat)
            await setperm(playerqueue[piter], hideperm, ghostchat)
            piter+=1

    #Assigning doctor and detective roles
    for i in range(2):
        if( piter < playercount ):
            allplayerroles += f"\n{playerqueue[piter].name} -> {normroles[3+i].title}"

            #Send player their role
            await dmrole( playerqueue[piter] , normroles[3+i])

            #Normal roles cannot interact with either mafiachat or ghostchat
            await setperm(playerqueue[piter], hideperm, mafiachat)
            await setperm(playerqueue[piter], hideperm, ghostchat)
            piter+=1

    #Assigning special roles, if any 
    random.shuffle(specialroles)
    for _ in range(specialcyclecount):
        for i in range( len( specialroles ) ):
            if piter < playercount-1: #There should be atleast one normal townsperson
                if specialroles[i].status == True:
                    allplayerroles += f"\n{playerqueue[piter].name} -> {specialroles[i].title}"

                    #Send player their role
                    await dmrole( playerqueue[piter],specialroles[i])

                    #Normal roles cannot interact with either mafiachat or ghostchat
                    await setperm(playerqueue[piter], hideperm, mafiachat)
                    await setperm(playerqueue[piter], hideperm, ghostchat)

                    piter +=1

    #Assigning Townpeople
    while( piter < playercount ):
        allplayerroles += f"\n{playerqueue[piter].name} -> Townsperson"

        #Send player their role
        await dmrole( playerqueue[piter], townsperson)

        #Normal roles cannot interact with either mafiachat or ghostchat
        await setperm(playerqueue[piter], hideperm, mafiachat)
        await setperm(playerqueue[piter], hideperm, ghostchat)
        piter += 1

    hostdm = await dmrole(gamehost, host)
    await hostdm.send("PLAYER ROLES\n\n" + allplayerroles)

    await channel.send(f"Each of you will now recieve a DM with your roles.")

    mssg = await channel.send(f"There are {mafiacount} mafia in the town. The game will now begin in...")
    await mssg.add_reaction("3️⃣")
    await mssg.add_reaction("2️⃣")
    await mssg.add_reaction("1️⃣")

    await channel.send(f"Who will be the next victims? ( Host can kill a player by typing -> !mafia kill <player> )")

    while( True ):
        mssg = await dsclient.wait_for('message')

        if mssg.author == gamehost:
            if mssg.content.startswith(f"{COMMAND} kill"):

                #Extract victim from message
                killmssg = mssg.content.split()
                deadplayer = await dsclient.fetch_user(killmssg[2][3:-1])
                
                if deadplayer == gamehost:
                    await channel.send("The host cannot be killed")
                else:
                    #Kill player
                    await kill(deadplayer,channel,mafiachat,ghostchat)
                
        
            elif mssg.content.startswith(f"{COMMAND} endgame"):
                await channel.send("The game has ended!")
                await reset(playerqueue,mafiachat,ghostchat,channel)
                return


async def dmrole(player, role):

    #print("PLAYER ->", player.name)

    try:

        #player is a discord.User object
        #role is a Role object
        playerdm = await player.create_dm()
        await playerdm.send(f"Your roles is: {role.title}\n\n{role.desc}")

        return playerdm
    except Exception as e:
        print(e)

async def viewroles(channel):

    count = 1
    allroles = "STANDARD ROLES:\n\n"
    for role in normroles:
        allroles += f"{role.emoji} \t {role.title} : {role.desc}\n\n"
        count+=1

    allroles += "\nSPECIAL ROLES:\n\n"
    for role in specialroles:
        allroles += f"{role.emoji} \t {role.title} : {role.desc}\n\n"
        count+=1

    await channel.send(allroles)

async def setperm(player,perm,channel):
    
    print(player.name,"-->",perm,type(perm),channel)

    await channel.set_permissions(player, overwrite=perm)
    return

async def kill(dead,channel,mafiachat,ghostchat):

    await channel.send(f"R.I.P 🪦 \n\n{dead.name} has been killed")

    #Send the dead a message
    try:
        deaddm = await dead.create_dm()
        await deaddm.send(f"You have been killed!\n\nWith your new ghostly powers, you can:\n1. Chat with other ghosts in <#{ghostchat.id}>\n2. See what the mafia are planning in <#{mafiachat.id}>")
        
        #Ghosts only read mafiachat, but not send messages
        #Ghosts can read and message in the ghostchat
        await setperm(dead, readperm, mafiachat)
        await setperm(dead, fullperm, ghostchat)
    
    except Exception as e:
        return

async def reset(players,mafiachat,ghostchat,channel):
    global specialroles

    #Reset all special roles to off
    for role in specialroles:
        role.status = False

    #Gives all players full permissions to mafia and ghost chats
    for player in players:
        await setperm(player, fullperm, mafiachat)
        await setperm(player, fullperm, ghostchat)

    await channel.send("Roles and Permissions are reset")