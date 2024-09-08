# MusicWizard

A [Discord](https://discord.com) music bot that aims to work with multiple sources such as YouTube, Spotify, SoundCloud, and BandCamp.
---  

## Functionality

| Command    | Output                                                                                                                                        |    Status     |
|------------|-----------------------------------------------------------------------------------------------------------------------------------------------|:-------------:|
| /play[^1]  | Plays audio from the requested URL or chooses the top choice on YouTube search. If a song is currently playing, adds a new song to the queue. |   Complete    |
| /queue[^2] | Lists the songs in queue.                                                                                                                     |   Complete    |
| /pause     | Pauses the currently playing song.                                                                                                            |   Complete    |
| /resume    | Resumes playback after a pause.                                                                                                               |   Complete    |
| /skip      | Skips the current track.                                                                                                                      |   Complete    |
| /stop      | Stops playback, clears the current queue, and leaves the voice channel.                                                                       |   Complete    |
| /shuffle   | Shuffles the order of the queue.                                                                                                              |   Complete    |

[^1]: Currently, /play is only able to take YouTube links. Non-YouTube links and YouTube playlists are not currently
supported but implementation is planned. YouTube searching without links is also planned but not available.
[^2]: /play does not currently add a song to the end of the queue when one is already playing. .queue must be used for
that. If .queue is not provided a link, the bot will return all queued songs.
___

## Setup

### Clone Repository

```console
git clone https://github.com/sulamiwizard/MusicWizard
cd MusicWizard
```

After cloning, make sure that you **read the cloned** `README.md` to ensure that all additional comments are read.

### Install Python

Download and install [Python](https://www.python.org/downloads/).

Make sure that Python is added to your PATH variable to allow you to use it in the command line.


### Setup Virtual Environment

Complete within the bot's file directory

#### Linux/MacOS Setup

```console
python -m venv venv
source venv/bin/activate
```

#### Windows Setup

Using a virtual environment isnt necessarily needed on windows because you could install dependencies globally.
Windows users could skip to the Install Internal Dependencies step should they wish to do so.

##### Command Prompt

```console
python -m venv venv
venv\Scripts\activate.bat
```

##### Powershell

```console
python -m venv venv
venv/Scripts\Activate.ps1
```

[comment]: <> (this is not tested yet and should be taken with a grain of salt.)

### Install Internal Dependencies

```console
pip install -r requirements.txt
```

### Create Discord Application

Log into the [Discord developer portal](https://discord.com/developers/applications). In the top right corner, click `New Application`. Once the application is created, click `Bot` on the left side menu. Reset the bot token and copy it using the `Copy` button. Multi-factor authentication information maybe required at this step.

### Setup Environment Variables

Create a `.env` file. In the `.env` file, add:

```console
DISCORD_TOKEN=YOUR_TOKEN_HERE
```

Ensure that `YOUR_TOKEN_HERE` is replaced with the token of your Discord application.

### Run the bot

```console
python main.py
```
