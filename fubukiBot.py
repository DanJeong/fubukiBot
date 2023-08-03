#fubuki bot says hello :D
import os
import random
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import mangaSearch

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
    search_results = mangaSearch.m_search(" ".join(args))
    
    manga_list = []
    list_line = []
    for num, nameLink in search_results.items():
        list_line.append(f'{num}. {nameLink[0]}')
        if num % 10 == 0:
            manga_list.append(list_line)
            list_line = []
    if list_line:
        manga_list.append(list_line)#appends any remaining lines left
    print(f'length of manga list: {len(manga_list)}')
    """ for line in manga_list:
        print("\n".join(line)) """
    pages = len(manga_list)
    if pages > 0:
        curr_page = 1
        msg_string = "\n".join(manga_list[curr_page-1])
        message = await ctx.send(f"Page {curr_page}/{pages}:\n{msg_string}")
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("✅")
        await ctx.send('When you decide which manga to add, react with ✅ and enter the corresponding manga number')
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️", "✅"]
        def check_msg(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.content.isnumeric()
        while True:
            try:
                reaction, user = await bot.wait_for("reaction_add", timeout=60, check=check)
                # waiting for a reaction to be added - times out after 60 seconds

                if str(reaction.emoji) == "▶️" and curr_page != pages:
                    curr_page += 1
                    msg_string = "\n".join(manga_list[curr_page-1])
                    await message.edit(content=f"Page {curr_page}/{pages}:\n{msg_string}")
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "◀️" and curr_page > 1:
                    curr_page -= 1
                    msg_string = "\n".join(manga_list[curr_page-1])
                    await message.edit(content=f"Page {curr_page}/{pages}:\n{msg_string}")
                    await message.remove_reaction(reaction, user)

                elif str(reaction.emoji) == "✅":
                    print("check emoji")
                    msg = await bot.wait_for("message", timeout=60, check=check_msg)
                    mangaNum = int(msg.content)
                    print(msg.content)
                    print('got msg')
                    print(f'manga you picked is #{mangaNum}: {search_results[mangaNum][0]}')
                    await ctx.send(f'You chose manga #{msg.content}: {search_results[mangaNum][0]}')
                
                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or
                    # backwards on the first page
            except asyncio.TimeoutError:
                await message.delete()
                break
                # ending the loop if user doesn't react after 60 seconds
    else:
        await ctx.send(f'No search results found for {" ".join(args)}')

@bot.command(name='manga_remove', help='choose a manga to remove from your update list')
async def remove_manga(ctx):
    #show user their manga list and assign each one a number
    #user gives number, and that manga is removed from their list (maybe have Y/N confirmation)
    print()

#client.run(TOKEN) #runs the client, with given token (in this case, fubuki bot)
bot.run(TOKEN)