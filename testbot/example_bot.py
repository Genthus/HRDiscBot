import discord

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

    if message.content.startswith('createChannel'):
        channel = await guild.create_text_channel('cool-channel')
client.run('Njk1NDQ4MDUxNjkwNTA0MzEz.XoaUvg.PH5NCSJvujw5k2HRV3gfGLCNvvA')

# Run Command
# py -3 C:\Users\solra\Documents\HRProject\testbot\example_bot.py
