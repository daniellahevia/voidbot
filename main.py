import os
import discord
from discord.ext import commands

# Get token from environment variable,
TOKEN = os.getenv("TOKEN")  # Changed to more specific name

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

# In-memory storage of void channel IDs,
void_channel_ids = set()

class VoidSetupView(discord.ui.View):
    def init(self, channel_id):
        super().init(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def enable(self, interaction: discord.Interaction, button: discord.ui.Button):
        void_channel_ids.add(self.channel_id)
        await interaction.response.send_message(
            " This channel is now a void. Messages will auto-delete.", 
            ephemeral=True
        )

    @discord.ui.button(label="Disable", style=discord.ButtonStyle.red)
    async def disable(self, interaction: discord.Interaction, button: discord.ui.Button):
        void_channel_ids.discard(self.channel_id)
        await interaction.response.send_message(
            " This channel is no longer a void.", 
            ephemeral=True
        )
@bot.event
async def on_ready():
    print(f' Logged in as {bot.user} (ID: {bot.user.id})')
    print(f' Invite link: https://discord.com/oauth2/authorize?client_id={bot.user.id}&scope=bot&permissions=274878024704')

@bot.command(name="setupvoid")
@commands.has_permissions(manage_channels=True)  # Added permission check
async def setup_void(ctx):
    """Sets up the current channel as a void channel where messages auto-delete"""
    embed = discord.Embed(
        title="Void Channel Setup",
        description="Click Enable to auto-delete messages here.\nClick Disable to stop that.",
        color=discord.Color.dark_purple()
    )
    view = VoidSetupView(channel_id=ctx.channel.id)
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_message(message):
    if message.author.bot or not message.guild:
        return await bot.process_commands(message)  # Moved this here for early return

    if message.channel.id in void_channel_ids:
        try:
            await message.delete()
        except discord.Forbidden:
            print(f" No permission to delete in #{message.channel.name} ({message.channel.id})")
        except discord.HTTPException as e:
            print(f"Failed to delete message in #{message.channel.name}: {e}")

    await bot.process_commands(message)

@setup_void.error
async def setup_void_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(" You need the 'Manage Channels' permission to use this command.")

if name == "main":
    bot.run(TOKEN)

