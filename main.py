import discord
import logging
from discord.ext import tasks, commands
from discord import app_commands
from dotenv import load_dotenv
import os
import datetime

people = []

load_dotenv()
token = os.getenv('TOKEN')
channel_id = os.getenv('CHANNEL_ID')

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
    test_time = datetime.date(2025, 7, 16)
    check_date_change.start()

@bot.tree.command(name="show_people", description="Displays people in system")
async def show_people(interaction: discord.Interaction):
    result = "\n".join(people) if people else "No people added yet."
    await interaction.response.send_message("Here are all the people:\n" + result)

@bot.tree.command(name="upload_person", description="Upload a person name")
@app_commands.describe(name="Name of the person")
async def upload_person(interaction: discord.Interaction, name: str):
    people.append(name)
    await interaction.response.send_message(f"Person '{name}' added!")

@tasks.loop(seconds=30)
async def check_date_change():
    now = datetime.date.today()
    print(now)
    print(test_time)
    if test_time == now:
        print("Yippee!")
        print(channel_id)
        channel = bot.get_channel(int(channel_id))
        await channel.send("Happy birthday")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)
