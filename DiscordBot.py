import discord
import openai
import random
import asyncio

TOKEN = 'OTUzNzA0NzMxNDk3MzY1NjA2.GwrLT2.tSpsbE6ir819Ud6JYTU-A_x5z8CM4or9c8VsEs'
CHATGPT_TOKEN = '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'
openai.api_key = CHATGPT_TOKEN


intents = discord.Intents.all()
intents.members = True
client = discord.Client(command_prefix = ',', intents=intents)

def response(message, slice):
    if slice:
        message.content = message.content[9:]
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=message.content,
        max_tokens=1024,
        temperature=0.7,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response["choices"][0]["text"]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    # don't respond to our own messages
    # if random.random() < 0.2:
    #     return
    print(f"{message.author}: {message.content}")
    if message.author == client.user:
        return
    if len(message.content) >= 8 and message.content[:9].lower() == 'hey bitch':
        # send the response
        await message.channel.send(response(message, True))
        return
    # else:
    #     if random.random() < 0.2:
    #         await message.channel.send(response(message, False))

client.run(TOKEN)
