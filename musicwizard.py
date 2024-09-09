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
        # Use this instead of await client.tree.sync to instantly sync your changes with the server you are testing on
        # and comment out the other client.tree.sync call
        await client.tree.sync(guild=discord.Object(id=198183299011706880))
        # await client.tree.sync()
        print(f"{client.user} is now pondering it's orb")

    def add_song_to_queue(guild_id, link, title):
        if guild_id not in queues:
            queues[guild_id] = []
        queues[guild_id].append((link, title))

    async def play_from_queue(ctx):
        if ctx.guild.id in queues and queues[ctx.guild.id]:
            link, title = queues[ctx.guild.id].pop(0)
            await play_song(ctx, link, title)
        else:
            await asyncio.sleep(2)
            await voice_clients[ctx.guild.id].disconnect()

    async def play_song(ctx, link, title):
        try:
            voice_client = voice_clients[ctx.guild.id]
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(link, download=False)
            )
            song_url = data["url"]
            player = discord.FFmpegOpusAudio(song_url, **ffmpeg_options)

            voice_client.play(
                player,
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    play_from_queue(ctx), client.loop
                ),
            )
            await ctx.send(f"Now Playing: **{title}**")
        except Exception as e:
            print(f"Error playing song: {e}")

    @client.hybrid_command(
        name="play",
        with_app_command=True,
        description="Plays or adds a song to the queue.",
    )
    async def play(ctx, *, link):
        # Check if the user is in a voice channel
        if not ctx.author.voice:
            await ctx.send("You need to be in a voice channel to use this command")
            return

        # Connect to the voice channle if not already connected
        try:
            voice_client = await ctx.author.voice.channel.connect()
            voice_clients[voice_client.guild.id] = voice_client
        except discord.ClientException:
            # Already connected to a channel in the server/guild
            voice_client = voice_clients.get(ctx.guild.id)

        if youtube_base_url not in link:
            query_string = urllib.parse.urlencode({"search_query": link})

            content = urllib.request.urlopen(youtube_results_url + query_string)

            search_results = re.findall(r"/watch\?v=(.{11})", content.read().decode())
            if not search_results:
                await ctx.send("DEBUG: No results found")
                return

            link = youtube_watch_url + search_results[0]

        # Run Youtube-DL in an async-friendly way and get the song title
        loop = asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(link, download=False)
        )

        song_title = data["title"]

        # Add song to the queue
        add_song_to_queue(ctx.guild.id, link, song_title)
        await ctx.send(f"Added to queue: **{song_title}**")

        # If not currently playing, start playing
        if not voice_clients[ctx.guild.id].is_playing():
            await play_from_queue(ctx)

    @client.hybrid_command(
        name="queue", with_app_command=True, description="Lists the songs in the queue."
    )
    async def queue(ctx):
        # Displays the current queue of songs with titles.
        if ctx.guild.id in queues and queues[ctx.guild.id]:
            song_titles = [
                f"{index + 1}. {title}"
                for index, (_, title) in enumerate(queues[ctx.guild.id])
            ]
            output = "\n".join(song_titles)
            await ctx.send(f"**Current Queue:**\n{output}")
        else:
            await ctx.send("The queue is empty!")

    @client.hybrid_command(
        name="skip",
        with_app_command=True,
        description="Skips the currently playing song.",
    )
    async def skip(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await play_from_queue(ctx)
            await ctx.send("Skipped current track!")
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="shuffle", with_app_command=True, description="Shuffles the queue."
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
        name="pause", with_app_command=True, description="Pauses the current song."
    )
    async def pause(ctx):
        try:
            voice_clients[ctx.guild.id].pause()
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="resume",
        with_app_command=True,
        description="Resumes playing the current song.",
    )
    async def resume(ctx):
        try:
            voice_clients[ctx.guild.id].resume()
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="stop",
        with_app_command=True,
        description="Stops the song and clears the queue.",
    )
    async def stop(ctx):
        try:
            voice_clients[ctx.guild.id].stop()
            await voice_clients[ctx.guild.id].disconnect()
            del voice_clients[ctx.guild.id]
            await clear_queue(ctx)
        except Exception as e:
            print(e)

    @client.hybrid_command(
        name="move", with_app_command=True, description="Moves songs in the queue."
    )
    async def move(ctx, song_index: int, destination_index: int):
        if ctx.guild.id not in queues or not queues[ctx.guild.id]:
            await ctx.send("The queue is empty!")
            return

        # This is a reference to the queue not a copy
        # Using this just to make the code a bit easier to read
        queue = queues[ctx.guild.id]
        queue_length = len(queue)

        # Check if 0 is inputted
        if song_index == 0 or destination_index == 0:
            await ctx.send("An index of 0 is not supported.")
            return

        # Adjust 1-based index to 0-based for positive indices
        if song_index > 0:
            song_index -= 1
        if destination_index > 0:
            destination_index -= 1

        # Adjust the indices if given a negative number
        if song_index < 0:
            song_index = queue_length + song_index
        if destination_index < 0:
            destination_index = queue_length + destination_index

        # Check if the inputted indices are within the valid range
        if not (0 <= song_index < queue_length) or not (
            0 <= destination_index < queue_length
        ):
            await ctx.send(f"Indices must be between 1 and {queue_length}.")
            return

        # Ensure destination index is not the same as the song index
        if song_index == destination_index:
            await ctx.send("The song is already in the desired position.")
            return

        # Move the song
        song = queue.pop(song_index)
        queue.insert(destination_index, song)

        await ctx.send(
            f"Moved **{song[1]}** to position {destination_index + 1} in the queue."
        )

    client.run(TOKEN)
