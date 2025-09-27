import os
import discord
from discord.ext import tasks
from itertools import cycle

# --- Configuration ---
# Your bot's token should be stored as an environment variable for security.
TOKEN = os.getenv("DISCORD_TOKEN")

# The text you want to animate in the status.
STATUS_TEXT = "The Best Developer"

# Create the bot client instance.
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

# Generate the frames and create an infinite cycle from them.
status_frames = cycle(generate_animation_frames(STATUS_TEXT))


# --- Background Task Definition ---
@tasks.loop(seconds=15)
async def change_status():
    """Cycles through the animated status frames and updates the bot's presence."""
    # NOTE: The 15-second interval is to stay within Discord's API rate limits
    # for status updates (5 per minute). Making this faster could get your bot flagged.
    new_status = next(status_frames)
    await client.change_presence(activity=discord.Game(name=new_status))


# --- Bot Events ---
@client.event
async def on_ready():
    """Called when the bot successfully logs in."""
    print(f'✅ Logged in as {client.user}')
    print('🚀 Starting status animation loop...')
    change_status.start() # Starts the animation loop.


# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    client.run(TOKEN)
