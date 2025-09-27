import os
import discord
from discord.ext import tasks
from itertools import cycle

# --- Configuration ---
# Your bot's token should be stored as an environment variable for security.
TOKEN = os.getenv("DISCORD_TOKEN")

# The text and emoji you want to animate in the custom status.
STATUS_TEXT = "The Best Developer"
STATUS_EMOJI = "💻"  # You can change the emoji here, or set it to None

# Create the bot client instance.
# You might need to specify intents for the custom status to show up reliably.
intents = discord.Intents.default()
client = discord.Client(intents=intents)


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
@tasks.loop(seconds=1)
async def change_status():
    """Cycles through the animated status frames and updates the bot's presence."""
    # NOTE: The 15-second interval is to stay within Discord's API rate limits.
    new_status_text = next(status_frames)

    # --- THIS IS THE MODIFIED PART ---
    # We now use discord.Custom to create a custom status.
    activity = discord.Custom(name=new_status_text, emoji=STATUS_EMOJI)
    
    await client.change_presence(activity=activity)


# --- Bot Events ---
@client.event
async def on_ready():
    """Called when the bot successfully logs in."""
    print(f'✅ Logged in as {client.user}')
    print('🚀 Starting custom status animation loop...')
    change_status.start() # Starts the animation loop.


# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    client.run(TOKEN)
