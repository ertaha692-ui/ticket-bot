import os
import json
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1545171964967260301
STAFF_ROLE_ID = 1555981454956044316  
PANELS_FILE = "panels.json"
BANNER_PANEL = "https://cdn.discordapp.com/attachments/1545175797562867762/1565431683673759794/file_000000004f0c81f4b5be9b9e75f7baaf.png"
BANNER_TICKET = "https://cdn.discordapp.com/attachments/1545175797562867762/1565431701180518420/file_0000000026b481f48431ddb775253e45.png"
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
bot = commands.Bot(command_prefix="!", intents=intents)
DEFAULT_PANELS = [{"id": "media", "label": "ميديا"}, {"id": "support", "label": "الدعم الفني 🔨"}, {"id": "report_player", "label": "للبلاغ عن لاعب"}, {"id": "report_bug", "label": "للبلاغ عن خطأ"}]
def load_panels():
    if os.path.exists(PANELS_FILE):
        with open(PANELS_FILE, "r", encoding="utf-8") as f: return json.load(f)
    save_panels(DEFAULT_PANELS); return DEFAULT_PANELS
def save_panels(panels):
    with open(PANELS_FILE, "w", encoding="utf-8") as f: json.dump(panels, f, ensure_ascii=False, indent=2)
class ClaimButton(discord.ui.Button):
    def __init__(self): super().__init__(label="استلام", style=discord.ButtonStyle.success, custom_id="ticket_claim", emoji="🙋‍♂️")
    async def callback(self, interaction: discord.Interaction):
        channel = interaction.channel
        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
        if staff_role: await channel.set_permissions(staff_role, view_channel=False)
        await channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        embed = interaction.message.embeds[0]; embed.color = discord.Color.green()
        view = discord.ui.View(timeout=None); view.add_item(CloseButton())
        await interaction.response.edit_message(embed=embed, view=view)
class CloseButton(discord.ui.Button):
    def __init__(self): super().__init__(label="إغلاق", style=discord.ButtonStyle.danger, custom_id="ticket_close", emoji="🔒")
    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("جاري الإغلاق...", ephemeral=True); await interaction.channel.delete()
class CloseView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None); self.add_item(ClaimButton()); self.add_item(CloseButton())
class TicketButton(discord.ui.Button):
    def __init__(self, label, panel_id): super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ticket_open_{panel_id}"); self.panel_id = panel_id; self.panel_label = label
    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild; member = interaction.user
        overwrites = {guild.default_role: discord.PermissionOverwrite(view_channel=False), member: discord.PermissionOverwrite(view_channel=True, send_messages=True), guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True)}
        channel = await guild.create_text_channel(name=f"ticket-{member.name.lower()}-{self.panel_id}", overwrites=overwrites)
        embed = discord.Embed(title=f"🎫 {self.panel_label}", description=f"أهلاً {member.mention}", color=discord.Color.blue())
        if BANNER_TICKET: embed.set_image(url=BANNER_TICKET)
        await channel.send(content=member.mention, embed=embed, view=CloseView())
        await interaction.response.send_message(f"✅ {channel.mention}", ephemeral=True)
def build_panel_view():
    view = discord.ui.View(timeout=None)
    for p in load_panels(): view.add_item(TicketButton(label=p["label"], panel_id=p["id"]))
    return view
ticket_group = app_commands.Group(name="ticket", description="نظام التكتات")
@ticket_group.command(name="panel", description="إدارة اللوحات")
@app_commands.choices(action=[app_commands.Choice(name="send", value="send"), app_commands.Choice(name="add", value="add")])
async def panel(interaction: discord.Interaction, action: app_commands.Choice[str], name: str = None):
    await interaction.response.defer(ephemeral=True)
    if action.value == "send":
        embed = discord.Embed(title="🎫 تذاكر الدعم", color=discord.Color.blue())
        if BANNER_PANEL: embed.set_image(url=BANNER_PANEL)
        view = discord.ui.View(timeout=None)
        for p in load_panels(): view.add_item(TicketButton(label=p["label"], panel_id=p["id"]))
        await interaction.channel.send(embed=embed, view=view)
bot.tree.add_command(ticket_group)
@bot.event
async def on_ready():
    bot.add_view(build_panel_view()); bot.add_view(CloseView())
    if GUILD_ID:
        guild = discord.Object(id=GUILD_ID); bot.tree.copy_global_to(guild=guild); await bot.tree.sync(guild=guild)
    print(f"🤖 تكت شغال: {bot.user}")
bot.run(TOKEN)
