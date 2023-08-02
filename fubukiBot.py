#fubuki bot says hello :D
import os
import random

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

intents = discord.Intents.all()
#intents.members = True
client = discord.Client(intents=intents) #a client is an object that represents a connection to Discord

bot = commands.Bot(command_prefix='!', intents=intents)
#---------------------------------------------------------------------------------#
@client.event
async def on_ready(): #event handler
    guild = discord.utils.get(client.guilds, name=GUILD)
    
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name} (id: {guild.id})'  
          )
    
    members = '\n - '.join([member.name for member in guild.members])
    print(f'Guild Members:\n - {members}')

@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hello {member.name}, welcome to fubuki\'s test server. More features will be implemented very soon, so stay tuned!'
    )

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content == 'raise-exception':
        raise discord.DiscordException
#---------------------------------------------------------------------------------#
#help command is not needed, already built into python bots, just need to edit that
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have permission to use this command (ADMIN)')

@bot.command(name='quote', help='Gives an insiprational quote from a random VTuber')
async def send_vQuote(ctx):
    vQuotes = ['\"watah in the fire why?\" - Korone',
               '\'no wife, only friend\' = Fubuki',
               '\"AH↓HA↑HA↑HA↑HA↑\" - Pekora']
    print("quote command")
    quote = random.choice(vQuotes)
    await ctx.send(quote)

@bot.command(name='d6', help='simulates rolling a 6-sided die')
async def roll(ctx, number_of_dice: int = 1):
    dice = [
        str(random.choice(range(1, 7)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create_channel', help='creates a channel with the given name (ADMIN ONLY)')
@commands.has_role('admin')
async def create_channel(ctx, channel_name='default_channel_name'):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new chanel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.command(name='manga_add', help='search for a manga to add to your update list')
async def search_for_manga(ctx, *args):
    currUser = ctx.author.name
    currUserID = ctx.author.id
    print(f'person who used this command is: {currUser}')
    print(f'ok, currently searching for: {" ".join(args)}')
    await ctx.send(f'{ctx.message.author.mention} i will search for {" ".join(args)} momentarily, please sit tight :D')

@bot.command(name='manga_remove', help='choose a manga to remove from your update list')
async def remove_manga(ctx):
    #show user their manga list and assign each one a number
    #user gives number, and that manga is removed from their list (maybe have Y/N confirmation)
    print()

#client.run(TOKEN) #runs the client, with given token (in this case, fubuki bot)
bot.run(TOKEN)