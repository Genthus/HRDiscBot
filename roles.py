import random

rolesDict = {
    Hacker:-3,
    DeskWorker:1
}
#Ability function library
async def revealHackers():
    message = 'The hacker team is:\n'
    for pl in playerClassList:
        if pl.gameRole.team == 'hackers':
            message += f'{pl.user.name}\n'
    await personalMessage(playerClass, message)

#Base game role class
class gameRole:
    playerClass = None
    name = None
    team = None
    description = None
    winCondition = None
    balanceScore = None
    ability = None
    charge = 0
    chargePerRound = 0
    chargeNeeded = 1

    def addCharge():
        global charge
        charge += chargePerRound

    def __init__(self, pC):
        self.playerClass = pC

#Game role subclass template
class vvv(gameRole):
    name = vvv
    team = vvv
    description = vvv
    winCondition = None
    async def ability():
        #This is the ability

class Hacker(gameRole):
    name = 'Hacker'
    team = 'hackers'
    description = 'Generic hacker'
    winCondition = 'You and the other hackers win if 4 challanges are failed'
    balanceScore = -3
    charge = 1
    chargePerRound =  0
    async def ability():
        global charge
        if charge >= chargeNeeded:
            charge -= chargeNeeded
            await revealHackers()

class DeskWorker(gameRole):
    name = 'Desk Worker'
    team = 'Cyber Police'
    description = 'You are a run off the mill desk worker, no special powers.'
    winCondition = 'You and the Cyber Police win if 4 challanges succeed'
    balanceScore = 1
    async def ability():
