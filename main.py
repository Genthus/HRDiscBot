import discord
from discord.ext import commands
import HRGame
import math
import random
import challanges
import os
import atexit

#
# HRDiscBot, a Discord bot made by Genthus
# github.com/Genthus/HRDiscBot
#

client = commands.Bot(command_prefix='', help_command=None)

guildDict = {
    # guildID: GameInstanceClass
}
lobbyDict = {
    # guildID: [playerList]
}


# Player class
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


# COMMANDS #
@client.event
async def on_ready():
    print('Bot is ready.')

# Voting command
@client.command(aliases=['Vote'.lower(), 'yes', 'no', 'Yes', 'No'])
async def vOte(ctx):
    try:
        gInstance = guildDict[ctx.guild]
    except KeyError:
        print(f'gInstance not found in guild: {ctx.guild.name}')
    if ctx.channel.category.name == 'Hidden Role Game':
        yes = 'yes'
        no = 'no'
        if gInstance.votingOpen is True and ctx.message.author not in gInstance.playersWhoVoted:
            message = ctx.message.content.lower()
            if yes in message:
                gInstance.yesVotes += 1
                await ctx.channel.send('You voted yes')
                gInstance.playersWhoVoted.append(ctx.message.author)
            elif no in message:
                gInstance.noVotes += 1
                await ctx.channel.send('You voted no')
                gInstance.playersWhoVoted.append(ctx.message.author)
            else:
                await ctx.send('Try again')

# Pick command
@client.command(aliases=['pick', 'answer', 'Pick', 'Answer'])
async def pickAnswer(ctx, *, pick):
    if ctx.channel.category.name == 'Hidden Role Game':
        try:
            gInstance = guildDict[ctx.guild]
            gInstance.challangeClass.answers[ctx.author.name] = pick
            await ctx.channel.send(f'you picked {pick}')
        except KeyError:
            print(f'gInstance not found in guild: {ctx.guild.name}')

# Nominate players
@client.command(aliases=['nominate'.lower(), 'nom', 'Nom', 'n', 'N'])
async def nOminate(ctx):
    try:
        gInstance = guildDict[ctx.guild]
    except KeyError:
        print(f'gInstance not found in guild: {ctx.guild.name}')
    if gInstance.leaderRole in ctx.message.author.roles and gInstance.gameState == 1 and len(gInstance.playersNominated) < gInstance.challangeSize[gInstance.currentRound]:
        nominees = ctx.message.content
        nomList = nominees.split(' ')
        nomList.remove(nomList[0])
        print(nomList[0])
        for n in nomList:
            # Picking from number
            if len(n) == 1:
                n = int(n)
                if n > 0 and n <= len(gInstance.playerClassList):
                    gInstance.playersNominated.append(gInstance.playerClassList[n-1])
            # Picking from name
            for pl in gInstance.playerClassList:
                n = str(n).lower()
                name = pl.user.name.lower()
                if n == name:
                    gInstance.playersNominated.append(pl)

# List the current players
@client.command(aliases=['player list', 'listplayers', 'players'])
async def playerList(ctx):
    try:
        lobby = lobbyDict[ctx.guild]
    except KeyError:
        print(f'gInstance not found in guild: {ctx.guild.name}')
    if ctx.channel.category.name == 'Hidden Role Game':
        if len(lobby) > 0:
            await ctx.send('Players:')
            for n in range(len(lobby)):
                await ctx.send(str(n+1) + '.  ' + lobby[n].name)
        else:
            await ctx.send('There are no players in the lobby')

# Join lobby command
@client.command(aliases=['join', 'Join', 'joingame'])
async def joinGame(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        global lobbyDict
        lobby = None
        try:
            gInstance = guildDict[ctx.guild]
            print(f'joinGame failed, gInstance found in guild {ctx.guild.name}')
            if gInstance.gameIsRunning is True:
                await ctx.send('There is a game already running in this server')
            else:
                guildDict.pop(ctx.guild)
                print(f'creating lobby in guild: {ctx.guild.name}')
                lobbyDict[ctx.guild] = []
                lobby = lobbyDict[ctx.guild]
                coincidenceCount = 0
                for n in range(len(lobby)):
                    if lobby[n] is ctx.author:
                        coincidenceCount += 1
                if coincidenceCount == 0:
                    if len(lobby) == 0:
                        await ctx.send('You have created a lobby')
                        print('the servel lobyy text channel is set')
                        # if ctx.message.channel == serverLobbyTextChannel:
                        lobby.append(ctx.author)
                        await ctx.send(ctx.author.name + ' has joined the lobby')
                        print(ctx.author.name + ' joined')
                    else:
                        lobby.append(ctx.author)
                        await ctx.send(ctx.author.name + ' has joined the lobby')
                        print(ctx.author.name + ' joined')
        except KeyError:
            try:
                lobby = lobbyDict[ctx.guild]
            except KeyError:
                print(f'creating lobby in guild: {ctx.guild.name}')
                lobbyDict[ctx.guild] = []
                lobby = lobbyDict[ctx.guild]
            finally:
                coincidenceCount = 0
                for n in range(len(lobby)):
                    if lobby[n] is ctx.author:
                        coincidenceCount += 1
                if coincidenceCount == 0:
                    if len(lobby) == 0:
                        await ctx.send('You have created a lobby')
                        print('the servel lobyy text channel is set')
                        # if ctx.message.channel == serverLobbyTextChannel:
                        lobby.append(ctx.author)
                        await ctx.send(ctx.author.name + ' has joined the lobby')
                        print(ctx.author.name + ' joined')
                    else:
                        lobby.append(ctx.author)
                        await ctx.send(ctx.author.name + ' has joined the lobby')
                        print(ctx.author.name + ' joined')

# Clear lobby
@client.command(aliases=['emptyLobby', 'clearL', 'clearl'])
async def clearLobby(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        try:
            lobbyDict[ctx.guild] = []
            await ctx.send('Lobby has been emptied')
        except KeyError:
            await ctx.send('No lobby to clear')

# Forcefully end the game
@client.command(aliases=['killGame'])
async def endTheGame(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        try:
            gInstance = guildDict[ctx.guild]
        except KeyError:
            print(f'gInstance not found in guild: {ctx.guild.name}')
        if gInstance.gameIsRunning:
            await gInstance.killGame()
            await ctx.send('Game has been forced to end')

# Game Setup
@client.command(aliases=['gameStart'])
async def startGame(ctx):
    global lobbyDict
    global guildDict
    if ctx.channel.category.name == 'Hidden Role Game':
        try:
            gInstance = guildDict[ctx.guild]
            if gInstance.gameIsRunning is False:
                print('gInstance found in guild {ctx.guild.name, restarting instance}')
                gInstance = HRGame.Game(lobbyDict.pop(ctx.guild))
                guildDict[ctx.guild] = gInstance
                gInstance.reset()
            else:
                await ctx.send('There is a game running in this server already')
        except KeyError:
            print(f'Creating gInstance in guild: {ctx.guild.name}')
            gInstance = HRGame.Game(lobbyDict.pop(ctx.guild))
            guildDict[ctx.guild] = gInstance
            lobbyDict[ctx.guild] = []

        if gInstance.gameIsRunning is False:
            lobbyDict[ctx.guild] = []

            # Create game channels
            gInstance.channelsCreated = []
            gameCategory = discord.utils.get(ctx.guild.categories, name='Hidden Role Game')
            gInstance.gameVoiceChannel = await gameCategory.create_voice_channel(name='Game VC', position=0, user_limit=len(gInstance.currentPlayerList))
            gInstance.channelsCreated.append(gInstance.gameVoiceChannel)
            challangeOverwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(connect=False)
            }
            gInstance.gameChallangeRoom = await gameCategory.create_voice_channel(name='Challange Room', overwrites=challangeOverwrites)
            gInstance.channelsCreated.append(gInstance.gameChallangeRoom)
            gInstance.playerClassList = []
            gInstance.rolesCreated = []

            n = 1
            for pl in gInstance.currentPlayerList:
                # Set Roles and nicknames
                role = await ctx.guild.create_role(name=str('Player ' + str(n)),
                                                   hoist=True)
                await pl.add_roles(role)
                gInstance.rolesCreated.append(role)
                print('user ' + pl.name + ' was given the role of ' + role.name)

                # Create channels for players
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                    role: discord.PermissionOverwrite(read_messages=True)
                }
                playerChannel = await gameCategory.create_text_channel(name=f"{pl.name} Dashboard", overwrites=overwrites)

                print(f'Channel for player {pl.name} was created')
                gInstance.channelsCreated.append(playerChannel)

                # Create instances of players with user, role, and game role
                gInstance.playerClassList.append(Player(pl, role, playerChannel))
                await playerChannel.send(f'Welcome to your dashboard {pl.mention}')
                n += 1

                await ctx.send('Roles have been set!')

            # Save player 0's voice channel as lobby
            for pl in gInstance.currentPlayerList:
                if pl.voice is not None:
                    gInstance.serverLobbyVoiceChannel = pl.voice.channel
                    print(pl.name + ' is now the VC lobby')
                    break
                else:
                    await ctx.send('No players are in a voice channel')

            # move players to new voice channel
            for pl in gInstance.currentPlayerList:
                await pl.move_to(gInstance.gameVoiceChannel)

            # Multiply challange size
            for n in gInstance.challangeSize:
                gInstance.challangeSize[n] = math.ceil(gInstance.challangeSize[n]*len(gInstance.playerClassList)/4)

            # Create leader role and assign it to a random player
            gInstance.leaderRole = await ctx.guild.create_role(name='Leader',
                                                               hoist=False)
            gInstance.leaderPlayer = random.choice(gInstance.playerClassList)
            await gInstance.leaderPlayer.user.add_roles(gInstance.leaderRole)
            gInstance.rolesCreated.append(gInstance.leaderRole)

            gInstance.gameIsRunning = True
            await gInstance.gameFlow()

# Server Setup Command
@client.command(aliases=['serverSetup', 'setupServer'])
async def prepareServer(ctx):
    print(f'setting up in guild: {ctx.guild.name}')
    gCategories = ctx.guild.categories
    gCategoryNames = []
    for gc in gCategories:
        gCategoryNames.append(gc.name)
    if 'Hidden Role Game' in gCategoryNames:
        print(f'Category found in guild: {ctx.guild.name}')
        gameCategory = discord.utils.get(ctx.guild.categories, name='Hidden Role Game')
        channels = gameCategory.channels
        print(channels)
        channelNames = []
        for ch in channels:
            channelNames.append(ch.name)
        print(channelNames)
        if 'lobby' in channelNames:
            print(f'Lobby text channel found in {ctx.guild.name}')
            # TODO assign guild lobby to this channel
        else:
            print(f'Creating text lobby in guild {ctx.guild.name}')
            textLobby = await gameCategory.create_text_channel(name='Lobby', position=0)
            # TODO assign guild lobby to this channel
        if 'Voice Lobby' in channelNames:
            print(f'Lobby voice channel found in {ctx.guild.name}')
            # TODO assign guild lobby to this channel
        else:
            print(f'Creating voice lobby in guild {ctx.guild.name}')
            voiceLobby = await gameCategory.create_voice_channel(name='Voice Lobby', position=1)
            # TODO assign guild lobby to this channel
    else:
        print(f'creating category, text lobby, voice lobby in guild {ctx.guild.name}')
        gameCategory = await ctx.guild.create_category(name='Hidden Role Game')
        await gameCategory.create_text_channel(name='Lobby', position=0)
        await gameCategory.create_voice_channel(name='Voice Lobby', position=1)

    await ctx.send('Everything is set-up!')


# Contact command
@client.command()
async def contact(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        await ctx.send('github page: https://github.com/Genthus/HRDiscBot \ne-mail: genthus0@gmail.com ')


# instructions command
@client.command(aliases=['howtoplay', 'HowToPlay', 'howToPlay'])
async def instructions(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        await ctx.send('A complete guide is here: https://github.com/Genthus/HRDiscBot#how-to-play')


# cleanup command
@client.command()
async def cleanup(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        print('someone tried to cleanup')
        await ctx.send('Sorry, this feature isnt available yet')

# delete category and channels if removed
@client.event
async def on_guild_remove(ctx):
    # TODO try to kill game, remove lobbies and category
    print(f'Bot removed from guild {ctx.guild.name}')


# Help command
@client.command(aliases=['bothelp', 'botHelp', 'aaaaaaaaaaaaa', 'hrprojecthelp'])
async def help(ctx):
    if ctx.channel.category.name == 'Hidden Role Game':
        await ctx.send(f'''`type any of the keywords to activate it\n
                       help: this message\n
                       instructions: link to the game guide\n
                       join: lets you join the lobby (this can only be done in the lobby)\n
                       startGame: starts the game\n
                       killGame: ends the game and deletes everything made for the current game`''')


# Kill all games
@atexit.register
def killAll():
    for k in guildDict.keys():
        guildDict[k].killGame()
    print(f'killed {len(guildDict)} games')


client.run(str(os.environ['botKey']))
