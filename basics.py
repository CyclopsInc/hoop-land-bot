import discord
import json
import os
import fuzzywuzzy
import unicodedata
import csv
from discord.ext import commands
from flask import Flask
from dotenv import load_dotenv

load_dotenv()
my_secret = os.environ['TOKEN']

app = Flask('')

@app.route('/')
def main():
    return 'The Hoops League Stat Bot is awake and at your service!'

def run():
    app.run(host='0.0.0.0', port=8000)

intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')
