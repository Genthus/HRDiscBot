<<<<<<< Updated upstream
import random
=======
import random, asyncio, math

#Challange dictionary
challangeDict = {
    'letters' : PickLetters
}

answers = {}

class Challange():
    challangerList = []
    numberOfChallangers = 0
    description = ''
    timer = 60

    def __init__(self, plc):
        self.challangerList = plc
        self.numberOfChallangers = len(plc)

    async def challangeMessage(self, message):
        messageList = []
        for pl in self.challangerList:
            x = await pl.playerChannel.send(message)
            messageList.append(x)
        return messageList

    async def startTimer(self):
        timer = self.timer
        timerRange = range(timer)
        timerMessage = await challangeMessage(f'You have {timer} seconds')
        for t in timerRange:
            await asyncio.sleep(1)
            timer-=1
            for m in timerMessage:
                await m.edit(content = f'You have {timer} seconds')

    async def condition():
        return 'success'

    async def startChallange(self):
        await challangeTask()
        challangeMessage(self.description)
        await startTimer
        global answers
        result = condition(answers)
        answers = {}
        return self.result




class PickLetters(Challange):

    async def challangeTask(self):
        letterList = 'abcdefghijklmnopqrstuvwxyz'.split('')
        print(letterList)
        correctAnswers = {}
        for pl in challangerList:
            letterList = letterList[0:numberOfChallangers]

    description = f'There are {numberOfChallangers} letters, each of you must pick a different letter to succeed the challange.\nThe letters are *{letterList}\n\n*'

    async def condition(self, answersDict):
        for p1 in challangerList:
            for p2 in challangerList:
                if answersDict[p1.user.name] == answersDict[p2.user.name] and p1 != p2:
                    return 'fail'
        return 'success'
>>>>>>> Stashed changes
