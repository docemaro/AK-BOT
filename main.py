import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# --- نظام التشغيل 24 ساعة ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- إعدادات البوت ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    await bot.change_presence(activity=discord.Game(name="إدارة السيرفر | !help"))

# --- 1. أوامر الإدارة (Moderation) ---

# مسح الرسائل
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ تم مسح {amount} رسالة!', delete_after=5)

# طرد عضو
@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await member.kick(reason=reason)
    await ctx.send(f'🚫 تم طرد {member.display_name} | السبب: {reason}')

# حظر عضو
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="لا يوجد سبب"):
    await member.ban(reason=reason)
    await ctx.send(f'❌ تم حظر {member.display_name} نهائياً!')

# --- 2. نظام الترحيب ---
@bot.event
async def on_member_join(member):
    # البوت هيبحث عن روم اسمه welcome ويرحب فيه
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"✨ نورت السيرفر يا {member.mention}! نتمنى لك وقتاً ممتعاً.")

# --- تشغيل البوت ---
keep_alive()
bot.run(os.getenv('TOKEN'))
