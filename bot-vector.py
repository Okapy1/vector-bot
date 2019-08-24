#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# https://discordpy.readthedocs.io/en/latest/api.html
# https://discordpy.readthedocs.io/en/latest/ext/commands/api.html
# https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

import discord
from discord.ext import commands
import random
import requests
import json
from lxml import html

token = open("discord.key", "r").read()  # Discord token is saved in a text file.

print('Discord version: {0}'.format(discord.__version__))
# bot = commands.Bot(command_prefix='')
bot = commands.Bot(command_prefix='$')
bot.remove_command('help')

## Commit message : add web scraping (GBA profil)

# ------- BOT FUNCTIONS --------------------------------------------

# Read random line from a text file
def random_line(fname):
    lines = open(fname, encoding='utf-8').read().splitlines()
    return random.choice(lines)

# Weather (use API)
def weather(city):
    # TODO : discord.errors.HTTPException: 400 BAD REQUEST (error code: 50006): Cannot send an empty message
    # city = "Paris,fr"
    owm_host = 'http://api.openweathermap.org/data/2.5/weather?q='
    owm_key = open("owm.key", "r").read()  # OpenWeatherMap API key is saved in a text file.
    owm_call = '{0}{1}&APPID={2}&units=metric&lang=fr'.format(owm_host, city, owm_key)
    response = requests.get(owm_call)
    weather = response.json()
    # print(json.dumps(weather, indent=2))
    meteo_name = weather['name']
    meteo_desc = weather['weather'][0]['description']
    meteo_temp = weather['main']['temp']
    meteo_temp_min = weather['main']['temp_min']
    meteo_temp_max = weather['main']['temp_max']
    # return(meteo_name, meteo_desc, meteo_temp, meteo_temp_min, meteo_temp_max)
    return(u'Météo {0} : {1}, {2}°C (min={3}°, max={4}°)'.format(meteo_name, meteo_desc, meteo_temp, meteo_temp_min, meteo_temp_max))

# Board Game Arena (scrape a web page)
def bga_player(id):
    bga_host = 'https://fr.boardgamearena.com/player?id='
    my_id = id
    my_url = '{0}{1}'.format(bga_host, my_id)
    r = requests.get(my_url)
    tree = html.fromstring(r.content)
    # Manage error
    bga_error = tree.xpath('//b[@id="bga_fatal_error_descr"]/text()')
    if not bga_error:     # if bga_error is empty
        # Scrape player information
        my_pseudo = tree.xpath('//span[@id="player_name"]/text()')
        my_pseudo = my_pseudo[0].strip()
        my_status = tree.xpath('//div[@id="player_status"]/text()')
        my_prestige = tree.xpath('//div[@id="pageheader_prestige"]/text()')
        my_prestige = my_prestige[0].strip()
        my_lastseen = tree.xpath('//div[@class="row-value"][@id="last_seen"]/text()')
        my_reputation = tree.xpath('//div[@class="progressbar_content"]//span[@class="progressbar_valuename"]/text()')
        my_reputation  = my_reputation[0].strip()
        my_gamelist = tree.xpath('//div[@class="palmares_game"]//a[@class="gamename game_name"]/text()')
        my_games = ', '.join(my_gamelist)
        # Scrape player status
        my_status = "Déconnecté"
        my_lastseen = my_lastseen[0].strip()
        if int(my_lastseen) < 2:    # in minutes
            my_status = "En ligne"
        # Return informations
        ## TODO : afficher dans une box (discord.Embed)
        ## TODO cf https://stackoverflow.com/questions/354883/how-do-i-return-multiple-values-from-a-function
        return(u'{0} ({1}) :\n \
            Prestige : {2}, Réputation : {3} \n \
            Jeux : {4} \n \
            Stats : {5}\n \
            '.format(my_pseudo, my_status, my_prestige, my_reputation, my_games, my_url))
    else:
        # service error, player unknow...
        return(u'Erreur : {0}'.format(bga_error[0].strip()))



# ------- BOT EVENT ----------------------------------------------
@bot.event
async def on_ready():
    print('Bot: {0} (id={1}) is ready !'.format(bot.user.name, bot.user.id))

@bot.event
async def on_message(message):
    # Debug
    # TODO : seulement si auteur est autorisé
    if message.content.startswith('$debug'):
        await message.channel.send('{0}'.format(message))

    # If keyword is found in sentence, send a message
    # TODO : pas dans les liens (images, documents)
    if "ping" in message.content:
        await message.channel.send("pong")

    # Repeat sentence
    if message.content.startswith('$echo'):
        echo_echo = str(message.content)
        echo_echo = echo_echo[5:]       # Remove string "$echo" to avoid infinite boucle
        await message.channel.send('{0}'.format(echo_echo))

    # Send message if user respond hello
    if message.content.startswith('$greet'):
        channel = message.channel
        await message.channel.send('Dis hello !')
        def check(m):
            return m.content == 'hello' and m.channel == channel
        msg = await bot.wait_for('message', check=check)
        await message.channel.send('Hello {.author} !'.format(msg))

    # Smiley
    if message.content.startswith('$hello'):
        await message.channel.send(":wave: :smiley: Salut !")

    # Image
    if message.content.startswith('$danse'):
        await message.channel.send("https://i.giphy.com/media/1pA2SJ1g6amgbDSFdZ/giphy.webp")

    # Citation box (from text file)
    if message.content.startswith('$quote'):
        # random citation from file
        quote = random_line('quote.txt')
        quote_txt = quote.split(';')[1]
        quote_author = quote.split(';')[0]
        embed = discord.Embed(title="Citation", description=quote_txt, color=0xeee657)
        embed.add_field(name="Auteur", value=quote_author)
        await message.channel.send(embed=embed)

    # Info box
    if message.content.startswith('$info'):
        embed = discord.Embed(title="Vector", description="De son vrai nom Vector Hugo, ce chatbot sympathique, né le 28 juillet 2019, est là pour vous accompagner.", color=0xeee657)
        embed.add_field(name="Citation", value='"N\'imitez rien ni personne. Un robot qui copie un robot devient un singe." \n (Vector Hugo)')    
        embed.add_field(name="Aide", value="Utilisez la commande : $help", inline=False)
        embed.add_field(name="Dresseur de bot", value="Okapy1")
        # Shows the number of servers the bot is member of.
        embed.add_field(name="Serveur", value=f"{len(bot.guilds)}")
        # give users a link to invite this bot to their server
        embed.add_field(name="Invitation", value="[Inviter ce bot Discord](<https://discordapp.com/api/oauth2/authorize?client_id=604724086618193931&permissions=67584&scope=bot>)")        
        await message.channel.send(embed=embed)

    # Help commands box
    if message.content.startswith('$help'):
        embed = discord.Embed(title="Liste des commandes de Vector", description="\r\n", color=0xffa500)
        # embed.add_field(name="$add X Y", value="Additionne **X** et **Y**", inline=False)
        embed.add_field(name="$hello", value="Message de bienvenue", inline=False)
        embed.add_field(name="$greet", value="Vector vous salue", inline=False)
        embed.add_field(name="$danse", value="Une gif animée pour mettre l'ambiance", inline=False)
        embed.add_field(name="$quote", value="Une citation", inline=False)
        embed.add_field(name="$weather", value="Affiche la météo du jour", inline=False)
        embed.add_field(name="$echo", value="Vector répète ton message", inline=False)
        embed.add_field(name="$info", value="Plus d'information à propos de Vector", inline=False)
        embed.add_field(name="$help", value="Affiche ce message d'aide", inline=False)
        await message.channel.send(embed=embed)

    # Weather
    # TODO : vérifier erreurs
    # TODO : return -vs- print
    # TODO : utiliser les icones Discord (:partly_sunny: , :cloud_rain: , ...)
    if message.content.startswith('$weather'):
        weather_input = str(message.content)    # message_content is a dict
        city = weather_input[9:]                # we need a string without command '$weather'
        if len(city) == 0:
            await message.channel.send("[Aide] Entrez le nom de la ville après la commande $weather")
        else:
            try:
                # return Weather info
                await message.channel.send(weather(city))
            except KeyError:
                # await message.channel.send(city)
                await message.channel.send("[erreur] ville inconnue: {0}".format(city))
    # return(u'Météo {0} : {1}, {2}°C (min={3}°, max={4}°)'.format(meteo_name, meteo_desc, meteo_temp, meteo_temp_min, meteo_temp_max))

    # Game Board Arena
    if message.content.startswith('$gba'):
        gba_input = str(message.content)    # message_content is a dict
        gba_player_id = gba_input[5:]              # we need a string without command '$gba'
        if len(gba_player_id) == 0:
            await message.channel.send("[Aide] Entrez l'id du joueur après la commande $gba")
            await message.channel.send("[Aide] ex: Lord Nogard=85198715, bob2433=7194185")
        else:
            try:
                # return GBA player info
                await message.channel.send(bga_player(gba_player_id))
            except KeyError:
                await message.channel.send("[erreur] réessayer plus tard")


# ------- BOT COMMAND --------------------------------------------
""" @bot.command()
async def echo(ctx, *args):                        # async def echo2(ctx, *, arg):
    await ctx.send('{}'.format(' '.join(args)))    # await ctx.send(arg) """

""" @bot.command()
async def add(ctx, a: int, b: int):
    await ctx.send(a+b) """


# ------- BOT RUN ------------------------------------------------
bot.run(token)