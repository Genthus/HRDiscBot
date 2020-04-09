"""
HRDiscBot, a Discord bot made by Genthus
github.com/Genthus/HRDiscBot
"""
import discord
from discord.ext import commands
import random, math, asyncio, roles, challanges

key = ''
try:
    with open('botKey.txt', 'r') as f:
        key = f.readline()
        f.close()
except FileNotFoundError:
    key = input('Paste your bot key here and press enter\n')
    keyFile = open('botKey.txt', 'w')
    keyFile.write(key)

client = commands.Bot(command_prefix = '')

serverLobbyTextChannel = None
serverLobbyVoiceChannel = None
gameChallangeRoom = None
gameVoiceChannel = None

gameIsRunning = False
firstRoundIsOver = False

challangeSize = [2,3,3,4,4,5,4]

CyberPoliceTeamWins= 0
HackerTeamWins= 0

currentRound = 0
roundTime = [3,4,5,5,6,6,6]
currentTimer = 0
currentTimerString = ''

votingOpen = False
yesVotes = 0
noVotes = 0
playersWhoVoted = []

currentPlayerList = []
playerClassList = []
leaderRole = None
leaderPlayer = None
gameState = None
playersToBeChallanged = []
playersNominated = []

#Role settings
roleSetMode = 'basic'

rolesCreated = []
channelsCreated = []



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


####      Functions     ####

#Send message to all player dashboards
async def globalMessage(message):
    messageList = []
    for pl in playerClassList:
        x = await pl.playerChannel.send(message)
        messageList.append(x)
    return messageList

#Send message to a player dashboard
async def personalMessage(playerClass, message):
    messageSent = await playerClass.playerChannel.send(message)
    return messageSent

#Challange room transfer
async def challangeTransfer():
    global playersNominated, playersToBeChallanged
    playersToBeChallanged = playersNominated
    playersNominated = []
    for pl in playersToBeChallanged:
        await pl.user.move_to(gameChallangeRoom)
        await personalMessage(pl, 'You are now in the challange room, prepare yourselves')

#Return challangers to main
async def challangeReturn():
    global playersToBeChallanged
    for pl in playersToBeChallanged:
        await pl.user.move_to(gameVoiceChannel)
        await personalMessage(pl, 'You are now back in the main voice channel')
    playersToBeChallanged = []

#Mute everyone in a voice channel
async def muteVoiceChannel(channelToMute):
    await channelToMute.set_permissions(channelToMute.guild.default_role, speak = False)

#Unmute everyone in a voice channel
async def unmuteVoiceChannel(channelToMute):
    await channelToMute.set_permissions(channelToMute.guild.default_role, speak = True)

#Returns list of current players as a message
async def playerListMessage():
    message = ''
    m=1
    for pl in playerClassList:
        message += f'{m}. {pl.user.name}\n'
        n=+1
    return(message)

#Set gameRoles
async def setGameRoles(playerClasses):
    modes = {
        'basic' : roles.basic
    }
    global playerClassList
    await modes.get(roleSetMode, 'basic')(playerClasses)
    for pl in playerClassList:
        await personalMessage(pl, f'Your role is {pl.gameRole.name}\nYou are part of the {pl.gameRole.team} team\n{pl.gameRole.description}\n{pl.gameRole.winCondition}\n{pl.gameRole.abilityDescription}')
        if pl.gameRole.name == 'Hacker':
            await pl.gameRole.ability(playerClassList, pl)

#Switch leader role
async def switchLeader():
    if len(leaderRole.members) > 0:
        global leaderPlayer
        currentLeader = leaderPlayer
        await leaderPlayer.user.remove_roles(leaderRole)
        leaderFound = False
        #Cycle to find leader and give to the next person
        #This cycles in the order they joined the lobby
        for pl in playerClassList:
            if leaderFound == True:
                await pl.user.add_role(leaderRole)
                leaderPlayer = pl
            if pl == currentLeader:
                leaderFound = True
                if pl == playerClassList[-1]:
                    await playerClassList[0].user.add_roles(leaderRole)
                    leaderPlayer = pl

#Voting function
async def startVote():
    global playersNominated, playersWhoVoted, votingOpen, yesVotes, noVotes
    votingOpen = True
    await globalMessage('The voting proccess is now open, type "vote yes" or "vote no", not voting counts as voting no\nThe nominated party is:')
    for pl in playersNominated:
        await globalMessage(f'{pl.user.name}')
    """
    await globalMessage('You have 15 seconds to vote.')
    await asyncio.sleep(15)
    """
    voteTimer = 15
    voteTimerRange = range(voteTimer)
    voteTimerMessage = await globalMessage(f'You have {voteTimer} seconds to vote')
    for t in voteTimerRange:
        await asyncio.sleep(1)
        voteTimer -=1
        for ch in voteTimerMessage:
            await ch.edit(content = f'You have {voteTimer} seconds to vote')
    noVotes = len(playerClassList)-yesVotes
    if yesVotes > noVotes:
        await globalMessage(f'The vote has passed with {yesVotes} yes votes against {noVotes}\nIn 15 seconds the players will be sent to the challange room.')
        await asyncio.sleep(15)
        await switchLeader()
        playersWhoVoted = []
        votingOpen = False
        yesVotes = 0
        noVotes = 0
        return 1
    else:
        await globalMessage("The vote didn't pass, leadership will be transfered and the nomination process will begin again.")
        #TO-DO restart party making round
        await switchLeader()
        playersNominated = []
        playersWhoVoted = []
        votingOpen = False
        yesVotes = 0
        noVotes = 0
        return 0


#Setup the round timer
async def setRoundTimer(round):
    global currentTimer, currentTimerString
    currentTimer = roundTime[round]*60
    originalTime = currentTimer
    timerMessage = await globalMessage(f'Time remaining: {currentTimerString}')
    await leaderPlayer.playerChannel.send(f'\nThese are the available players\n{await playerListMessage()}')
    for n in range(originalTime):
        if len(playersNominated) < challangeSize[round]:
            currentTimer -=1
            currentTimerString = f'{math.floor(currentTimer/60)}:{currentTimer%60}'
            await asyncio.sleep(1)
            for m in timerMessage:
                if len(playersNominated)>0:
                    nomineesString = ''
                    for pl in playersNominated:
                        nomineesString += f'{pl.user.name}\n'
                    await m.edit(content = f'Time Remaining: {currentTimerString}\nThe current nominees are: {nomineesString}')
                else:
                    await m.edit(content = f'Time Remaining: {currentTimerString}\nThere are currently no nominated players')
            if playersNominated == challangeSize:
                await m.delete()
                await globalMessage('The nominees have been decided.')
                break

#Retry state 1
async def retryPartySelect():
    global votesFailed
    a0 = await switchGameState(1)
    if a0 == 'voteFailed':
        a1 = await switchGameState(1)
        if a1 == 'voteFailed':
            a2 = await switchGameState(1)
            if a2 == 'voteFailed':
                a3 = await switchGameState(1)
                if a3 == 'voteFailed':
                    a4 = await switchGameState(1)
                    if a4 == 'voteFailed':
                        print('failed to choose party 5 times')
                        return 'voteFailed'
    else: return 'votePassed'

#Announce score
async def scoreboard():
    await globalMessage(f'The current score is\nCyber Police: {CyberPoliceTeamWins}\nHackers: {HackerTeamWins}')

#Function to end the game
async def killGame():
    global gameIsRunning
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

#Check for victory
async def victoryCheck():
    global villageTeamWins, werewolfTeamWins
    if CyberPoliceTeamWins>= 4:
        print('Cyber Police team won')
        await globalMessage('The Cyber Police team has won the game!\nThe game will close in 30 seconds')
        return 'end'

    elif HackerTeamWins>= 4:
        print('Hacker team won')
        await globalMessage('The Hacker team has won the game!\nThe game will close in 30 seconds')
        return 'end'

#Whole 7 round game function
async def gameFlow():
    global currentRound, villageTeamWins, werewolfTeamWins, votesFailed
    #Give roles
    await setGameRoles(playerClassList)
    await asyncio.sleep(15)
    #Round 1:4
    for r in range(3):
        r1 = await retryPartySelect()
        if r1 == 'voteFailed':
            await globalMessage('Since no party was selected for 5 consecutive votes, the game is over and will be forced to end')
            await asyncio.sleep(30)
            await killGame()
        else:
            await switchGameState(2)
            await scoreboard()
            currentRound += 1
    #rounds 5:7
    for r in range(2):
        r1 = await retryPartySelect()
        if r1 == 'voteFailed':
            await globalMessage('Since no party was selected for 5 consecutive votes, the game is over and will be forced to end')
            await asyncio.sleep(30)
            await killGame()
        else:
            await switchGameState(2)
            await scoreboard()
            if await victoryCheck() == 'end':
                await asyncio.sleep(30)
                await killGame()
            currentRound += 1

#Function to switch gamestate
async def switchGameState(stateToSwitchTo):
    global gameState
    gameState = stateToSwitchTo

    #Party pick phase
    if gameState == 1:
        print('switched to game state 1')
        gameState = 1
        global firstRoundIsOver
        if firstRoundIsOver == False:
            await globalMessage('Welcome to HRProject, the game will now begin')
            #TO-DO add prompt for rules and instructions here
            #TO-DO add the role introduction here
            await globalMessage(f"For the first round, you will have {roundTime[0]} minutes to decide the party.\nIf the current leader doesn't decide within the time alloted, the role of leader will be appointed to someone else\nThe time begins now")
            firstRoundIsOver = True

        await globalMessage(f'The current leader is {leaderPlayer.user.mention}, to nominate players, type "nominate a b c",where a b and c are the numbers of the players you wish to nominate\nThe leader must nominate {challangeSize[currentRound]} players')
        await setRoundTimer(currentRound)
        result = await startVote()
        if result == 1: return 'votePassed'
        elif result == 0: return 'voteFailed'

    #Challange room phase
    if gameState ==2:
        global CyberPoliceTeamWins, HackerTeamWins
        await globalMessage('The selected party will now be sent to the challange room')
        await challangeTransfer()
        await asyncio.sleep(5)
        for pl in playerClassList:
            if pl not in playersToBeChallanged:
                pl.gameRole.addCharge()
                personalMessage(pl, "Your ability has recieved charge")
        challangePicked = random.choice(list(challanges.challangeDict.keys()))
        challangeToPlay = challanges.challangeDict.get(challangePicked, 'PickLetters')(playersToBeChallanged)
        result = await challangeToPlay.startChallange()
        await challangeReturn()
        if result == 'fail':
            HackerTeamWins += 1
        elif result == 'success':
            CyberPoliceTeamWins +=1

#### COMMANDS ####
@client.event
async def on_ready():
    print('Bot is ready.')

#Voting command
@client.command(aliases = ['Vote'.lower(), 'yes', 'no', 'Yes', 'No'])
async def vOte(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        global playersWhoVoted, noVotes, yesVotes
        yes = 'yes'
        no = 'no'
        if votingOpen == True and ctx.message.author not in playersWhoVoted:
            message = ctx.message.content.lower()
            if yes in message:
                yesVotes +=1
                print(ctx.message.content)
                await ctx.channel.send('You voted yes')
                playersWhoVoted.append(ctx.message.author)
            elif no in message:
                noVotes =+1
                print(ctx.message.content)
                await ctx.channel.send('You voted no')
                playersWhoVoted.append(ctx.message.author)
            else:
                await ctx.send('Try again')

#Pick command
@client.command(aliases = ['pick', 'answer', 'Pick', 'Answer'])
async def pickAnswer(ctx, *, pick):
    if ctx.message.channel.category.name == 'HRProject':
        challanges.answers[ctx.author.name] = pick
        await ctx.channel.send(f'you picked {pick}')

#Nominate players
@client.command(aliases = ['nominate'.lower(), 'nom', 'Nom', 'n', 'N'])
async def nOminate(ctx):
    if leaderRole in ctx.message.author.roles and gameState == 1 and len(playersNominated) < challangeSize[currentRound]:
        nominees = ctx.message.content
        nomList = nominees.split(' ')
        nomList.remove(nomList[0])
        print(nomList[0])
        for n in nomList:
            #Picking from number
            if len(n)==1:
                n = int(n)
                if n >0 and n <= len(playerClassList):
                    playersNominated.append(playerClassList[n-1])
            #Picking from name
            for pl in playerClassList:
                n = str(n).lower()
                name = pl.user.name.lower()
                if n == name:
                    playersNominated.append(pl)

#List the current players
@client.command(aliases = ['player list', 'listplayers', 'players'])
async def playerList(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        if len(currentPlayerList)>0:
            await ctx.send('Players:')
            for n in range(len(currentPlayerList)):
                await ctx.send(str(n+1) + '.  ' + currentPlayerList[n].name)
        else: await ctx.send('There are no players in the lobby')

#Join lobby command
@client.command(aliases = ['join', 'Join', 'joingame'])
async def joinGame(ctx):
    if gameIsRunning == False and ctx.message.channel.category.name == 'HRProject':
        coincidenceCount = 0
        for n in range(len(currentPlayerList)):
            if currentPlayerList[n] == ctx.author: coincidenceCount+=1
        if coincidenceCount == 0:
            if len(currentPlayerList)==0:
                global serverLobbyTextChannel
                serverLobbyTextChannel = ctx.message.channel
                await ctx.send('You have created a lobby')
                print('the servel lobyy text channel is set')
            if ctx.message.channel == serverLobbyTextChannel:
                currentPlayerList.append(ctx.author)
                await ctx.send(ctx.author.name + ' has joined the lobby')
                print(ctx.author.name + ' joined')

#Clear lobby
@client.command(aliases = ['emptyLobby', 'clearL', 'clearl'])
async def clearLobby(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        global currentPlayerList
        if len(currentPlayerList)>0 and gameIsRunning == False:
            currentPlayerList = []
            await ctx.send('Lobby has been emptied')
        else:
            await ctx.send('No lobby to clear')

#Forcefully end the game
@client.command(aliases = ['killGame'])
async def endTheGame(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        if gameIsRunning and ctx.message.channel == serverLobbyTextChannel:
            await killGame()
            await ctx.send('Game has been forced to end')

#Game Setup
@client.command(aliases = ['gameStart'])
async def startGame(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        global gameIsRunning
        if not gameIsRunning:

            #Create game channels
            global gameVoiceChannel, gameChallangeRoom
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
                playerChannel = await gameCategory.create_text_channel(name = f"{pl.name}'s Dashboard", overwrites = overwrites)

                print(f'Channel for player {pl.name} was created')
                channelsCreated.append(playerChannel)
                #await playerChannel.send(f'Welcome to your dashboard {pl.mention}')

                #Create instances of players with user, role, and game role
                playerClassList.append(Player(pl, role, playerChannel))
                await globalMessage(f'Welcome to your dashboard {pl.mention}')
                n+=1

                await ctx.send('Roles have been set!')

            #Save player 0's voice channel as lobby
            global serverLobbyVoiceChannel
            for pl in currentPlayerList:
                if pl.voice != None:
                    serverLobbyVoiceChannel = pl.voice.channel
                    print(pl.name + ' is now the VC lobby')
                    break
                else:
                    await ctx.send('No players are in a voice channel')

            #move players to new voice channel
            for pl in currentPlayerList:
                await pl.move_to(gameVoiceChannel)

            #Multiply challange size
            for n in challangeSize:
                challangeSize[n] = math.roof(challangeSize*len(playerClassList)/4)

            #Create leader role and assign it to a random player
            global leaderRole
            global leaderPlayer
            leaderRole = await ctx.guild.create_role(name = 'Leader', hoist = False)
            leaderPlayer = random.choice(playerClassList)
            await leaderPlayer.user.add_roles(leaderRole)
            rolesCreated.append(leaderRole)

            gameIsRunning = True
            await gameFlow()

#Server Setup Command
@client.command(aliases = ['serverSetup' , 'setupServer'])
async def prepareServer(ctx):
    createdCategory = await ctx.guild.create_category(name = 'HRProject')
    print('Category created')
    await ctx.guild.create_text_channel(name = 'Lobby', category = createdCategory, position = 0)
    print('Lobby created')
    await ctx.guild.create_voice_channel(name = 'Voice Lobby', category = createdCategory, position = 1)
    print('Voice lobby created')

#Contact command
@client.command()
async def contact(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        await ctx.send('github page:https://github.com/Genthus/HRDiscBot \ne-mail: genthus0@gmail.com ')

@client.command(aliases = ['howtoplay', 'HowToPlay', 'howToPlay'])
async def instructions(ctx):
    if ctx.category.name == 'HRProject':
        await ctx.send('A complete guide is here: https://github.com/Genthus/HRDiscBot#how-to-play')

@client.command(aliases = ['bothelp', 'botHelp', 'aaaaaaaaaaaaa'])
async def plshelp(ctx):
    if ctx.message.channel.category.name == 'HRProject':
        await ctx.send(f'type any of the keywords to activate it\nhelp : this message\ninstructions : link to the game guide\njoin : lets you join the lobby (this can only be done in the lobby)\n startGame : starts the game\nkillGame : ends the game and deletes everything made for the current game')



client.run(str(key))
