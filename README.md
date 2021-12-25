# discord-bot
![icon1x](https://user-images.githubusercontent.com/24566737/132656284-f0ff6571-631c-4cef-bed7-f575233cbf5f.png)

## Features
1. Wong Tai Sin Fortune Sticks
2. GPA prediction
3. Music playing (including Queue!!!)
4. Move your friends to different voice channels randomly and repeatly
5. Send GIF according to your message
6. Simple graph plotting

## Command

**Music**
1. `#play [url]` Play music, tested platform: Youtube, Soundcloud
2. `#pause` Pause music
3. `#resume` Resume music
4. `#skip` Play next song
5. `#queue` Display the queue
6. `#stop` Kick the bot from voice channel
    
**Graph**
1. `#plot` Create simple scatter/line plot
    
**Kidding**
1. `#joke [userid] [times] [duration]` Move a specified user into random voice channels randomly and repeatly
2. `#leavemealone` Stop yourself from being bullied
3. `#save [userid]` Recuse your friend from cyber-bullying

**Other**
1. `#stick` Fortune sticks from Wong Tai Sin
2. `#gpa` Get prediction of your GPA (Maximum: 4.0)
3. `#help` Display a list of all commands aviliable
4. `#credit` Display information of the bot developer
5. `#hello` Return 'hello world'
6. `#ping` Return latency
7. `#log` Display the previous 20 in/out user
8. `#debug` Check parameters (for debugging)

**New features**
1. `#when` Return the start time of the bot
2. `#dm [userid] [message]` Send message to any user privately

## Dependencies
- yt_dlp==2021.9.2
- pytz==2021.1
- discord.py==1.7.3
- numpy==1.20.1
- requests==2.25.1
- matplotlib==3.3.4
- sympy==1.8
- beautifulsoup4==4.10.0
- discord==1.7.3

## Usage
- Complusory
  
  1. Generate TOKEN in https://discord.com/developers/applications
  2. Copy the TOKEN and paste inside `config.txt`
  3. Change the timezone to your favourite (For all available timezone, please refer to [https://github.com/newvem/pytz/blob/master/pytz/\_\_init\_\_.py](https://github.com/newvem/pytz/blob/master/pytz/__init__.py')

- Optional
   1. To include personalised GIFs, you may specify the keywords and link in `gif.json`
   2. To include personalised Welcome message for specified user, you may specify the userid and message in `user.json`

- Setting up bot in https://replit.com/
  1. Upload all the files
  2. Change mode from 0 to 1 inside `config.txt`
  3. To keep bot alive, you may use https://uptimerobot.com/

## Demo

- Add Virus to your channel!!! [CLICK HERE!!!](https://discord.com/oauth2/authorize?client_id=885452084269424660&permissions=8&scope=bot)

## To-dos
1. Support playlist from youtube
