import os
import discord
from discord.ext import commands

# --- Configuration ---
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Bot Setup ---
intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store channel configurations
channel_configs = []

# --- Slash Command Setup ---
@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# --- Slash Command: /start ---
@bot.tree.command(name="start", description="Configure and create channels with messages")
async def start_config(interaction: discord.Interaction):
    # Check if user has administrator permissions
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You need administrator permissions to use this command!", ephemeral=True)
        return

    # Create modal for configuration
    modal = ChannelConfigModal()
    await interaction.response.send_modal(modal)

# --- Modal for Configuration ---
class ChannelConfigModal(discord.ui.Modal, title="Channel Configuration"):
    def __init__(self):
        super().__init__()

    channel_config = discord.ui.TextInput(
        label="Channel Configurations",
        style=discord.TextStyle.long,
        placeholder="Format: channel_name:message (one per line)\nExample:\ngeneral:Welcome to the server!\ntest:This is a test channel\nannouncements:Important announcements here",
        required=True,
        max_length=2000
    )

    confirmation = discord.ui.TextInput(
        label="Type 'CONFIRM' to proceed",
        style=discord.TextStyle.short,
        placeholder="Type CONFIRM to execute",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Check confirmation
        if self.confirmation.value != "CONFIRM":
            await interaction.response.send_message("❌ Confirmation failed. Please type 'CONFIRM' exactly.", ephemeral=True)
            return

        # Parse channel configurations
        configs = []
        lines = self.channel_config.value.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                channel_name, message = line.split(':', 1)
                configs.append({
                    'name': channel_name.strip(),
                    'message': message.strip()
                })

        if not configs:
            await interaction.response.send_message("❌ No valid configurations found. Please check the format.", ephemeral=True)
            return

        # Process the configuration
        await interaction.response.send_message("🔄 Processing channel creation...", ephemeral=True)
        
        try:
            guild = interaction.guild
            
            # Delete all existing channels
            deleted_count = 0
            for channel in guild.channels:
                try:
                    await channel.delete()
                    deleted_count += 1
                except Exception as e:
                    print(f"❌ Error deleting channel {channel.name}: {e}")
            
            # Create new channels and send messages
            created_channels = []
            for config in configs:
                try:
                    # Create text channel
                    new_channel = await guild.create_text_channel(config['name'])
                    created_channels.append(new_channel.name)
                    
                    # Send message in the channel
                    await new_channel.send(config['message'])
                    
                except Exception as e:
                    print(f"❌ Error creating channel {config['name']}: {e}")
            
            # Send completion message
            result_msg = f"✅ Configuration completed!\n- Deleted {deleted_count} channels\n- Created {len(created_channels)} channels: {', '.join(created_channels)}"
            await interaction.followup.send(result_msg, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred: {e}", ephemeral=True)

# --- Run the Bot ---
if TOKEN is None:
    print("❌ ERROR: DISCORD_TOKEN environment variable is not set.")
else:
    try:
        bot.run(TOKEN)
    except discord.errors.LoginFailure:
        print("❌ ERROR: Invalid DISCORD_TOKEN. Please check your token and try again.")
    except discord.errors.DiscordException as e:
        print(f"❌ An unexpected Discord error occurred: {e}")
