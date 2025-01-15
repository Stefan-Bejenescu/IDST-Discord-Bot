#!./.venv/bin/python

import discord
import os
from discord.ext import commands

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

def log_msg(msg: str, level: str):
    levels = {
        'debug': ('\033[34m', '-'),
        'info': ('\033[32m', '*'),
        'warning': ('\033[33m', '?'),
        'error': ('\033[31m', '!'),
    }
    if level not in levels:
        level = 'info'
    print(f"{levels[level][0]}[{levels[level][1]}] {msg}\033[0m")

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

MUSIC_DIR = './music'  # Directory containing music files

@bot.event
async def on_ready():
    log_msg(f'Logged on as {bot.user}', 'info')

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    await bot.process_commands(msg)

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id == bot.user.id and before.channel and not after.channel:
        log_msg("Bot disconnected from the voice channel.", "info")
    elif member.id != bot.user.id and before.channel and before.channel == bot.user.voice_client.channel:
        if len(before.channel.members) == 1:  # Bot is alone
            log_msg("Bot is alone in the voice channel, disconnecting.", "info")
            await bot.voice_client.disconnect()

@bot.command(brief='Play a song by name')
async def play(ctx, song: str):
    voice_channel = ctx.author.voice.channel
    if voice_channel is None:
        await ctx.send("You need to be in a voice channel to use this command.")
        return
    
    file_path = os.path.join(MUSIC_DIR, song)
    if not os.path.isfile(file_path):
        await ctx.send(f"Song `{song}` not found in the music directory.")
        return

    vc = ctx.voice_client or await voice_channel.connect()
    vc.play(discord.FFmpegPCMAudio(executable='ffmpeg', source=file_path))
    await ctx.send(f"Playing `{song}` in {voice_channel.name}.")

@bot.command(brief='List all available songs')
async def list(ctx):
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)
    songs = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
    if not songs:
        await ctx.send("No songs available.")
    else:
        await ctx.send("Available songs:\n" + "\n".join(songs))

@bot.command(brief='Disconnect the bot immediately')
async def scram(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("Not connected to any voice channel.")

@bot.command(brief='Disconnect from the voice channel')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected.")
    else:
        await ctx.send("Not connected to any voice channel.")

################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

if __name__ == '__main__':
    if not os.path.exists(MUSIC_DIR):
        os.makedirs(MUSIC_DIR)
    token=os.getenv("DISCORD_BOT_TOKEN")
    bot.run(token)