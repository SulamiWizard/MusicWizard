import asyncio
import os
import random
import re
import urllib.parse
import urllib.request

import discord
import yt_dlp
from discord.ext import commands
from dotenv import load_dotenv


def run_bot():
    load_dotenv()
    TOKEN = str(os.getenv("DISCORD_TOKEN"))
    intents = discord.Intents.default()
    intents.message_content = True
    client = commands.Bot(command_prefix=".", intents=intents)

    queues = {}
    voice_clients = {}
    youtube_base_url = "https://www.youtube.com/"
    youtube_results_url = youtube_base_url + "results?"
    youtube_watch_url = youtube_base_url + "watch?v="
    yt_dl_options = {"format": "bestaudio/best"}
    ytdl = yt_dlp.YoutubeDL(yt_dl_options)

    ffmpeg_options = {
        "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
        "options": '-vn -filter:a "volume=0.25"',
    }

    @client.event
    async def on_ready():
        await client.tree.sync()
        print(f"{client.user} is now pondering it's orb")

    async def play_next(ctx):
        # Checks if there are songs in the queue
        # If there are songs in the queue, pop the next song and play it
        if queues[ctx.guild.id] != []:
            # Using queues[ctx.guild.id] is sort of similar to a hash map i think. Correct me and call me an idiot if I am wrong
            # The same would apply to really anything with a guild.id in the index of an array
            #
            # The main reason we use this index [ctx.guild.id] in the array is to allow us to control the bot in each server seperately,
            # instead of globally controlling all instances of the bot
            link = queues[ctx.guild.id].pop(0)
            await play(ctx, link=link)
        else:
            # Auto disconnect after 2 seconds at the end of the queue
            await asyncio.sleep(2)
            await voice_clients[ctx.guild.id].disconnect()

    @client.hybrid_command(
        name="play", with_app_command=True, description="Play or queue a song."
    )
    async def play(ctx, *, link):
        # This first try/catch statement is solely used to connect to the voice channel that the user is in
        #
        # TODO: Add functionality for when the message sender is not currently in any voice channel for the bot to connect to.
        #   Ideally this would be in the form of a message sent to the channel the command was placed in, could be ephemeral or not.
        #   Also it should not try to download and play the song if it doesn't have a channel to connect to.
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except Exception as e:
            print(e)

        # This next try/catch statement handles the actual downloading and playing of the content from the link passed to the play command
        try:
            if youtube_base_url not in link:
                query_string = urllib.parse.urlencode({"search_query": link})

                content = urllib.request.urlopen(youtube_results_url + query_string)

                search_results = re.findall(
                    r"/watch\?v=(.{11})", content.read().decode()
                )

                link = youtube_watch_url + search_results[0]

            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(link, download=False)
            )

            song = data["url"]
            player = discord.FFmpegOpusAudio(song, **ffmpeg_options)

            voice_clients[ctx.guild.id].play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_next(ctx), client.loop
                ),
            )
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="skip",
        with_app_command=True,
        description="Skip the currently playing song.",
    )
    async def skip(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await play_next(ctx)
            await ctx.send("Skipped current track!")
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="shuffle", with_app_command=True, description="Shuffle the queue!"
    )
    async def shuffle(ctx):
        random.shuffle(queues[ctx.guild.id])
        await ctx.send("The queue has been shuffled!")

    @client.hybrid_command(
        name="clear",
        with_app_command=True,
        description="Clears the queue without skipping the current song.",
    )
    async def clear_queue(ctx):
        if ctx.guild.id in queues:
            queues[ctx.guild.id].clear()
            await ctx.send("Queue cleared!")
        else:
            await ctx.send("There is no queue to clear")

    @client.hybrid_command(
        name="pause", with_app_command=True, description="Pause the current song."
    )
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="resume",
        with_app_command=True,
        description="Resume playing the current song.",
    )
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="stop",
        with_app_command=True,
        description="Stop the song and clear the queue.",
    )
    async def stop(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]

            # Having the queue be cleared when stopping the bot is handled by this next line.
            # Commenting this line will keep the queue for the the next time the bot joins a channel
            await clear_queue(ctx)
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="queue", with_app_command=True, description="List the songs in the queue."
    )
    # url is deafulting to None to allow the parameter to be optional
    # TODO: Make the queue function solely list the queue instead of adding stuff to it.
    #       Only do this after we get the /play command working as intended
    async def queue(ctx, *, url=None):
        if url is not None:
            # First checks if the queue exists then pushes the song to the back of the queue
            if ctx.guild.id not in queues:
                queues[ctx.guild.id] = []
            queues[ctx.guild.id].append(url)
            await ctx.send("Added to queue!")
        else:
            for song in queues[ctx.guild.id]:
                # TODO: show song titles instead of the urls when listing tracks in queue
                await ctx.send(song)

    client.run(TOKEN)
