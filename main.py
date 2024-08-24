import os

import discord
from discord.ext import commands
from dotenv import load_dotenv


def is_valid_link(link):
    pass


load_dotenv()

TOKEN = str(os.getenv("DISCORD_TOKEN"))

client = commands.Bot(command_prefix="!", intents=discord.Intents.all())


@client.event
async def on_ready():
    await client.tree.sync()
    print("Success: Bot is connected to Discord")


# example slash command
@client.tree.command(name="ping", description="Shows the bot's latency in ms.")
async def ping(interaction: discord.Interaction):
    bot_latency = round(client.latency * 1000)
    await interaction.response.send_message(f"Pong! {bot_latency}")


@client.command()
async def test(ctx, args):
    await ctx.send(f"Pong {args}")


@client.tree.command(name="test", description="testing slash commands")
async def test(interaction: discord.Interaction):
    await interaction.response.send_message("it worked!")

client.run(TOKEN)
