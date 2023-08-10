import os
import re
import random
import asyncio
import sqlite3
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
from collections import defaultdict
from utils import mangaUpdates
from utils import mangaSearch

connection = sqlite3.connect("manga_list.db")
c = connection.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS manga_list (
            user_id string NOT NULL,
            manga_name string NOT NULL,
            manga_link string NOT NULL,
            PRIMARY KEY(user_id, manga_name)
            )""")
c.execute("""CREATE TABLE IF NOT EXISTS latest_chapters (
            manga_name string NOT NULL PRIMARY KEY,
            manga_link string NOT NULL,
            latest_chapter string NOT NULL
            )""")
manga_list_insert = """INSERT INTO manga_list
                            (user_id, manga_name, manga_link)
                            VALUES (?, ?, ?);"""
latest_chapters_insert = """INSERT INTO latest_chapters
                            (manga_name, manga_link, latest_chapter)
                            VALUES (?, ?, ?);"""

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', help_command=help_command, intents=intents)

#Non-Bot Functions
def get_user_manga(user_id):
    c.execute("SELECT manga_name FROM manga_list WHERE user_id=? ORDER BY manga_name ASC", (user_id,))
    search_results = c.fetchall()
    #formats list into pages of 10
    manga_list = []
    list_line = []
    for num, manga in enumerate(search_results, 1):
        list_line.append(f'{num}. {manga[0]}')
        if num % 10 == 0:
            manga_list.append(list_line)
            list_line = []
    if list_line:
        manga_list.append(list_line)#appends any remaining lines left
    return manga_list

#help command is not needed, already built into python bots, just need to edit that
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    check_for_updates.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send('You do not have permission to use this command (ADMIN)')

@bot.command(name='quote', help='Gives an insiprational quote from a random VTuber')
async def send_vQuote(ctx):
    v_quotes = ['\"watah in the fire why?\" - Korone',
               '\'no wife, only friend\' = Fubuki',
               '\"AH↓HA↑HA↑HA↑HA↑\" - Pekora']
    print("quote command")
    quote = random.choice(v_quotes)
    await ctx.send(quote)

@bot.command(name='d6', help='simulates rolling a 6-sided die')
async def roll(ctx, number_of_dice: int = commands.parameter(default = 1, description='number of times to roll the die')):
    dice = [
        str(random.choice(range(1, 7)))
        for _ in range(number_of_dice)
    ]
    await ctx.send(', '.join(dice))

@bot.command(name='create_channel', help='creates a channel with the given name (ADMIN ONLY)')
@commands.has_role('admin')
async def create_channel(ctx, channel_name = commands.parameter(default = 'default_channel_name', description='name of new channel')):
    guild = ctx.guild
    existing_channel = discord.utils.get(guild.channels, name=channel_name)
    if not existing_channel:
        print(f'Creating a new chanel: {channel_name}')
        await guild.create_text_channel(channel_name)

@bot.command(name='manga_add', help='search for a manga to add to your update list')
async def search_for_manga(ctx, *args):
    search_results = {}
    searched = False
    if len(args) < 1:
        await ctx.send(f'Please give a manga to search for after the command')
    else:
        await ctx.send(f'{ctx.message.author.mention} i will search for {" ".join(args)} momentarily, please sit tight 😇')
        search_results = mangaSearch.m_search(" ".join(args))
        searched = True
    
    manga_list = []
    list_line = []
    for num, name_link in search_results.items():
        list_line.append(f'{num}. {name_link[0]}')
        if num % 10 == 0:
            manga_list.append(list_line)
            list_line = []
    if list_line:
        manga_list.append(list_line)#appends any remaining lines left
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
                    msg = await bot.wait_for("message", timeout=60, check=check_msg)
                    manga_num = int(msg.content)
                    if manga_num in search_results:
                        #sqlite stuff here, adding manga into database
                        user_id = ctx.author.id
                        manga_name = search_results[manga_num][0]
                        manga_link = search_results[manga_num][1]
                        #see if row already exists in table
                        c.execute("SELECT count(*) FROM manga_list WHERE (user_id=? AND manga_name=?)", (user_id, manga_name,))
                        rows_before = c.fetchone()[0]
                        if rows_before == 0:
                            insert_values = (user_id, manga_name, manga_link)
                            c.execute(manga_list_insert, insert_values)
                            connection.commit()
                            #updating latest_chapters table
                            c.execute("SELECT count(*) FROM latest_chapters WHERE manga_name=?", (manga_name,))
                            rows_before = c.fetchone()[0]
                            if rows_before == 0:#if not already in latest_chapters
                                latest_link = mangaUpdates.get_latest_chapter(manga_link)
                                insert_values = (manga_name, manga_link, latest_link)
                                c.execute(latest_chapters_insert, insert_values)
                                connection.commit()
                            await ctx.send(f'Manga #{msg.content}: {search_results[manga_num][0]}, was added to your list')
                            break
                        else:
                            await ctx.send(f'Manga #{msg.content}: {search_results[manga_num][0]}, was already in your list')
                            await message.remove_reaction(reaction, user)
                            continue
                    else:
                        await ctx.send(f'{manga_num} is not on the list, please enter a valid number')
                        await message.remove_reaction(reaction, user)
                        continue
                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or backwards on the first page
            except asyncio.TimeoutError:
                break # ending the loop if user doesn't react after 60 seconds
    elif searched == True:
        await ctx.send(f'No search results found for {" ".join(args)}')

@bot.command(name='manga_remove', help='choose a manga to remove from your update list')
async def remove_manga(ctx):
    user_id = ctx.author.id
    manga_list = get_user_manga(user_id)
    pages = len(manga_list)
    if pages > 0:
        curr_page = 1
        msg_string = "\n".join(manga_list[curr_page-1])
        message = await ctx.send(f"Page {curr_page}/{pages}:\n{msg_string}")
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("✅")
        await ctx.send('When you decide which manga to remove, react with ✅ and enter the corresponding manga number')
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
                    msg = await bot.wait_for("message", timeout=60, check=check_msg)
                    manga_num = int(msg.content)
                    last_num = (len(manga_list) - 1)*10 + len(manga_list[-1])
                    if manga_num > 0 and manga_num <= last_num:
                        dirty_manga_name = manga_list[(manga_num - 1) // 10][(manga_num - 1) % 10]
                        manga_name = dirty_manga_name.lstrip('0123456789. ')
                        c.execute("DELETE FROM manga_list WHERE (user_id=? AND manga_name=?)", (user_id, manga_name,))
                        connection.commit()
                        #remove manga from latest_chapters if not in manga_list anymore
                        c.execute("SELECT count(*) FROM manga_list WHERE manga_name=?", (manga_name,))
                        rows_before = c.fetchone()[0]
                        if rows_before == 0:
                            c.execute("DELETE FROM latest_chapters WHERE manga_name=?", (manga_name,))
                            connection.commit()
                        await ctx.send(f'{manga_name} was successfully removed from your list')
                        break
                    else:
                        await ctx.send(f'{manga_num} is not on the list, please enter a valid number')
                        await message.remove_reaction(reaction, user)
                        continue
                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or backwards on the first page
            except asyncio.TimeoutError:
                break # ending the loop if user doesn't react after 60 seconds
    else:
        await ctx.send(f'Your manga list is currently empty, use *!manga_add* to add to your list')

@bot.command(name='manga_view', help='view your manga update list')
async def view_manga(ctx):
    user_id = ctx.author.id
    manga_list = get_user_manga(user_id)
    pages = len(manga_list)
    if pages > 0:
        curr_page = 1
        msg_string = "\n".join(manga_list[curr_page-1])
        message = await ctx.send(f"Page {curr_page}/{pages}:\n{msg_string}")
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
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

                else:
                    await message.remove_reaction(reaction, user)
                    # removes reactions if the user tries to go forward on the last page or backwards on the first page
            except asyncio.TimeoutError:
                break # ending the loop if user doesn't react after 60 seconds
    else:
        await ctx.send(f'Your manga update list is currently empty, try !manga_add *manga_name* to add a manga to your list!')

@tasks.loop(hours=1)
async def check_for_updates():
    users_to_message = defaultdict(list)
    c.execute("SELECT manga_link, user_id FROM manga_list")
    user_list = c.fetchall()
    for manga_link, user_id in user_list:
        users_to_message[manga_link].append(user_id)

    manga_checker = defaultdict(list)
    c.execute("SELECT * FROM latest_chapters")
    lc_rows = c.fetchall()
    for manga_name, manga_link, latest_chapter in lc_rows:
        manga_checker[manga_link] = [manga_name, latest_chapter]
    updated_manga = []
    for manga_link, pair in manga_checker.items():
        old_chapter = pair[1]
        new_chapter = mangaUpdates.get_latest_chapter(manga_link)
        if old_chapter != new_chapter:
            manga_checker[manga_link][1] = new_chapter
            updated_manga.append(manga_link)
            c.execute("UPDATE latest_chapters SET latest_chapter=? WHERE manga_name=?", (new_chapter, pair[0],))
            connection.commit()

    for manga in updated_manga:
        manga_name = manga_checker[manga][0]
        new_link = manga_checker[manga][1]
        for user_id in users_to_message[manga]:
            user = bot.get_user(int(user_id))
            await user.create_dm()
            await user.dm_channel.send(f'There is a new chapter available for {manga_name}! Read here: {new_link}')

bot.run(TOKEN)