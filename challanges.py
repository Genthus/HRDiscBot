import asyncio

answers = {}


class Challange():
    challangerList = []  # player class list
    numberOfChallangers = 0
    description = ''
    timer = 60

    def __init__(self, plc):
        self.challangerList = plc
        self.numberOfChallangers = len(plc)

    async def challangeMessage(self, players, message):
        messageList = []
        for pl in players:
            x = await pl.playerChannel.send(message)
            messageList.append(x)
        return messageList

    async def startTimer(self, players):
        timer = self.timer
        timerRange = range(timer)
        timerMessage = await self.challangeMessage(players, f'You have {timer} seconds')
        for t in timerRange:
            await asyncio.sleep(1)
            timer -= 1
            for m in timerMessage:
                await m.edit(content=f'You have {timer} seconds')


class PickLetters(Challange):
    letterList = []

    async def challangeTask(self, players):
        letterList = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split(' ')
        for pl in players:
            self.letterList = letterList[0:len(players)]
        print(self.letterList)

    def returnDesc(self, players):
        return f'There are {len(players)} letters, each of you must pick a different letter to succeed the challange.\nThe letters are **{self.letterList}**\n\nTo pick a letter type "pick" and then the letter you want to pick'

    async def condition(self, answersDict, players):
        for p1 in players:
            for p2 in players:
                if answersDict[p1.user.name] == answersDict[p2.user.name] and p1 != p2:
                    return 'fail'
        return 'success'

    async def startChallange(self):
        await self.challangeTask(self.challangerList)
        await self.challangeMessage(self.challangerList, self.returnDesc(self.letterList))
        await self.startTimer(self.challangerList)
        global answers
        result = await self.condition(answers, self.challangerList)
        answers = {}
        return result


# Challange dictionary
challangeDict = {
    'letters': PickLetters
}
