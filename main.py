import discord
import os
from discord.ext import commands
import json
import feedparser
import time
import datetime
# from keep_alive import keep_alive

client = discord.Client()

masterlist = []
time_offset = 0
time_stored = time.time() + time_offset  # - 86400

time_period_start = time.time()
time_period_end = time.time() + 1000
master_channel_id = 800053776039804981
master_channel = client.get_channel(master_channel_id)
ready = True


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    global master_channel
    master_channel = client.get_channel(master_channel_id)
    with open('database.txt', 'r') as filehandle:
        global masterlist
        masterlist = json.load(filehandle)


@client.event
async def on_message(message):
    if message.author == client.user and message.channel.id != master_channel_id:
        return

    if message.content.startswith('!hello'):
        await
        message.channel.send('hello!')

    if message.content.startswith('party') and message.channel.id == master_channel_id:
        await
        master_channel.send('has started')
        await
        master_channel.send('Start run!')
        # global ready
        # ready = False
        # while(ready):
        #   time_now = time.localtime(time.time() + time_offset)
        #   time.sleep(1)
        #   if(time_now.tm_min % 5 == 0 and time_now.tm_sec == 0):
        #     print('Start run!')
        #     ready = False
        #     await master_channel.send('Start run!')

    if message.content.startswith('Start run!') and message.channel.id == master_channel_id:
        await
        master_channel.send('Starting run at {}'.format(time.asctime(time.localtime(time.time() + time_offset))))

        global time_period_end
        time_period_end = time.time() + time_offset
        for line in masterlist:
            diaries = get_diaries(line[0])
            for diary in range(len(diaries)):
                for channel in range(len(line) - 1):
                    discord_channel = client.get_channel(line[channel + 1])
                    await
                    discord_channel.send(embed=diaries[diary])

        global time_period_start
        time_period_start = time_period_end

        await
        master_channel.send(
            'Ending run at {} / {}'.format(time.asctime(time.localtime(time.time() + time_offset)), time.time()))
        await
        master_channel.send('party')

    if message.content.startswith('&followlist'):
        id = message.channel.id

        emb_descr = ''
        for line in masterlist:
            if id in line:
                emb_descr = emb_descr + '[' + line[0] + '](https://letterboxd.com/' + line[0] + '), '

        emb_descr = emb_descr[:-2]
        embed = discord.Embed(title="List of Letterboxd members being followed in the channel", description=emb_descr)
        await
        message.channel.send(embed=embed)
        return

    if message.content.startswith('&follow'):
        command = message.content.split()
        command[1] = command[1].lower()

        if (len(command) < 2):
            await
            message.channel.send('You are missing a parameter')
            return

        feed_url = 'https://letterboxd.com/' + command[1] + '/rss/'
        NewsFeed = feedparser.parse(feed_url)

        if (NewsFeed.status != 200):
            await
            message.channel.send('This is an invalid username')
            return

        nameIndex = masterlist_find(command[1])
        if (nameIndex == -1):
            list1 = [command[1], message.channel.id]
            masterlist.append(list1)
        else:
            if message.channel.id in masterlist[nameIndex]:
                await
                message.channel.send('{} is already being followed in this channel!'.format(command[1]))
                return
            else:
                masterlist[nameIndex].append(message.channel.id)
                await
                message.channel.send('{} is now being followed!'.format(command[1]))

        with open('database.txt', 'w') as filehandle:
            json.dump(masterlist, filehandle)

    if message.content.startswith('&unfollow'):
        command = message.content.split()

        if (len(command) < 2):
            await
            message.channel.send('You are missing a parameter')
            return

        nameIndex = masterlist_find(command[1])
        if (nameIndex == -1):
            await
            message.channel.send("This user wasn't even being followed lol")
        else:
            if message.channel.id in masterlist[nameIndex]:
                masterlist[nameIndex].remove(message.channel.id)
                await
                message.channel.send("{} has been unfollowed!".format(command[1]))
            else:
                await
                message.channel.send("This user wasn't even being followed lol")

        nameIndex = masterlist_find(command[1])
        with open('database.txt', 'w') as filehandle:
            json.dump(masterlist, filehandle)

    if message.content.startswith('&help'):
        await
        message.channel.send()

    # this is an incorrect command without api
    # if message.content.startswith('!diary'):

    #   await message.channel.send(embed=diary('king', 0))

    # this is a fake command without api
    # if message.content.startswith('!f '):
    #   embTitle = "Title"
    #   embUrl = "https://letterboxd.com/film/parasite-2019/"
    #   embThumbnail = "https://a.ltrbxd.com/resized/film-poster/4/2/6/4/0/6/426406-parasite-0-500-0-750-crop.jpg?k=3f39b58008" # image

    #   author = "author"
    #   country = "country"
    #   length = 120
    #   genre = "Drama"
    #   rating = 3.5
    #   numRatings = 100
    #   numViews = 500

    #   embZero = 'optional'
    #   embFirst = '**' + author + '** — ' + country
    #   embSecond = '**' + str(length) + ' mins** — ' + genre
    #   embThird = '**' + str(rating) + ' stars** (' + str(numRatings) + ' ratings, ' + str(numViews) + ' views)'
    #   embDescr = embZero + '\n' + embFirst + '\n' + embSecond + '\n' + embThird

    #   embedVar = discord.Embed(title=embTitle, url=embUrl, description=embDescr, color=0xf99f9f)
    #   embedVar.set_thumbnail(url=embThumbnail)
    #   await message.channel.send(embed=embedVar)


def get_diaries(name):
    diaries = []

    feed_url = 'https://letterboxd.com/' + name + '/rss/'
    NewsFeed = feedparser.parse(feed_url)

    if (NewsFeed.status != 200):
        print("{} doesn't work".format(name))
        return diaries

    for entry in NewsFeed.entries:
        if ((earlier_time(entry.published_parsed, time.localtime(time_period_start)) == 0) or (
                earlier_time(entry.published_parsed, time.localtime(time_period_end)) == 1)):
            break
        else:
            diaries.append(diary(name, entry))

    return diaries


def earlier_time(entry, stored):
    entry_time = entry
    datetime_entry = datetime.datetime(year=entry_time.tm_year, month=entry_time.tm_mon, day=entry_time.tm_mday,
                                       hour=entry_time.tm_hour, minute=entry_time.tm_min, second=entry_time.tm_sec)

    datetime_stored = datetime.datetime(year=stored.tm_year, month=stored.tm_mon, day=stored.tm_mday,
                                        hour=stored.tm_hour, minute=stored.tm_min, second=stored.tm_sec)

    if (datetime_entry < datetime_stored):
        return 0
    else:
        return 1


def diary(name, entry):
    feed_url = 'https://letterboxd.com/' + name + '/rss/'
    NewsFeed = feedparser.parse(feed_url)

    if (NewsFeed.status != 200):
        master_channel.send("{} doesn't work".format(name))
        print("{} doesn't work".format(name))

    description = entry.description.split("<p>")
    title = entry.title.rsplit(', ', 1)
    title_latter_half = title[1].split(' - ', -1)

    emb_author = name
    emb_author_url = 'https://letterboxd.com/' + name + '/films/diary'

    emb_title = title[0] + " (" + title[1].split(' - ', -1)[0] + ")"
    emb_url = entry.link
    emb_thumbnail = description[1].split('"')[1]

    date = entry.letterboxd_watcheddate

    rating = ''
    if (len(title_latter_half) > 1):
        rating = ' ' + title[1].split(' - ', -1)[1] + ' '

    rewatch = ''
    if (entry.letterboxd_rewatch == 'Yes'):
        rewatch = '↺'

    full_description = ''
    for x in range(len(description) - 2):
        full_description = full_description + description[x + 2] + '\n'

    full_description = clean(full_description)

    if (len(full_description) > 400):
        full_description = full_description[0:400] + '...'

    emb_first = '**' + date + '**' + rating + rewatch  # haven't added like option
    emb_second = '```' + full_description + '```'
    emb_descr = emb_first + '\n' + emb_second

    embed_var = discord.Embed(title=emb_title, url=emb_url, description=emb_descr, color=0xcecad3)
    embed_var.set_author(name="Recent diary activity from " + emb_author, url=emb_author_url)
    embed_var.set_thumbnail(url=emb_thumbnail)
    return embed_var


def masterlist_find(name):
    for line in range(len(masterlist)):
        if (masterlist[line][0] == name):
            return line
    return -1


def clean(description):
    stylistic_choices = ["</p>", "<blockquote>", "</blockquote>", "<b>", "</b>", "<br />", "<i>", "</i>"]

    for i in stylistic_choices:
        description = description.replace(i, "")
    return description


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await
        ctx.send('This command requires a parameter.')
    elif isinstance(error, commands.BotMissingPermissions):
        await
        ctx.send('This command requires the {} permission.'.format(
            ', '.join(err for err in error.missing_perms)))
    elif isinstance(error, (commands.CommandNotFound, commands.CheckFailure)):
        return
    elif isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.HTTPException):
            return
    else:
        await
        ctx.send('Sorry, the command crashed. :/')


# keep_alive()
client.run(os.getenv('TOKEN'))