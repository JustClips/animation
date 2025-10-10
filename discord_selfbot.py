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
    "channel_name": "test-channel",
    "message": "Hello! This is a test message.",
    "max_channels": 500  # Discord limit is ~500 channels per server
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
@bot.tree.command(name="configure", description="Set up channel name and message")
async def configure(interaction: discord.Interaction, channel_name: str, message: str, max_channels: int = 500):
    """Configure the channel name, message, and maximum number of channels"""
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)
        return

    # Validate max_channels
    if max_channels < 1 or max_channels > 500:
        await interaction.response.send_message("❌ Max channels must be between 1 and 500", ephemeral=True)
        return

    # Update configuration
    bot_config["channel_name"] = channel_name
    bot_config["message"] = message
    bot_config["max_channels"] = max_channels
    
    await interaction.response.send_message(
        f"✅ Configuration updated!\n"
        f"Channel name: `{channel_name}`\n"
        f"Message: `{message}`\n"
        f"Max channels: `{max_channels}`\n"
        f"\nNow use `/create` to start creating channels!", 
        ephemeral=True
    )

# --- Slash Command: /create ---
@bot.tree.command(name="create", description="Create configured channels and send messages")
async def create(interaction: discord.Interaction):
    """Create channels and send configured message in each"""
    
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
        max_channels = bot_config["max_channels"]
        
        # Count existing channels
        existing_channels = len(guild.channels)
        channels_to_create = min(max_channels, 500 - existing_channels)
        
        if channels_to_create <= 0:
            await interaction.followup.send(
                f"❌ Cannot create more channels! Server has {existing_channels} channels (limit is 500)", 
                ephemeral=True
            )
            return

        # Create channels and send messages
        created_count = 0
        errors = []
        
        for i in range(channels_to_create):
            try:
                # Create unique channel name
                unique_name = f"{channel_name}-{i+1}" if channels_to_create > 1 else channel_name
                
                # Create text channel
                new_channel = await guild.create_text_channel(unique_name)
                created_count += 1
                
                # Send message in the channel
                await new_channel.send(message)
                
            except discord.errors.HTTPException as e:
                if "Maximum number of channels" in str(e):
                    errors.append(f"Reached Discord channel limit at {created_count} channels")
                    break
                else:
                    errors.append(f"Channel {i+1}: {str(e)[:50]}")
            except Exception as e:
                errors.append(f"Channel {i+1}: {str(e)[:50]}")

        # Prepare response
        response = f"✅ Channel Creation Completed!\n"
        response += f"- Created {created_count} channels\n"
        response += f"- Channel name pattern: `{channel_name}`\n"
        response += f"- Message sent: `{message}`\n"
        
        if errors:
            response += f"\n⚠️ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
        
        await interaction.followup.send(response, ephemeral=True)

    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}", ephemeral=True)

# --- Slash Command: /clear ---
@bot.tree.command(name="clear", description="Delete all channels in the server")
async def clear(interaction: discord.Interaction):
    """Delete all channels in the server"""
    
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

        # Delete all channels
        deleted_count = 0
        errors = []
        
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {channel.name}: {str(e)[:50]}")

        # Prepare response
        response = f"✅ Channel Deletion Completed!\n"
        response += f"- Deleted {deleted_count} channels\n"
        
        if errors:
            response += f"\n⚠️ Errors ({len(errors)}):\n" + "\n".join(errors[:10])
        
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
