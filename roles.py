import random
import math


# Send message to a player dashboard
async def personalMessage(playerClass, message):
    messageSent = await playerClass.playerChannel.send(message)
    return messageSent
# Roles dictionary


# Ability function library
async def revealHackers(user, playerClasses):
    message = 'The hacker team is:\n'
    for pl in playerClasses:
        if pl.gameRole.team == 'hackers':
            message += f'{pl.user.name}\n'
    await personalMessage(user, message)


# Base game role class
class gameRole:
    playerClass = None
    name = str
    team = str
    description = str
    winCondition = str
    balanceScore = str
    ability = None
    charge = 0
    chargePerRound = 0
    chargeNeeded = 1
    abilityDescription = ''

    async def addCharge(self):
        if self.charge < self.chargeNeeded:
            self.charge += self.chargePerRound


class Hacker(gameRole):
    name = 'Hacker'
    team = 'hackers'
    description = 'Generic hacker'
    winCondition = 'You and the other hackers win if 4 challanges are failed'
    balanceScore = -3
    charge = 1
    chargePerRound = 0

    async def ability(self, players, user):
        if self.charge >= self.chargeNeeded:
            self.charge -= self.chargeNeeded
            await revealHackers(user, players)


class DeskWorker(gameRole):
    name = 'Desk Worker'
    team = 'Cyber Police'
    description = 'You are a run off the mill desk worker, no special powers.'
    winCondition = 'You and the Cyber Police win if 4 challanges succeed'
    balanceScore = 1


# Role setting algorithms
async def basic(playerClasses):
    if len(playerClasses) > 2:
        hackerCount = math.floor(len(playerClasses)/3)
    else:
        hackerCount = 1
    print(f'set to have {hackerCount} hackers')
    playersWithoutRole = range(len(playerClasses))
    playersWithRole = []
    # Set hackers
    for h in range(hackerCount):
        c = random.choice(playersWithoutRole)
        playersWithRole.append(c)
        playerClasses[c].gameRole = Hacker()
        print(f'set {playerClasses[c].user.name} as {playerClasses[c].gameRole.name}')
    # Set everyone else as desk workers
    for pl in playersWithoutRole:
        if pl in playersWithRole:
            continue
        else:
            playerClasses[pl].gameRole = DeskWorker()
            print(f'set {playerClasses[pl].user.name} as {playerClasses[pl].gameRole.name}')
