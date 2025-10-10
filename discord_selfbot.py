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

# --- Event: Bot Ready ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# --- Slash Command: /setup ---
@bot.tree.command(name="setup", description="Configure channels and messages")
async def setup(interaction: discord.Interaction):
    """Open setup modal for channel configuration"""
    
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions!", ephemeral=True)
        return

    # Create and send modal
    modal = SetupModal()
    await interaction.response.send_modal(modal)

# --- Modal for Setup Configuration ---
class SetupModal(discord.ui.Modal, title="Channel Setup"):
    def __init__(self):
        super().__init__()

    channel1 = discord.ui.TextInput(
        label="Channel 1",
        placeholder="Format: channel_name:message",
        required=False,
        max_length=200
    )

    channel2 = discord.ui.TextInput(
        label="Channel 2",
        placeholder="Format: channel_name:message",
        required=False,
        max_length=200
    )

    channel3 = discord.ui.TextInput(
        label="Channel 3",
        placeholder="Format: channel_name:message",
        required=False,
        max_length=200
    )

    channel4 = discord.ui.TextInput(
        label="Channel 4",
        placeholder="Format: channel_name:message",
        required=False,
        max_length=200
    )

    channel5 = discord.ui.TextInput(
        label="Channel 5",
        placeholder="Format: channel_name:message",
        required=False,
        max_length=200
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = interaction.guild
            if not guild:
                await interaction.followup.send("❌ Could not find guild", ephemeral=True)
                return

            # Collect all channel configurations
            channels_data = [
                self.channel1.value,
                self.channel2.value,
                self.channel3.value,
                self.channel4.value,
                self.channel5.value
            ]
            
            # Filter out empty configurations
            valid_channels = [ch for ch in channels_data if ch and ':' in ch]
            
            if not valid_channels:
                await interaction.followup.send("❌ No valid channel configurations provided!", ephemeral=True)
                return

            # Delete all existing channels first
            deleted_count = 0
            for channel in guild.channels:
                try:
                    await channel.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Error deleting channel {channel.name}: {e}")

            # Create new channels and send messages
            created_channels = []
            errors = []
            
            for channel_config in valid_channels:
                try:
                    channel_name, message = channel_config.split(':', 1)
                    channel_name = channel_name.strip()
                    message = message.strip()
                    
                    if channel_name and message:
                        # Create text channel
                        new_channel = await guild.create_text_channel(channel_name)
                        created_channels.append(channel_name)
                        
                        # Send message in the channel
                        await new_channel.send(message)
                    
                except Exception as e:
                    errors.append(f"Failed config: {channel_config[:30]}... Error: {str(e)[:50]}")

            # Prepare response
            response = f"✅ Setup Completed!\n"
            response += f"- Deleted {deleted_count} existing channels\n"
            response += f"- Created {len(created_channels)} new channels: {', '.join(created_channels)}\n"
            
            if errors:
                response += f"\n⚠️ Errors ({len(errors)}):\n" + "\n".join(errors[:5])
            else:
                response += "\n🎉 All channels created successfully!"
            
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
