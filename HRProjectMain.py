import discord
from discord.ext import commands
import random, math, asyncio

client = commands.Bot(command_prefix = '')

serverLobbyTextChannel = None
serverLobbyVoiceChannel = None
gameChallangeRoom = None

gameIsRunning = False
firstRoundIsOver = False
roundTime = [3,4,5,5,6,6,6]
currentTimer = 0
currentTimerString = ''

votingOpen = False
yesVotes = 0
noVotes = 0
playersWhoVoted = []

currentPlayerList = []
playerClassList = []
rolesCreated = []
channelsCreated = []
gameState = None
playersToBeChallanged = []
playersNominated = []
leader = None



#Player class
class Player:
    user = None
    discordRole = None
    gameRole = None
    playerChannel = None
    state = 'Alive'

    def __init__(self, u, dR, pC):
        self.user = u
        self.discordRole = dR
        self.playerChannel = pC

#Function to switch gamestatef
async def switchGameState(stateToSwitchTo):
    gameState = stateToSwitchTo

    #Party pick phase
    if gameState == 1:
        if firstRoundIsOver == False:
            globalMessage('Welcome to HRProject, the game will now begin')
            #TO-DO add prompt for rules and instructions here
            #TO-DO add the role introduction here
            globalMessage(f"For the first round, you will have {roundTime[0]} minutes to decide the party.\n If the current leader doesn't decide within the time alloted, the role of leader will be appointed to someone else\n The time begins now")
            #TO-DO add way to show the timer
            
    #Challange room phase
    if gameState ==2:
        globalMessage('The selected party will now be sent to the challange room')
        for pl in playersToBeChallanged:
            await pl.move_to(gameChallangeRoom)
            personalMessage(pl, 'You are now in the challange room, prepare yourselves')
        

####      Functions     ####

#Send message to all player dashboards
async def globalMessage(message):
    for pl in playerClassList:
        await pl.playerChannel.send(message)

#Send message to a player dashboard
async def personalMessage(playerClass, message):
    await playerClass.playerChannel.send(message)

#Challange room transfer
async def challangeTransfer():
    playersToBeChallanged = playersNominated
    playersNominated = []
    for pl in playersToBeChallanged:
        playersToBeChallanged.user.move_to(gameChallangeRoom)

#Mute everyone in a voice channel
async def muteVoiceChannel(channelToMute):
    await channelToMute.set_permissions(default_member, speak = False)

#Unmute everyone in a voice channel
async def unmuteVoiceChannel(channelToMute):
    await channelToMute.set_permissions(default_member, speak = True)

#Returns list of current players as a message
async def playerListMessage():
    message = ''
    n=1
    for pl in playerClassList:
        message += f'{n}. {pl.user.name}\n'
        n=+1
    return(message)

#Switch leader role
async def switchLeader():
    if len(leader.members) > 0:
        currentLeader = leader.members[0]
        await currentLeader.remove_roles(leader)
        #Cycle to find leader and give to the next person
        #This cycles in the order they joined the lobby
        for pl in playerClassList:
            if leaderFound == True:
                await pl.give_role(leader)
            if pl.user == currentLeader:
                leaderFound = True
                if pl == playerClassList[-1]:
                    playerClassList[0].user.give_role(leader)

#Voting function
async def startVote():
    votingOpen = True
    globalMessage('The voting proccess is now open, type "vote yes" or "vote no"\n The nominated party is:')
    for pl in playersNominated:
        globalMessage(f'{pl.user.name}')
    globalMessage('You have 15 seconds to vote.')
    await asyncio.sleep(15)
    if yesVotes > noVotes:
        globalMessage('The vote has passed\n In 15 seconds the players will be sent to the challange room.')
        await asyncio.sleep(15)
        challangeTransfer()
    else:
        globalMessage("The vote didn't pass, leadership will be transfered and the nomination process will begin again.")
        #TO-DO restart party making round

    switchLeader()
    playersNominated = []
    playersWhoVoted = []
    votingOpen = False
    yesVotes = 0
    noVotes = 0

#Setup the round timer
async def setRoundTimer(time, round):
    currentTimer = t*60
    originalTime = t*60
    for n in originalTime:
        if len(playersNominated) < roundPartySize[r]:
            await asyncio.sleep(1)
            currentTimer =-1
            currentTimerString = f'{math.floor(currentTimer/60)}:{currentTimer%60}'
            


@client.event
async def on_ready():
    print('Bot is ready.')

@client.event(aliases = ['Vote'])
async def vote(ctx, desicion):
    if votingOpen == True and ctx.message.author not in playersWhoVoted:
        message = ctx.message.content
        if 'yes'.lower in message and 'no'.lower not in message:
            yesVotes +=1
        elif 'no'.lower in message and 'yes'.lower not in message:
            noVotes =+1
        playersWhoVotes.append(ctx.message.author)

#List the current players
@client.command(aliases = ['player list', 'listplayers', 'players'])
async def playerList(ctx):
    if len(currentPlayerList)>0:
        await ctx.send('Players:')
        for n in range(len(currentPlayerList)):
            await ctx.send(str(n+1) + '.  ' + currentPlayerList[n].name)
    else: await ctx.send('There are no players in the lobby')

#Join lobby command
@client.command(aliases = ['join', 'Join'])
async def joinGame(ctx):
    if gameIsRunning == False:
        coincidenceCount = 0
        for n in range(len(currentPlayerList)):
            if currentPlayerList[n] == ctx.author: coincidenceCount+=1
        if coincidenceCount == 0:
            if len(currentPlayerList)==0:
                global serverLobbyTextChannel
                serverLobbyTextChannel = ctx.message.channel
                print('the servel lobyy text channel is set')
            if ctx.message.channel == serverLobbyTextChannel:
                currentPlayerList.append(ctx.author)
                await ctx.send(ctx.author.name + ' has joined the lobby')
                print(ctx.author.name + ' joined')

#Clear lobby
@client.command(aliases = ['emptyLobby'])
async def clearLobby(ctx):
    global currentPlayerList
    if len(currentPlayerList)>0 and gameIsRunning == False:
        currentPlayerList = []
        await ctx.send('Lobby has been emptied')

#Forcefully end the game
@client.command(aliases = ['killGame'])
async def endTheGame(ctx):
    global gameIsRunning
    if gameIsRunning and ctx.message.channel == serverLobbyTextChannel:
        #delte created roles
        for rl in rolesCreated:
            await rl.delete()
        print('roles deleted')
        gameIsRunning = False

        #Move players back to original voice chat
        global currentPlayerList
        for pl in currentPlayerList:
            await pl.move_to(serverLobbyVoiceChannel)
        #Wipe player list
        currentPlayerList = []
        print('playerlist deleted')
        #Delete created channels
        global channelsCreated
        for ch in channelsCreated:
            await ch.delete()
        print('channels deleted')

        await ctx.send('Game has been forced to end')


#Game Setup
@client.command(aliases = ['gameStart'])
async def startGame(ctx):
    global gameIsRunning
    if not gameIsRunning:

        #Create game channels
        gameCategory = discord.utils.get(ctx.guild.categories, name = 'HRProject')
        gameVoiceChannel = await gameCategory.create_voice_channel(name = 'Game VC', position = 0, user_limit = len(currentPlayerList))
        channelsCreated.append(gameVoiceChannel)
        challangeOverwrites = {
            ctx.guild.default_role : discord.PermissionOverwrite(connect = False)
        }
        gameChallangeRoom = await gameCategory.create_voice_channel(name = 'Challange Room')
        channelsCreated.append(gameChallangeRoom)

        #Set Roles and nicknames
        n=1
        for pl in currentPlayerList:
            role = await ctx.guild.create_role(name = str('Player '+ str(n)), hoist = True)
            await pl.add_roles(role)
            rolesCreated.append(role)
            print('user ' + pl.name + ' was given the role of ' + role.name)

            #Create channels for players
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                role: discord.PermissionOverwrite(read_messages = True)
            }
            playerChannel = await gameCategory.create_text_channel(name = 'Dashboard', overwrites = overwrites)

            print(f'Channel for player {pl.name} was created')
            channelsCreated.append(playerChannel)
            #await playerChannel.send(f'Welcome to your dashboard {pl.mention}')

            #Create instances of players with user, role, and game role
            playerClassList.append(Player(pl, role, playerChannel))

            n+=1

        await globalMessage(f'Welcome to your dashboard {pl.mention}')

        await ctx.send('Roles have been set!')


        #Save player 0's voice channel as lobby
        global serverLobbyVoiceChannel
        for pl in currentPlayerList:
            if pl.voice != None:
                serverLobbyVoiceChannel = pl.voice.channel
                print(pl.name + 'is now the VC lobby')
                break
            else:
                await ctx.send('No players are in a voice channel')

        #move players to new voice channel
        for pl in currentPlayerList:
            await pl.move_to(gameVoiceChannel)

        #Create leader role and assign it to a random player
        leader = await ctx.guild.create_role(name = 'Leader', hoist = False)
        await random.choice(playerClassList).user.add_roles(leader)
        rolesCreated.append(leader)

        gameIsRunning = True
        switchGameState(1)

#Server Setup Command
@client.command(aliases = ['serverSetup' , 'setupServer'])
async def prepareServer(ctx):
    createdCategory = await ctx.guild.create_category(name = 'HRProject')
    print('Category created')
    await ctx.guild.create_text_channel(name = 'Lobby', category = createdCategory, position = 0)
    print('Lobby created')
    await ctx.guild.create_voice_channel(name = 'Voice Lobby', category = createdCategory, position = 1)
    print('Voice lobby created')





client.run('Njk1NDQ4MDUxNjkwNTA0MzEz.XoaWhA.BHmnknfL3de6pUs57PEr2M0W_Qs')
