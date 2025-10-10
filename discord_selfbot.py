import os
import discord
from discord.ext import commands

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
bot = commands.Bot(command_prefix='!')

# --- Event: Bot Ready ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

# --- Regular Command: !start ---
@bot.command(name="start")
async def start(ctx, *, channels_and_messages):
    """
    Create channels and send messages
    Format: channel1_name:message1 | channel2_name:message2 | ...
    Example: !start general:Welcome! | test:Testing channel | announcements:Read me!
    """
    
    # Check if user has administrator permissions
    if not ctx.message.author.guild_permissions.administrator:
        await ctx.send("❌ You need administrator permissions!")
        return

    await ctx.send("🔄 Processing... Please wait.")
    
    try:
        guild = ctx.message.guild
        if not guild:
            await ctx.send("❌ Could not find guild")
            return

        # Parse input: split by | to get channel:message pairs
        pairs = channels_and_messages.split('|')
        created_channels = []
        errors = []

        # Delete all existing channels first
        deleted_count = 0
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {channel.name}: {str(e)[:50]}")

        # Create new channels and send messages
        for pair in pairs:
            if ':' in pair:
                channel_name, message = pair.split(':', 1)
                channel_name = channel_name.strip()
                message = message.strip()
                
                try:
                    # Create text channel
                    new_channel = await guild.create_text_channel(channel_name)
                    created_channels.append(channel_name)
                    
                    # Send message in the channel
                    await new_channel.send(message)
                    
                except Exception as e:
                    errors.append(f"Failed to create/send to {channel_name}: {str(e)[:50]}")
            else:
                errors.append(f"Invalid format in: {pair}")

        # Prepare response
        response = f"✅ Completed!\n"
        response += f"- Deleted {deleted_count} channels\n"
        response += f"- Created {len(created_channels)} channels: {', '.join(created_channels)}\n"
        
        if errors:
            response += f"\n⚠️ Errors ({len(errors)}):\n" + "\n".join(errors[:5])
        
        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    try:
        bot.run(TOKEN)
    except:
        print("❌ ERROR: Invalid DISCORD_TOKEN or discord.py version issue.")
