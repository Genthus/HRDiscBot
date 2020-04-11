import roles
import asyncio
import math
import challanges
import random


class Game():
    # Guild lobbies
    serverLobbyTextChannel = None
    serverLobbyVoiceChannel = None
    # Game channels
    gameChallangeRoom = None
    gameVoiceChannel = None
    # player variables and lists
    currentPlayerList = []
    playerClassList = []
    leaderRole = None
    leaderPlayer = None
    playersToBeChallanged = []
    playersNominated = []
    challangeClass = None
    # Game-state variables
    gameIsRunning = False
    firstRoundIsOver = False
    gameState = 0
    currentRound = 0
    votingOpen = False
    yesVotes = 0
    noVotes = 0
    playersWhoVoted = []
    CyberPoliceTeamWins = 0
    HackerTeamWins = 0
    currentTimer = 0
    currentTimerString = ''
    # Settings
    shortTime = 15  # time for short timers such as voting
    challangeSize = [1, 1, 3, 4, 4, 5, 4]
    # TODO revert the challange size
    roundTime = [3, 4, 5, 5, 6, 6, 6]
    roleSetMode = 'basic'
    # Clean-up lists
    rolesCreated = []
    channelsCreated = []

    #
    # Functions
    #

    # Reset all
    def reset(self):
        # Guild lobbies
        self.serverLobbyTextChannel = None
        self.serverLobbyVoiceChannel = None
        # Game channels
        self.gameChallangeRoom = None
        self.gameVoiceChannel = None
        # player variables and lists
        self.currentPlayerList.clear()
        self.playerClassList.clear()
        self.leaderRole = None
        self.leaderPlayer = None
        self.playersToBeChallanged.clear()
        self.playersNominated.clear()
        self.challangeClass = None
        # Game-state variables
        self.gameIsRunning = False
        self.firstRoundIsOver = False
        self.gameState = 0
        self.currentRound = 0
        self.votingOpen = False
        self.yesVotes = 0
        self.noVotes = 0
        self.playersWhoVoted.clear()
        self.CyberPoliceTeamWins = 0
        self.HackerTeamWins = 0
        self.currentTimer = 0
        self.currentTimerString = ''
        # Settings
        self.shortTime = 15  # time for short timers such as voting
        self.challangeSize = [1, 1, 3, 4, 4, 5, 4]
        # TODO revert the challange size
        self.roundTime = [3, 4, 5, 5, 6, 6, 6]
        self.roleSetMode = 'basic'
        # Clean-up lists
        self.rolesCreated.clear()
        self.channelsCreated.clear()

    # Send message to all player dashboards
    async def globalMessage(self, message):
        messageList = []
        for pl in self.playerClassList:
            x = await pl.playerChannel.send(message)
            messageList.append(x)
        return messageList

    # Send message to a player dashboard
    async def personalMessage(self, pC, message):
        messageSent = await pC.playerChannel.send(message)
        return messageSent

    # Challange room transfer
    async def challangeTransfer(self):
        self. playersToBeChallanged = self.playersNominated
        self.playersNominated = []
        for pl in self.playersToBeChallanged:
            await pl.user.move_to(self.gameChallangeRoom)
            await self.personalMessage(pl, f'You are now in the challange room. \n Prepare yourselves')

    # Return challangers to main
    async def challangeReturn(self):
        for pl in self.playersToBeChallanged:
            await pl.user.move_to(self.gameVoiceChannel)
            await self.personalMessage(pl, 'You are now back in the main voice channel')
        self.playersToBeChallanged = []

    # Mute everyone in a voice channel
    async def muteVoiceChannel(channelToMute):
        await channelToMute.set_permissions(channelToMute.guild.default_role, speak=False)

    # Unmute everyone in a voice channel
    async def unmuteVoiceChannel(channelToMute):
        await channelToMute.set_permissions(channelToMute.guild.default_role, speak=True)

    # Returns list of current players as a message
    async def playerListMessage(self):
        message = ''
        m = 1
        for pl in self.playerClassList:
            message += f'{m}. {pl.user.name}\n'
            m = +1
        return(message)

    # Set gameRoles
    async def setGameRoles(self):
        modes = {
            'basic': roles.basic
        }
        await modes.get(self.roleSetMode, 'basic')(self.playerClassList)
        for pl in self.playerClassList:
            await self.personalMessage(pl,
                                  f'''Your role is {pl.gameRole.name}\n
                                  You are part of the {pl.gameRole.team} team\n
                                  {pl.gameRole.description}\n
                                  {pl.gameRole.winCondition}\n
                                  {pl.gameRole.abilityDescription}
                                  ''')
            if pl.gameRole.name == 'Hacker':
                await pl.gameRole.ability(self.playerClassList, pl)

    # Switch leader role
    async def switchLeader(self):
        if len(self.leaderRole.members) > 0:
            currentLeader = self.leaderPlayer
            await self.leaderPlayer.user.remove_roles(self.leaderRole)
            leaderFound = False
            # Cycle to find leader and give to the next person
            # This cycles in the order they joined the lobby
            for pl in self.playerClassList:
                if leaderFound is True:
                    await pl.user.add_role(self.leaderRole)
                    self.leaderPlayer = pl
                if pl == currentLeader:
                    leaderFound = True
                    if pl == self.playerClassList[-1]:
                        await self.playerClassList[0].user.add_roles(self.leaderRole)
                        self.leaderPlayer = pl

    # Voting function
    async def startVote(self):
        self.votingOpen = True
        await self.globalMessage('''The voting proccess is now open, type "vote yes" or "vote no"\n
                            Not voting counts as voting no\nThe nominated party is: ''')
        for pl in self.playersNominated:
            await self.globalMessage(f'{pl.user.name}')
        voteTimer = self.shortTime
        voteTimerRange = range(voteTimer)
        voteTimerMessage = await self.globalMessage(f'You have {voteTimer} seconds to vote')
        for t in voteTimerRange:
            await asyncio.sleep(1)
            voteTimer -= 1
            for ch in voteTimerMessage:
                await ch.edit(content=f'You have {voteTimer} seconds to vote')
        noVotes = len(self.playerClassList)-self.yesVotes
        if self.yesVotes > noVotes:
            await self.globalMessage(
                f'''The vote has passed with {self.yesVotes} yes votes against {noVotes}\n
                In 15 seconds the players will be sent to the challange room.''')
            await asyncio.sleep(15)
            await self.switchLeader()
            self.playersWhoVoted = []
            self.votingOpen = False
            self.yesVotes = 0
            self.noVotes = 0
            return 1
        else:
            await self.globalMessage("""The vote didn't pass. Leadership will be transfered and the nomination process will restart.""")
            await self.switchLeader()
            self.playersNominated = []
            self.playersWhoVoted = []
            self.votingOpen = False
            self.yesVotes = 0
            self.noVotes = 0
            return 0

    # Setup the round timer
    async def setRoundTimer(self, round):
        currentTimer = self.roundTime[round]*60
        originalTime = currentTimer
        timerMessage = await self.globalMessage(f'Time remaining: {self.currentTimerString}')
        await self.leaderPlayer.playerChannel.send(f'\nThese are the available players:\n {await self.playerListMessage()}')
        for n in range(originalTime):
            if len(self.playersNominated) < self.challangeSize[round]:
                currentTimer -= 1
                currentTimerString = f'{math.floor(currentTimer/60)}:{currentTimer%60}'
                await asyncio.sleep(1)
                for m in timerMessage:
                    if len(self.playersNominated) > 0:
                        nomineesString = ''
                        for pl in self.playersNominated:
                            nomineesString += f'{pl.user.name}\n'
                        await m.edit(content=f'''Time Remaining: {currentTimerString}\n
                                     The current nominees are: {nomineesString}''')
                    elif self.gameIsRunning is False:
                        break
                    else:
                        await m.edit(content=f'''Time Remaining: {currentTimerString}\n
                                     There are currently no nominated players''')
                    if self.playersNominated == self.challangeSize[round]:
                        await m.delete()
                        await self.globalMessage('The nominees have been decided.')
                        break

    # Retry state 1
    async def retryPartySelect(self):
        a0 = await self.switchGameState(1)
        if a0 == 'voteFailed':
            a1 = await self.switchGameState(1)
            if a1 == 'voteFailed':
                a2 = await self.switchGameState(1)
                if a2 == 'voteFailed':
                    a3 = await self.switchGameState(1)
                    if a3 == 'voteFailed':
                        a4 = await self.switchGameState(1)
                        if a4 == 'voteFailed':
                            print('failed to choose party 5 times')
                            return 'voteFailed'
        else:
            return 'votePassed'

    # Announce score
    async def scoreboard(self):
        await self.globalMessage(f'''The current score is\n
                            Cyber Police: {self.CyberPoliceTeamWins}\n
                            Hackers: {self.HackerTeamWins}''')

    # Function to end the game
    async def killGame(self):
        # Delte created roles
        for rl in self.rolesCreated:
            try:
                await rl.delete()
            except:
                print()
        print('roles deleted')
        # Move players back to original voice chat
        for pl in self.currentPlayerList:
            await pl.move_to(self.serverLobbyVoiceChannel)
        # Delete created channels
        for ch in self.channelsCreated:
            try:
                await ch.delete()
            except:
                print()
        self.gameIsRunning = False
        print('channels deleted')

    # Check for victory
    async def victoryCheck(self):
        if self.CyberPoliceTeamWins >= 4:
            print('Cyber Police team won')
            await self.globalMessage('''The Cyber Police team has won the game!\n
                                    The game will close in 30 seconds''')
            return 'end'

        elif self.HackerTeamWins >= 4:
            print('Hacker team won')
            await self.globalMessage('''The Hacker team has won the game!\n
                                    The game will close in 30 seconds''')
            return 'end'

    # Whole 7 round game function
    async def gameFlow(self):
        # Give roles
        print(self.playerClassList)
        await self.setGameRoles()
        print('gameroles set')
        await asyncio.sleep(15)
        # Round 1:4
        for r in range(3):
            if self.gameIsRunning is False:
                print('gameFlow broken')
                break
            r1 = await self.retryPartySelect()
            if r1 == 'voteFailed':
                await self.globalMessage('''Since no party was selected for 5 consecutive votes,
                                the game is over and will be forced to end''')
                await asyncio.sleep(30)
                await self.killGame()
            else:
                await self.switchGameState(2)
                await self.scoreboard()
                self.currentRound += 1
        # rounds 5:7
        for r in range(2):
            if self.gameIsRunning is False:
                print('gameFlow broken')
                break
            r1 = await self.retryPartySelect()
            if r1 == 'voteFailed':
                await self.globalMessage('''Since no party was selected for 5 consecutive votes,
                                the game is over and will be forced to end''')
                await asyncio.sleep(30)
                await self.killGame()
            else:
                await self.switchGameState(2)
                await self.scoreboard()
                if await self.victoryCheck() == 'end':
                    await asyncio.sleep(30)
                    await self.killGame()
                    self.currentRound += 1

    # Function to switch gamestate
    async def switchGameState(self, stateToSwitchTo):
        gameState = stateToSwitchTo

        # Party pick phase
        if gameState == 1 and self.gameIsRunning is True:
            self.gameState = 1
            print('switched to game state 1')
            if self.firstRoundIsOver is False:
                await self.globalMessage('Welcome to HRProject, the game will now begin')
                # TO-DO add prompt for rules and instructions here
                await self.globalMessage(f"""For the first round, you will have {self.roundTime[0]} minutes to decide the party.\n
                                If the current leader doesn't decide within the time alloted, the role of leader will be appointed to someone else\n
                                The time begins now""")
                self.firstRoundIsOver = True

            await self.globalMessage(f'The current leader is {self.leaderPlayer.user.mention}, to nominate players, type "nominate a b c",where a b and c are the numbers of the players you wish to nominate\nThe leader must nominate {self.challangeSize[self.currentRound]} players')
            await self.setRoundTimer(self.currentRound)
            result = await self.startVote()
            if result == 1:
                return 'votePassed'
            elif result == 0:
                return 'voteFailed'

        # Challange room phase
        if gameState == 2 and self.gameIsRunning is True:
            self.gameState = 2
            await self.globalMessage('The selected party will now be sent to the challange room')
            await self.challangeTransfer()
            await asyncio.sleep(5)
            # TODO uncomment this once abilities are back in
            # for pl in self.playerClassList:
            # if pl not in self.playersToBeChallanged:
                # pl.gameRole.addCharge()
                # await self.personalMessage(pl, "Your ability has recieved charge")
            challangePicked = random.choice(list(challanges.challangeDict.keys()))
            self.challangeClass = challanges.challangeDict.get(challangePicked, 'PickLetters')(self.playersToBeChallanged)
            result = await self.challangeClass.startChallange()
            self.challangeClass = None
            await self.challangeReturn()
            if result == 'fail':
                self.HackerTeamWins += 1
            elif result == 'success':
                self.CyberPoliceTeamWins += 1

    def __init__(self, playerLobby):
        self.currentPlayerList = playerLobby
