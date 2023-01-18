import discord
import openai
from gtts import gTTS
import soundfile as sf
from scipy.signal import resample
import random

demon_mode = False
sample_rates = [8000, 11025, 12000, 16000, 22050, 24000, 32000, 44100, 48000]

text_engine = "text-davinci-003"
image_engine = "image-alpha-001"

TOKEN = 'OTUzNzA0NzMxNDk3MzY1NjA2.GXPWnh.dH3JzBoCqB7cWEcnooFnJ4-GxDbjojqiHnkBgI'
CHATGPT_TOKEN = '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'
TENOR_TOKEN = 'AIzaSyCYWIpNV0IpZ9Sx9jkf0J29qoKtCRNWJkg'
DEEP_ART_TOKEN = '9b3hH3QBvsaqmXLUy1TgF1jqbgTSRCHk3sjgfJQG'

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

    # message.content = f"Marv is a chatbot that reluctantly answers questions with sarcastic responses:\n\nYou: How many pounds are in a kilogram?\nMarv: This again? There are 2.2 pounds in a kilogram. Please make a note of this.\nYou: What does HTML stand for?\nMarv: Was Google too busy? Hypertext Markup Language. The T is for try to ask better questions in the future.\nYou: When did the first airplane fly?\nMarv: On December 17, 1903, Wilbur and Orville Wright made the first flights. I wish they’d come and take me away.\nYou: What is the meaning of life?\nMarv: I’m not sure. I’ll ask my friend Google.\nYou: {message.content}\nMarv:"

    print(message.content)
    response = openai.Completion.create(
        model=text_engine,
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
    global demon_mode
    if message.author == client.user:
        return

    if 'demon mode' in message.content.lower():
        if demon_mode:
            await message.channel.send('demon mode off')
        else:
            await message.channel.send('demon mode engaged')
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

    if 'join kat' in message.content.lower() or 'join cat' in message.content.lower():
        if message.author.voice: # If the person is in a channel
            channel = message.author.voice.channel
            await channel.connect()
            await message.channel.send('Joined!')
        else: #But is (s)he isn't in a voice channel
            await message.channel.send("You must be in a voice channel first so I can join it.")
        return
    if 'leave kat' in message.content.lower() or 'leave cat' in message.content.lower():
        if (message.guild.voice_client): # If the bot is in a voice channel 
            await message.guild.voice_client.disconnect() # Leave the channel
            await message.channel.send('Bye!')
        else: # But if it isn't
            await message.channel.send("I'm not in a voice channel, use the join command to make me join.")
        return


    if 'cat' in message.content.lower() or 'kat' in message.content.lower():
        print(f"{message.author}: {message.content}")

        if 'cat draw' in message.content.lower() or 'kat draw' in message.content.lower():
            try:
                image = openai.Image.create(
                    prompt = (f"{message.content.lower()[9:]}"),
                    model = image_engine,
                    size = '512x512'
                )
                image_url = image["data"][0]["url"]
                await message.channel.send(image_url)
                return
            except openai.error.InvalidRequestError as e:
                message.content = "Respond as if you are an angry parent scolding a child for doing something rude: "
                await message.channel.send(response(message,False))
                return


            # endpoint = "https://api.deepart.io/1/post/art"
            # api_key = DEEP_ART_TOKEN
            # model = "Deevad"
            # image_url = "https://images.pexels.com/photos/559858/pexels-photo-559858.jpeg" #example of image url
            # data = {"image_url": image_url, "model_name": model, "prompt": message.content.lower()[9:]}
            # headers = {"Content-Type": "application/json", "Api-Key": api_key}
            
            # # Make the API request
            # response = requests.post(endpoint, json=data, headers=headers)
            # response_json = json.loads(response.text)
            
            # if "error" in response_json:
            #     raise ValueError(response_json["error"])
            
            # await message.channel.send(response_json["result_url"])

        # send the response
        str = response(message, True)
        if str != '':
            await message.channel.send(str)
            
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
