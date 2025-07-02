import discord
import logging
from discord.ext import tasks, commands
from discord import app_commands
from dotenv import load_dotenv
import requests
import os
import datetime
from person import Person

load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
channel_id = os.getenv('CHANNEL_ID')
db_domain = os.getenv('DB_DOMAIN')
db_token = os.getenv('DB_DOMAIN_TOKEN')

headers = {
        "apikey": db_token,
        "Authorization": f"Bearer {db_token}",
        "Content-Type": "application/json"
    }

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
test_time = datetime.date.today()

bot = commands.Bot(command_prefix="/", intents=intents)

def user_exists(name: str):
    response = requests.get(db_domain, headers=headers)
    people = []
    if response.status_code == 200:
        data = response.json()
        for entry in data:
            people.append(Person(entry['name'], datetime.date.fromisoformat(entry['birthday'])))
        for person in people:
            if person.name == name:
                return True
    return False

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}")
    notify_birthday.start()


@bot.tree.command(name="show_birthdays", description="Displays all registered birthdays")
async def show_birthdays(interaction: discord.Interaction):
    response = requests.get(db_domain, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        people = []
        for entry in data:
            people.append(Person(entry['name'], datetime.date.fromisoformat(entry['birthday'])))

        sorted_birthdays = sorted(people, key=lambda d: (d.birthday.month, d.birthday.day))

        result = ""
        for person in sorted_birthdays:
            result += "\n" + person.name + " : " + person.birthday.strftime('%B %d')

        await interaction.response.send_message("Here are all the registered birthdays:" + result)

    else:
        await interaction.response.send_message("Could not access database domain.")

@bot.tree.command(name="upload_birthday", description="Upload a birthday.")
@app_commands.describe(name="Global user name, not the display name.", date="Birth date of the person. Use YYYY-MM-DD format.")
async def upload_birthday(interaction: discord.Interaction, name: str, date: str):
    try:
        date = datetime.date.fromisoformat(date)
        if user_exists(name):
            await interaction.response.send_message("Please refrain from adding duplicate users.")
        
        response = requests.post(db_domain, headers=headers, json={'name': name, 'birthday': date})

        if response.status_code == 201:
            await interaction.response.send_message(f"{name} added to birthday list.")
        else:
            await interaction.response.send_message("Could not access database domain.")
    except:
        await interaction.response.send_message(f"Use the correct date format - YYYY-MM-DD.")


@tasks.loop(seconds=30)
async def notify_birthday():
    channel = bot.get_channel(int(channel_id))
    now = datetime.date.today()
    
    response = requests.get(db_domain, headers=headers)

    if response.status_code == 200:
        data = response.json()
        
        people = []
        for entry in data:
            people.append(Person(entry['name'].lower(), datetime.date.fromisoformat(entry['birthday'])))
    
    for person in people:
        user = discord.utils.find(lambda m: m.name == person.name, channel.guild.members)
        
        if (person.birthday.day == now.day and person.birthday.month == now.month):
            if user is None:
                await channel.send("Happy birthday, " + person.name + "!")
            else:
                await channel.send("Happy birthday " + user.mention + "!")


bot.run(discord_token, log_handler=handler, log_level=logging.DEBUG)


    