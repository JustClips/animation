import os
import discord
from discord.ext import tasks

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")
TARGET_CHANNEL_ID = 1410395105965375600 # The channel ID for the hourly message

# --- Bot Setup ---
intents = discord.Intents.default()
client = discord.Client(intents=intents)

# --- Background Task to Send a Scheduled Message ---
# The interval is set to a safe 1 hour. NEVER set this to a few seconds.
@tasks.loop(seconds=1)
async def hourly_message():
    # Wait until the bot is ready before trying to send the first message
    await client.wait_until_ready()
    
    # Get the channel object from the ID
    channel = client.get_channel(TARGET_CHANNEL_ID)
    
    if channel:
        try:
            await channel.send("This is the hourly scheduled message!")
            print(f"✅ Sent hourly message to channel {TARGET_CHANNEL_ID}")
        except discord.errors.Forbidden:
            print(f"❌ ERROR: I don't have permission to send messages in channel {TARGET_CHANNEL_ID}.")
    else:
        print(f"❌ ERROR: Could not find channel with ID {TARGET_CHANNEL_ID}.")


# --- Bot Ready Event ---
@client.event
async def on_ready():
    """Called when the bot successfully logs in."""
    print(f'✅ Logged in as {client.user}')
    print('🚀 Starting hourly message task...')
    hourly_message.start() # Start the loop


# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    try:
        client.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ ERROR: Invalid DISCORD_TOKEN. Please check your token and try again.")
    except discord.errors.DiscordException as e:
        print(f"❌ An unexpected Discord error occurred: {e}")
