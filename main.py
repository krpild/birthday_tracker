import discord
import logging
from discord.ext import tasks, commands
from discord import app_commands
from dotenv import load_dotenv
import json
import requests
import os
import datetime
from person import Person

people = []

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
channel_id = os.getenv('CHANNEL_ID')
db_domain = os.getenv('DB_DOMAIN')
db_token = os.getenv('DB_DOMAIN_TOKEN')


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
test_time = datetime.date.today()

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}")
    check_date_change.start()

@bot.tree.command(name="show_people", description="Displays people in system")
async def show_people(interaction: discord.Interaction):
    url = db_domain
    headers = {
        "apikey": db_token,
        "Authorization": f"Bearer {db_token}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    people = []
    for entry in data:
        people.append(Person(entry['name'],entry['birthday'][5:]))
    result = ""
    for person in people:
        result += "\n" + person.name + " : " + person.birthday
    await interaction.response.send_message("Here are all the people:\n" + result)

@bot.tree.command(name="upload_birthday", description="Upload a birthday")
@app_commands.describe(name="Global user name, not the display name.", date="Birth date of the person. Use YYYY-MM-DD format.")
async def upload_birthday(interaction: discord.Interaction, name: str, date: str):
    people.append(name)
    await interaction.response.send_message(f"Person '{name}' added!")

@tasks.loop(minutes=30)
async def check_date_change():
    channel = bot.get_channel(int(channel_id))
    now = datetime.date.today()
    for person in people:
        if person[1] == now:
            await channel.send("Happy birthday " + person[0])


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)
