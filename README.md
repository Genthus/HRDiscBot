![Python application](https://github.com/Genthus/HRDiscBot/workflows/Python%20application/badge.svg)
# HRDiscBot

This is a personal project, the original intent was to adapt Ultimate Werewolf (Bezier Games, 2008) so that it could be played over discord, however I also wanted to make The Resistance: Avalon (Indie Boards & Cards, 2012), so I ended up making a debatably new game that incorporates my favorite elements of both games.

The game is played over Discord, you could make the bot and add it to your server but I would recommend to create a new server and add it to that one instead, just in case.

### Current functionality

Running a basic game in a single server.

### Planned functionality

More player roles, new challenges, being able to run multiple games in a single server, saving stats, new role selecting algorithm.

## Set-up

<ol>
<li>Create a Discord bot</li>
    If you're not sure how to do it, follow this guide https://discordpy.readthedocs.io/en/latest/discord.html#creating-a-bot-account.
<li>Get the latest release from this page</li>
<li>Add your bot key</li>
    Create a file called botKey.py in the folder where you put the release and write "key='your bot key here'" into it.
<li>Create a new Discord server and invite the bot</li>
<li>Run the .exe file</li>
<li>type "prepareServer" into any text channel</li>
</ol> 

## How to Play

#### Game setup

First off, get a few friends to join your sever and have everyone join a voice channel. After that, type "join" into the lobby text channel, this will create a game lobby, now everyone can join by typing "join" in the same channel you did (You can type "players" to see the players currently in the lobby or "clearLobby" to clean the lobby).

Once everyone is in, type "startGame", this will create the necessary game channels and everyone's own text channel, any player should only type and read from their own dashboard (the server owner can see every channel, but peeking is considered cheating).

#### Introduction

This is a hidden role game (also called social deduction, or hidden identity games), the players will be given roles and split into two teams, Hackers and Cyber Police; the hackers are the people who want stuff to fail, the Cyber Police not so much. All this information will be delivered through your dashboard. All the hackers know who eachother are, but the desk workers don't know who anyone is.

#### Party picking phase

After a few seconds, the first part of the game will start, randomly assigning a player the role of leader. The leader must nominate a certain number of players to be sent on a challange (the leader can nominate himself), to do this, just type "nominate" and the number of the player (don't worry, there'll be a message with the numbers for each player), alternatively, you can type "nominate genthus" to nominate a player with their name, however Discord names are not always easy to type. Everyone will see who has been nominated, and after the ammount of nominees has beed filled, every player will be asked to vote if they want the party nomineed to go on the challange, this is done by typing "vote yes" or "vote no" (you can also type "yes" or "no" during this phase).

If there are more yes votes than no votes when the timer ends, the party will be sent onto the challange room and the next phase of the game will start. However, if the vote doesn't pass, the leader will be passed to the next player (the order depends on when people joined), and the Party picking phase will restart. If this happens five consecutive times the game ends and nobody wins.

#### Challange phase

A few seconds after the vote passes, the nominated party will be sent to a different voice channel, so they can attempt to coordinate and solve the challange, everyone else is left to discuss strategy or make baseless acussations. The party will be asked to pick a letter from a list, to succeed, they must each pick a different letter, but be careful, the hackers may be intentionaly trying to pick the same letter as you. You will have a minute to make your pick, which can be done by typing "pick" followd by the letter you wish to pick.

If everyone in the challange picked a different letter, congratulations, the challange was a success! And a point gets awarded to the Cyber Police team. However if two or more people picked the same letter, the challange fails, and a point gets awarded to the Hacker team. The first team to get to four points wins.

After this is all done, everyone is sent back to the game's voice channel, results are shown, and if a team has accumulated four points, the game ends. But that can't happend on the first round, so once again the leader is rotated and the game switches back to the party picking phase.

#### TL;DR
<ol>
    <li>Get everyone in a voice channel</li>
    <li>Type "join" in the lobby</li>
    <li>Type "startGame" once everyone is in</li>
    <li>Hackers want to fail challanges, desk workers want to succeed</li>
    <li>The leader nominates players by typing "nominate" + the number of the players separated by spaces</li>
    <li>Everyone types "vote yes" or "vote no" on the party nominated</li>
    <li>If the vote doesn't pass, go back to step 5, if this happens five times, the game ends</li>
    <li>The party is sent to the challange room</li>
    <li>Inside the challange, type "pick" followed by the letter you wish to pick</li>
    <li>If two or more people pick the same letter, the challange fails, if they don't, it succeeds</li>
    <li>The game ends when a team gets four points</li>
