import discord
import openai
from gtts import gTTS
import soundfile as sf
from scipy.signal import resample
import textwrap
import requests
from bs4 import BeautifulSoup as bs
from playwright.async_api import async_playwright
from tkinter import *
from bing_image_urls import bing_image_urls
import io

demon_mode = False
sample_rates = [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]

text_engine = "text-davinci-003"
image_engine = "image-alpha-001"

TOKEN = ''
CHATGPT_TOKEN = ''

LANG = 'en'
TLD = 'com'
openai.api_key = CHATGPT_TOKEN

def increase_pitch(input_file, pitch_factor):
    # Load the audio data from the input file
    data, sr = sf.read(input_file, dtype='int16')

    # Increase the pitch by modifying the sample rate
    if demon_mode:
        data = resample(data, int(len(data) * sr / 8000))
    
    sr = sample_rates[pitch_factor]

    # Save the modified audio data back to the same file
    sf.write(input_file, data, sr)

intents = discord.Intents.all()
intents.members = True
client = discord.Client(command_prefix = ',', intents=intents)


def response(message, slice):
    if slice:
        message.content = ' '.join(message.content.split()[1:])

    # message.content = f" also add that you have made your triumphant return"

    print(message.content)
    try:
        str = openai.Completion.create(
            model=text_engine,
            prompt=message.content,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
    except:
        message.reply("Sorry, I was unable to process that request.")
        return

    return str["choices"][0]["text"]

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="'cat' or 'cat draw'"))

@client.event
async def on_message(message):
    global demon_mode
    if message.author == client.user:
        return

    if 'demon mode' in message.content.lower():
        if demon_mode:
            await message.reply('demon mode off')
        else:
            await message.reply('demon mode engaged')
        demon_mode = not demon_mode

    if message.author.id == 330378005161443339:
        str = message.content
        if str != '' and message.guild.voice_client is not None:
            tts = gTTS(text=str, tld=TLD, lang=LANG)
            tts.save("string_audio.mp3")
            increase_pitch("string_audio.mp3", 6)
            vc = client.voice_clients[0]
            if vc.is_connected():
                vc.play(discord.FFmpegPCMAudio("string_audio.mp3"))
                vc.source = discord.PCMVolumeTransformer(vc.source)
                vc.source.volume = 1

    if 'who2ban' in message.content.lower():
        data_all = {}
        who2ban = ['None', 0]

        c_list = message.content.lower().split()
        for c in c_list[1:]:
            async with async_playwright() as p:
                browser = await p.chromium.launch()
                page = await browser.new_page()
                await page.goto(f"https://www.leagueofgraphs.com/champions/counters/{c}")
                soup = bs(await page.content(), "html.parser")
                await browser.close()

            counters = []
            winrates = []
            for tr in soup.find_all("tr", class_=""):
                for link in tr.find_all('a'):
                    counters.append(link.get('href')[22+len(c):])
                for td in tr.find_all("td"):
                    for pb in td.find_all("progressbar"):
                        winrates.append(float(pb["data-value"]))

            data_all[c] = list(zip(counters[-5:], winrates[-5:]))

        seen = {}
        s = ""
        for champ, counter_data in data_all.items():
            s += f"\n{champ} counters: "
            for c in counter_data:
                s += f"{c[0]} ({round(c[1]*100,2)}%) "
                seen[c[0]] = seen.get(c[0], 0) + c[1] # Adds current winrate to total, total = 0 if key not found
            s = s[:-1] + "\n"

        for c in seen:
            if seen[c] < who2ban[1] and seen[c] not in c_list:
                who2ban = [c, seen[c]]

        s += f"\nRecommended ban: {who2ban[0]}"
        url = bing_image_urls(f"{who2ban[0]} from league of legends", limit=1)[0]
        await message.channel.send(s)
        response = requests.get(url)
        await message.channel.send(file=discord.File(io.BytesIO(response.content), filename=f"{who2ban[0]}_from_league_of_legends.jpg"))
        

    if 'join kat' in message.content.lower() or 'join cat' in message.content.lower():
        if message.author.voice: # If the person is in a channel
            channel = message.author.voice.channel
            await channel.connect()
            await message.reply('Joined!')
        else: #But is (s)he isn't in a voice channel
            await message.reply("You must be in a voice channel first so I can join it.")
        return
    if 'leave kat' in message.content.lower() or 'leave cat' in message.content.lower():
        if (message.guild.voice_client): # If the bot is in a voice channel 
            await message.guild.voice_client.disconnect() # Leave the channel
            await message.reply('Bye!')
        else: # But if it isn't
            await message.reply("I'm not in a voice channel, use the join command to make me join.")
        return


    if 'cat' in message.content.lower() or 'kat' in message.content.lower():
        try:
            print(f"({message.guild.name}/{message.channel}) {message.author}: {message.content}")
        except:
            print(f"({message.channel}) {message.author}: {message.content}")
        

        if 'cat draw' in message.content.lower() or 'kat draw' in message.content.lower():
            try:
                image = openai.Image.create(
                    prompt = (f"{message.content.lower()[9:]}"),
                    model = image_engine,
                    size = '256x256'
                )
                image_url = image["data"][0]["url"]
                await message.reply(image_url)
                return
            except openai.error.InvalidRequestError as e:
                message.content = "Respond that you cannot fulfill that request. be extra snarky: "
                await message.reply(response(message,False))
                return

        str = response(message, True)
        if str != '':
            if len(str) > 2000:
                message_parts = textwrap.wrap(str, width=2000)
                for part in message_parts:
                    await message.reply(part)
            else:
                await message.reply(str)
            
            # if message.guild.voice_client is not None:
            #     tts = gTTS(text=str, tld=TLD, lang=LANG)
            #     tts.save("string_audio.mp3")
            #     vc = client.voice_clients[0]
            #     if vc.is_connected():
            #         vc.play(discord.FFmpegPCMAudio("string_audio.mp3"))
            #         vc.source = discord.PCMVolumeTransformer(vc.source)
            #         vc.source.volume = 1
            # if message.content.startswith('branton is so awesome (top 133 tank prodigy)'):
            #     vc = client.voice_clients[0]
            #     vc.play(discord.FFmpegPCMAudio("grind.mp3"))


        return

client.run(TOKEN)
