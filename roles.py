import discord
from discord.ext import commands
import random

#Ability dictionary

#Base game role class
class gameRole:
    name = None
    team = None
    description = None
    winCondition = None
    ability = None

#Game role subclass template
class vvv(gameRole):
    name = vvv
    team = vvv
    description = vvv
    winCondition = None

    async def ability():
        #This is the ability
