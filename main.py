import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = str(os.getenv("DISCORD_TOKEN"))

client = commands.Bot(command_prefix='!', intents=discord.Intents.all())


@client.event
async def on_ready():
    print("Success: Bot is connected to Discord")


@client.command()
async def ping(ctx):
    await ctx.send("Pong")


@client.command()
async def magic_eightball(ctx, *, question):
    pass

@client.command()
async def bruh(ctx):
    await ctx.send("bruv")

client.run(TOKEN)
