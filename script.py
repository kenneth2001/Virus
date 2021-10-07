import asyncio
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
import discord
import numpy as np
from urllib.error import HTTPError
import yt_dlp as youtube_dl
from discord.ext import commands
import sympy
import matplotlib.pyplot as plt
import os
from pytz import timezone
from yt_dlp.utils import DownloadError, ExtractorError
from util.log import pretty_output, pretty_print
from util.preprocessing import load_config, load_gif, load_user
#from util.keep_alive import keep_alive # For setting up bot on replit.com
import secrets

try:
    print('LOADING config.txt')
    TOKEN, TIMEZONE = load_config('config/config.txt')
    print('LOADED config.txt\n')
except:
    print('ERROR LOADING config.txt\n')

tz = timezone(TIMEZONE)
token = TOKEN #os.environ['token']

try:
    print('LOADING gif.json')
    gif = load_gif('config/gif.json')
    print('LOADED gif.json\n')
except:
    print('ERROR LOADING gif.json\n')
    
try:
    print('LOADING user.json')
    user = load_user('config/user.json')
    print('LOADED user.json\n')
except:
    print('ERROR LOADING user.json\n')

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' 
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

# channel_var stores all variable for differnet channels
# key: serverid
# value: 1. activated[bool] - indicate whether the music playing function is activated
#        2. bully[dict] - list of user being bullied
#        3. ctx[object]
#        4. log[list] - log of user entering / leaving voice channels
#        5. playing[bool] - indicate whether the bot is playing music
#        6. queue[list] - list of music to be played
channel_var = {}

# return gif link
def send_gif(msg):
    if msg in gif.keys():
        return gif[msg]

# Wong Tai Sin Fortune Sticks (黃大仙求籤)
def get_stick(tag):
    num = np.random.randint(1, 101)
    URL = f'https://andy.hk/divine/wongtaisin/{num}'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    result = soup.find(id='content')
    job_elements = result.find("div", class_="inner-padding col-md-5 col-md-offset-7")
    stick_no = job_elements.find('h2', class_='id-color text-center').text
    stick_author = job_elements.find_all('h4', class_='text-center')[0].text
    stick_content = job_elements.find_all('h4', class_='text-center')[1].text
    stick_explain = job_elements.text.split('仙機：')[1].split('解說及記載：')[0]
    stick_story = job_elements.text.split('仙機：')[1].split('解說及記載：')[1].split('■')[0]
    text = tag + '求得' + stick_no + '\n' + stick_author + '\n\n籤文:\n' + stick_content + '\n\n仙機：' + stick_explain + '\n解說及記載' + stick_story
    return text

client = commands.Bot(command_prefix='#', help_command=None)

@client.event
async def on_connect():
    print("Bot activated successfully")

async def initialize(server_id: int, ctx: object=None):
    """Initializing channel_var
    
    Args:
        server_id (int)
        ctx (object, optional): Defaults to None.
    """
    global channel_var
    info = channel_var.get(server_id, -1)
    if info != -1:
        if channel_var[server_id]['ctx'] == None and ctx != None:
            channel_var[server_id]['ctx'] = ctx
        return
    else:
        channel_var[server_id] = {'ctx':ctx, 'queue':[], 'activated':False, 'playing':True, 'log':[], 'bully':{}}
    

@client.event
async def on_voice_state_update(member, before, after):
    server_id = member.guild.id
    await initialize(server_id)
    global channel_var
    
    if before.channel is None and after.channel is not None:
        channel_var[server_id]['log'].append([datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), '*' + str(member) + '* Entered `' + str(after.channel) + '`'])
    if before.channel is not None and after.channel is None:
        channel_var[server_id]['log'].append([datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), '*' + str(member) + '* Leaved `' + str(before.channel) + '`'])
    if before.channel is not None and after.channel is not None:
        channel_var[server_id]['log'].append([datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S'), '*' + str(member) + '* Leaved `' + str(before.channel)+ '`, Joined `' + str(after.channel) + '`'])  
        
      
@client.command(name='log')
async def log(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var
        
    if len(channel_var[ctx.guild.id]['log']) == 0:
        return
    
    embed = discord.Embed(color = discord.Colour.red())
    embed.set_author(name='Log (Recent 20 records)')
    for field in channel_var[ctx.guild.id]['log'][-20:]:
        embed.add_field(name=field[0], value=field[1], inline=False)
    await ctx.send(embed=embed)   

async def play_music(ctx):
    while not client.is_closed():
        global channel_var
        if not len(channel_var[ctx.guild.id]['queue']) == 0 and ctx is not None:
            server = ctx.message.guild
            voice_channel = server.voice_client
            if (voice_channel and voice_channel.is_connected() and not voice_channel.is_playing() and channel_var[ctx.guild.id]['playing']) == True:
                server = ctx.message.guild
                voice_channel = server.voice_client
                try:
                    link = channel_var[ctx.guild.id]['queue'][0][1]
                    title = channel_var[ctx.guild.id]['queue'][0][2]
                    player = discord.FFmpegPCMAudio(link, **ffmpeg_options)
                    voice_channel.play(player)
                    await ctx.send(f'**Now playing:** {title}')
                except DownloadError:
                    await ctx.send(f'**Download error:** {title}')
                    
                del(channel_var[ctx.guild.id]['queue'][0])
        await asyncio.sleep(1)
                  
@client.command(name='play')
async def play(ctx, *url):
    url = ' '.join(url)

    await initialize(ctx.guild.id, ctx)
    global channel_var
    
    def music(link):
        with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
            info = ydl.extract_info(link, download=False)
        
        # Handle if the url is a playlist
        if 'entries' in info:
            info = info['entries'][0]
        
        LINK = info['webpage_url']
        URL = info['url']
        TITLE = info['title']
        return LINK, URL, TITLE
    
    if not ctx.message.author.voice: # handle if message author is not inside any voice channel
        await ctx.send(**"You are not connected to a voice channel**")
        return
    elif ctx.message.guild.voice_client: # if bot is inside any voice channel
        if ctx.message.guild.voice_client.channel != ctx.message.author.voice.channel: # if bot is not inside the author's channel
            channel = ctx.message.author.voice.channel
            user = await ctx.guild.fetch_member(client.user.id)
            ctx.voice_client.pause()
            await user.move_to(channel)
            ctx.voice_client.resume()
    else: # if bot is not inside any voice channel
        channel = ctx.message.author.voice.channel
        await channel.connect() # connect to message author's channel
    
    server = ctx.message.guild
    voice_channel = server.voice_client
   
    if url is None or url == '':
        if len(channel_var[ctx.guild.id]['queue']) == 0:
            return
    else:
        try:
            link, player_link, title = music(url)
            channel_var[ctx.guild.id]['queue'].append([link, player_link, title])
        except ExtractorError:
            await ctx.send('**Error:** ' + url)
        except HTTPError:
            await ctx.send('**Error:** ' + url)
        except DownloadError:
            await ctx.send('**Error:** ' + url)
    
    # activate music playing function
    if channel_var[ctx.guild.id]['activated'] == False:
        channel_var[ctx.guild.id]['activated'] = True
        await play_music(ctx)

@client.command(name='debug')
async def debug(ctx):
    def check(m):
        return m.author == ctx.message.author
    
    func_token = secrets.token_hex(10)
    print("Token:", func_token)
    await ctx.send('**Please type in the token displayed in console**')
    msg = await client.wait_for("message", check=check)
    if msg.content == func_token:
        pretty_print(channel_var)
        pretty_output(channel_var, filename='tmp.json')
        await ctx.send(file=discord.File('tmp.json'))
    else:
        await ctx.send("**Only admin can use this command**")

@client.command(name='queue')
async def queue_(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var
        
    if len(channel_var[ctx.guild.id]['queue']) == 0:
        await ctx.send('**Queue is empty!**')
    else:
        async with ctx.typing():
            await ctx.send('\n'.join([f'{idx}. {item[2]}\n{item[0]}' for idx, item in enumerate(channel_var[ctx.guild.id]['queue'], start=1)]))
            
@client.command(name='stop')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='gpa')
async def gpa(ctx):
    x = round(np.random.uniform(3,4) - np.random.normal(0, 1), 2)
    text = 4.0 if x > 4 else x
    if text >= 3.8:
        text = "Predicted GPA: " + str(text)
    elif text >= 3.0:
        text = "Predicted GPA: " + str(text)
    elif text >= 2.5:
        text = "Predicted GPA: " + str(text)
    else:
        text = "Predicted GPA: " + str(text)
        
    tag = "<@" + str(ctx.message.author.id) + ">"
    await ctx.message.channel.send(str(text)+tag)

@client.command(name='pause')
async def pause(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var

    channel_var[ctx.guild.id]['playing'] = False
    
    if ctx.voice_client is not None:
        ctx.voice_client.pause()
        await ctx.send('**Paused**')

@client.command(name='resume')
async def resume(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var

    channel_var[ctx.guild.id]['playing'] = True

    if ctx.voice_client is not None:
        ctx.voice_client.resume()
        await ctx.send('**Resumed**')
        
@client.command(name='skip')
async def skip(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var
    
    if ctx.voice_client is not None:
        ctx.voice_client.stop()
        await ctx.send('**Skipped**')
        
@client.listen()
async def on_message(message):
    author = message.author
    author_id = str(message.author.id)
    tag = "<@" + str(message.author.id) + ">"
    msg = message.content.lower()
    
    if author == client.user:
        return
    
    #print('Debugging:', author, msg)
    
    today = date.today()
    
    if user.get(author_id, -1) != -1:
        if user[author_id]['date'] != today:
            user[author_id]['date'] = today
            await message.channel.send(user[author_id]['text'] + tag)
    
    if message.content.startswith('#hello'):
        await message.channel.send("Hello World!")
   
    gif = send_gif(msg)
    if gif is not None:
        await message.channel.send(gif)

@client.command(name='help')
async def help(ctx):
    embed = discord.Embed(title="Virus", url="https://github.com/kenneth2001/virus", description="Discord Bot developed by YeeKiiiiii 2021", color=discord.Colour.blue())
    embed.set_author(name="Virus", url="https://github.com/kenneth2001/virus", icon_url="https://user-images.githubusercontent.com/24566737/132656284-f0ff6571-631c-4cef-bed7-f575233cbf5f.png")
    
    embed.add_field(name=':musical_note: __Music__', value="""1. `#play [url]` Play music, tested platform: Youtube, Soundcloud
                                                          2. `#pause` Pause music
                                                          3. `#resume` Resume music
                                                          4. `#skip` Play next song
                                                          5. `#queue` Display the queue
                                                          6. `#stop` Kick the bot from voice channel""", inline=False)
    
    embed.add_field(name=':pencil2: __Graph (Developing)__', value="""1. `#plot` Create simple scatter/line plot""", inline=False)
    
    embed.add_field(name=':black_joker: __Kidding__', value="""1. `#joke [userid] [times] [duration]` 
                                                           Move a specified user into random voice channels randomly and repeatly
                                                           2. `#leavemealone` Stop yourself from being bullied
                                                           3. `#save [userid]` Recuse your friend from cyber-bullying""", inline=False)
    
    embed.add_field(name=':man_office_worker: __Other__', value="""1. `#stick` Fortune sticks from Wong Tai Sin
                                                               2. `#gpa` Get prediction of your GPA (Maximum: 4.0)
                                                               3. `#help` Display a list of all commands aviliable
                                                               4. `#credit` Display information of the bot developer
                                                               5. `#hello` Return 'hello world'
                                                               6. `#ping` Return latency
                                                               7. `#log` Display the previous 20 in/out user
                                                               8. `#clear` Delete previous 30 messages sent by this bot / started with '#'
                                                               9. `#debug` Check parameters (for debugging)""", inline=False)
    
    embed.add_field(name=':new: __New Features (Experimental)__', value="""1. `#when` Return the start time of the bot
                                                                        2. `#dm [userid] [message]` Send message to any user privately""" )
    
    embed.add_field(name=':frame_with_picture: __GIF__', value="Automatically return GIF if the message matches the following keywords\n`" + '` `'.join(gif.keys()) +'`', inline=False)
    embed.set_footer(text="Last updated on 18 September 2021")
    await ctx.send(embed=embed)

@client.command(name='ping')
async def ping(ctx):
     await ctx.send(f'In {round(client.latency * 1000)}ms')

@client.command(name='stick')
async def stick(ctx):
    tag = "<@" + str(ctx.message.author.id) + ">"
    text = get_stick(tag)
    await ctx.send(text)

@client.command(name='credit')
async def credit(ctx):
    await ctx.send('Created By kenneth\nLast Update On 18/9/2021\nhttps://github.com/kenneth2001')

@client.command(name='clear')
async def clear(ctx):
    def is_bot(m):
        try:
            return m.author == client.user or m.content[0] == '#'
        except:
            return False

    deleted = await ctx.message.channel.purge(limit=30, check=is_bot)
    await ctx.send('Deleted {} message(s)'.format(len(deleted)), delete_after=10)

@client.command(name='joke')
async def joke(ctx, userid=None, n=10, sleep_time=0.5):
    await initialize(ctx.guild.id, ctx)
    global channel_var

    try:
        userid = int(userid)
        user = await ctx.guild.fetch_member(userid)
        info = channel_var[ctx.guild.id]['bully'].get(userid, -1)
        if info == -1:
            channel_var[ctx.guild.id]['bully'][userid] = True
        channel_var[ctx.guild.id]['bully'][userid] = True
        tag1 = "<@" + str(ctx.message.author.id) + ">"
        tag2 = "<@" + str(userid) + ">"
        await ctx.send(tag1 + " is pranking " + tag2)
        await ctx.send('To stop, type #leavemealone')
    except:
        tag = "<@" + str(ctx.message.author.id) + ">"
        await ctx.send('Please provide a valid user id!' + tag)
        return
    
    while(n > 0):
        if channel_var[ctx.guild.id]['bully'][userid] == False:
            return
        
        try:
            if user.voice is not None:
                await user.move_to(np.random.choice(ctx.guild.voice_channels))
                n -= 1
        except:
            pass
        
        await asyncio.sleep(sleep_time)
                                           
def generate_question():
    question = ""
    for i in range(6):
        question += str(np.random.randint(1, 21))
        question += np.random.choice(['*', '+', '-'])
    question += str(np.random.randint(1, 21))
    return question

@client.command(name='leavemealone')
async def leavemealone(ctx):
    await initialize(ctx.guild.id, ctx)
    global channel_var
    info = channel_var[ctx.guild.id]['bully'].get(ctx.message.author.id, -1)
    if info == -1:
        channel_var[ctx.guild.id]['bully'][ctx.message.author.id] = True
    
    def check(m):
        return m.author == ctx.message.author
    
    question = generate_question()
    await ctx.send('Question:  `'+question+'`\nType your answer:')
    answer = int(sympy.sympify(question))
    print('Answer:', answer)
    msg = await client.wait_for("message", check=check)
    tag = "<@" + str(ctx.message.author.id) + ">"
    if int(msg.content) == answer:
        channel_var[ctx.guild.id]['bully'][ctx.message.author.id] = False
        await ctx.send("Good Job" + tag)
    else:
        await ctx.send("on9" + tag)
        
@client.command(name='save')
async def save(ctx, id=None):
    if id is None:
        await ctx.send("You must specify an id")
        return
    
    await initialize(ctx.guild.id, ctx)
    global channel_var
    userid = int(id)
    
    def check(m):
        return m.author == ctx.message.author
    
    if channel_var[ctx.guild.id]['bully'].get(userid, -1) == -1:
        await ctx.send("This user is not under bully list")
    elif channel_var[ctx.guild.id]['bully'][userid] == False:
        await ctx.send("This user is not being bullied")
    else:
        question = generate_question()
        await ctx.send('Question:  `'+question+'`\nType your answer:')
        answer = int(sympy.sympify(question))
        print('Answer:', answer)
        msg = await client.wait_for("message", check=check)
        tag = "<@" + str(ctx.message.author.id) + ">"
        if int(msg.content) == answer:
            channel_var[ctx.guild.id]['bully'][userid] = False
            await ctx.send("Good Job" + tag)
        else:
            await ctx.send("Be careful" + tag)

# experimental   
@client.command(name='plot')
async def plot(ctx):
    def check(m):
        return m.author == ctx.message.author 
    
    await ctx.send("1. Please Enter The Type of The Plot")
    await ctx.send("a: scatter plot, b: line plot")
    msg = await client.wait_for("message", check=check)
    graph_type = msg.content
    
    await ctx.send("2. Please enter the x-coordinate for all points (seperated by comma)")
    msg = await client.wait_for("message", check=check)
    x = [int(i) for i in msg.content.split(',')]
    
    await ctx.send("3. Please enter the y-coordinate for all points (seperated by comma)")
    msg = await client.wait_for("message", check=check)
    y = [int(i) for i in msg.content.split(',')]
    
    await ctx.send("4. Please enter the title of the plot")
    msg = await client.wait_for("message", check=check)
    title = msg.content
    
    await ctx.send("5. Please enter the name of x-axis")
    msg = await client.wait_for("message", check=check)
    x_name = msg.content
    
    await ctx.send("6. Please enter the name of y-axis")
    msg = await client.wait_for("message", check=check)
    y_name = msg.content
    
    plt.plot(x, y, linestyle="-" if graph_type == 'b' else 'none', marker='.')
    plt.title(title)
    plt.xlabel(x_name)
    plt.ylabel(y_name)
    plt.savefig('plot.png')
    await ctx.send(file=discord.File('plot.png'))
    os.remove('plot.png')
    plt.clf()
   
# experimental
@client.command(name='when')
async def when(ctx):
    await ctx.send(start_time.strftime("**Bot started from %Y-%m-%d %I-%M %p**"))

# experimental
@client.command(name='dm')
async def dm(ctx, userid, *message):
    try:
        userid = int(userid)
        user = await client.fetch_user(userid)
        await user.send(' '.join(message))
        await ctx.send("**Message sent successfully**")
    except:
        await ctx.send("**Message is not sent**")
 
#keep_alive() # For setting up bot on replit.com
start_time = datetime.now(tz)
client.run(token)
