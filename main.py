import discord
import logging
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import os

people = []

load_dotenv()
token = os.getenv('TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot is ready. Logged in as {bot.user}")

@bot.command()
async def show_people(ctx):
    result = "\n".join(people) if people else "No people added yet."
    await ctx.send("Here are all the people:\n" + result)

@bot.tree.command(name="upload_person", description="Upload a person name")
@app_commands.describe(name="Name of the person")
async def upload_person(interaction: discord.Interaction, name: str):
    people.append(name)
    await interaction.response.send_message(f"Person '{name}' added!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
