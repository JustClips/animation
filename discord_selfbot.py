import os
import discord
from discord.ext import commands

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store configuration
bot_config = {
    "channel_name": "test",
    "message": "Hello! This is a test message.",
    "number_of_channels": 5
}

# --- Event: Bot Ready ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# --- Slash Command: /configure ---
@bot.tree.command(name="configure", description="Set up channel name, message, and number of channels")
async def configure(interaction: discord.Interaction, channel_name: str, message: str, number_of_channels: int = 5):
    """Configure the channel name, message, and number of channels to create"""
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)
        return

    # Validate number_of_channels
    if number_of_channels < 1 or number_of_channels > 50:
        await interaction.response.send_message("❌ Number of channels must be between 1 and 50", ephemeral=True)
        return

    # Update configuration
    bot_config["channel_name"] = channel_name
    bot_config["message"] = message
    bot_config["number_of_channels"] = number_of_channels
    
    await interaction.response.send_message(
        f"✅ Configuration updated!\n"
        f"Channel name: `{channel_name}`\n"
        f"Message: `{message}`\n"
        f"Number of channels: `{number_of_channels}`\n"
        f"\nNow use `/start` to create channels and send messages!", 
        ephemeral=True
    )

# --- Slash Command: /start ---
@bot.tree.command(name="start", description="Delete all channels, create new ones, and send 10 messages in each")
async def start(interaction: discord.Interaction):
    """Delete all channels, create configured channels, and send 10 messages in each"""
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    
    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Could not find guild", ephemeral=True)
            return

        # Get configuration
        channel_name = bot_config["channel_name"]
        message = bot_config["message"]
        number_of_channels = bot_config["number_of_channels"]
        
        # Delete all existing channels first
        deleted_count = 0
        errors = []
        
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {channel.name}: {str(e)[:50]}")

        # Create new channels and send 10 messages in each
        created_channels = []
        message_errors = []
        
        for i in range(number_of_channels):
            try:
                # Create channel with the exact name (no numbering)
                new_channel = await guild.create_text_channel(channel_name)
                created_channels.append(new_channel.name)
                
                # Send 10 messages in the channel
                for j in range(10):
                    try:
                        await new_channel.send(message)
                    except Exception as e:
                        message_errors.append(f"Message {j+1} in channel {i+1}: {str(e)[:50]}")
                        break
                
            except Exception as e:
                errors.append(f"Channel {i+1}: {str(e)[:50]}")

        # Prepare response
        response = f"✅ Process Completed!\n"
        response += f"- Deleted {deleted_count} existing channels\n"
        response += f"- Created {len(created_channels)} channels named `{channel_name}`\n"
        response += f"- Sent 10 messages to each channel\n"
        response += f"- Total messages sent: {len(created_channels) * 10 - len(message_errors)}\n"
        
        if errors:
            response += f"\n⚠️ Channel errors ({len(errors)}):\n" + "\n".join(errors[:5])
            
        if message_errors:
            response += f"\n⚠️ Message errors ({len(message_errors)}):\n" + "\n".join(message_errors[:5])
        
        await interaction.followup.send(response, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ ERROR: Invalid DISCORD_TOKEN. Please check your token and try again.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
