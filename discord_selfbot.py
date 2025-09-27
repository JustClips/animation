import os
import discord
from discord.ext import tasks
from itertools import cycle

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")
STATUS_TEXT = "The Best Developer"
STATUS_EMOJI = "💻"  # You can change this emoji

# Create the bot client instance
client = discord.Client()


# --- Animated Status Setup ---
def generate_animation_frames(text):
    """Creates a list of strings for the animation effect."""
    frames = []
    # Build up the string, letter by letter
    for i in range(1, len(text) + 1):
        frames.append(text[:i])
    # Tear down the string, letter by letter
    for i in range(len(text) - 1, -1, -1):
        frames.append(text[:i])
    return frames

# Create an infinite cycle from the animation frames
status_frames = cycle(generate_animation_frames(STATUS_TEXT))


# --- Background Task to Change Status ---
@tasks.loop(seconds=1)
async def change_status():
    """Cycles through the animated status frames."""
    # NOTE: The 15-second delay is to avoid errors from Discord's rate limits.
    new_status_text = next(status_frames)
    
    # Use CustomActivity for a custom status with an emoji
    activity = discord.CustomActivity(name=new_status_text, emoji=STATUS_EMOJI)
    
    await client.change_presence(activity=activity)


# --- Bot Ready Event ---
@client.event
async def on_ready():
    """Called when the bot successfully logs in."""
    print(f'✅ Logged in as {client.user}')
    print('🚀 Starting custom status animation...')
    change_status.start()


# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    client.run(TOKEN)
