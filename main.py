import discord
from discord.ext import commands
import os
import random
import asyncio
from flask import Flask
from threading import Thread

# --- 1. نظام التشغيل 24 ساعة ---
app = Flask('')
@app.route('/')
def home(): return "البوت يعمل بنجاح 24/7!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول باسم: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="إدارة السيرفر | !أوامر"))

# --- 3. نظام الحماية والترحيب ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            await message.channel.send(f"⚠️ ممنوع نشر الروابط يا {message.author.mention}!", delete_after=5)
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if channel:
        await channel.send(f"✨ نورت السيرفر يا {member.mention}! نتمنى لك وقتاً ممتعاً.")

# --- 4. أوامر الإدارة (بما فيها السجن) ---

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_ar(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ تم مسح {amount} رسالة بنجاح!', delete_after=5)

@bot.command(name="سجن")
@commands.has_permissions(manage_roles=True)
async def mute_ar(ctx, member: discord.Member, time: int = 15, *, reason="غير محدد"):
    # البوت بيبحث عن رتبة اسمها Muted أو بيحبس العضو عن طريق تعطيل صلاحية الكلام
    guild = ctx.guild
    muted_role = discord.utils.get(guild.roles, name="Muted")
    
    if not muted_role:
        muted_role = await guild.create_role(name="Muted")
        for channel in guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
            
    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"🤐 تم سجن {member.mention} لمدة {time} دقيقة | السبب: {reason}")
    await asyncio.sleep(time * 60)
    await member.remove_roles(muted_role)
    await ctx.send(f"🔓 تم فك سجن {member.mention} تلقائياً.")

@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick_ar(ctx, member: discord.Member, *, reason="غير محدد"):
    await member.kick(reason=reason)
    await ctx.send(f'🚫 تم طرد {member.display_name} | السبب: {reason}')

@bot.command(name="بند")
@commands.has_permissions(ban_members=True)
async def ban_ar(ctx, member: discord.Member, *, reason="غير محدد"):
    await member.ban(reason=reason)
    await ctx.send(f'❌ تم حظر {member.display_name} نهائياً!')

# --- 5. قسم الألعاب والترفيه ---

@bot.command(name="روليت")
async def roulette_ar(ctx):
    outcomes = ['فزت! 🎉 البوت هو اللي مات المرة دي.', 'للأسف.. طلقة في الراس! مات العضو. 💀', 'نجوت بأعجوبة! 🔫']
    result = random.choice(outcomes)
    await ctx.send(f"**{ctx.author.display_name}** جرب حظه في الروليت...\n{result}")

@bot.command(name="لعب")
async def rps_ar(ctx, choice: str):
    options = ['حجر', 'ورقة', 'مقص']
    bot_choice = random.choice(options)
    if choice not in options:
        await ctx.send("اختار: (حجر، ورقة، مقص)")
        return
    if choice == bot_choice: result = "تعادل! 🤝"
    elif (choice == 'حجر' and bot_choice == 'مقص') or (choice == 'ورقة' and bot_choice == 'حجر') or (choice == 'مقص' and bot_choice == 'ورقة'):
        result = "أنت فزت! 🏆"
    else: result = "أنا اللي فزت! 😎"
    await ctx.send(f"أنت: {choice} | أنا: {bot_choice}\n**النتيجة: {result}**")

# --- 6. قائمة الأوامر ---
@bot.command(name="أوامر")
async def help_ar(ctx):
    embed = discord.Embed(title="📜 قائمة الأوامر المتاحة", color=discord.Color.gold())
    embed.add_field(name="🛡️ الإدارة", value="`!مسح` , `!سجن [عضو] [دقائق]` , `!طرد` , `!بند`", inline=False)
    embed.add_field(name="🎮 الألعاب", value="`!روليت` , `!لعب [حجر/ورقة/مقص]`", inline=False)
    embed.set_footer(text="سيستم متكامل لحماية وإدارة السيرفر")
    await ctx.send(embed=embed)

# --- تشغيل البوت ---
keep_alive()
bot.run(os.getenv('TOKEN'))
