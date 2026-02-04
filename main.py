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

# قائمة الكلمات الممنوعة (تقدر تزيد عليها)
bad_words = ["كلمة1", "كلمة2", "سب"] 
# نظام تخزين التحذيرات (مؤقت في الرام)
warnings = {}

@bot.event
async def on_ready():
    print(f'تم تسجيل الدخول باسم: {bot.user}')
    await bot.change_presence(activity=discord.Game(name="إدارة السيرفر | !أوامر"))

# --- 3. نظام الحماية والترحيب والرتب التلقائية ---
@bot.event
async def on_message(message):
    if message.author.bot: return
    
    # حماية من الروابط
    if "http" in message.content or "discord.gg" in message.content:
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            return await message.channel.send(f"⚠️ ممنوع نشر الروابط يا {message.author.mention}!", delete_after=5)
    
    # حماية من السب
    if any(word in message.content for word in bad_words):
        if not message.author.guild_permissions.manage_messages:
            await message.delete()
            return await message.channel.send(f"❌ يا {message.author.mention}، التزم الأدب في الكلام!", delete_after=5)

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    # الترحيب (لازم روم اسمه welcome)
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome_channel:
        await welcome_channel.send(f"✨ نورت السيرفر يا {member.mention}! نتمنى لك وقتاً ممتعاً.")
    
    # الرتبة التلقائية (لازم يكون عندك رتبة اسمها Member أو عضو)
    role = discord.utils.get(member.guild.roles, name="Member")
    if role:
        await member.add_roles(role)

# --- 4. أوامر الإدارة الشاملة ---

@bot.command(name="مسح")
@commands.has_permissions(manage_messages=True)
async def clear_ar(ctx, amount: int = 5):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f'✅ تم مسح {amount} رسالة بنجاح!', delete_after=5)

@bot.command(name="سجن")
@commands.has_permissions(manage_roles=True)
async def mute_ar(ctx, member: discord.Member, time: int = 15, *, reason="غير محدد"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, speak=False, send_messages=False)
    await member.add_roles(muted_role)
    await ctx.send(f"🤐 تم سجن {member.mention} لمدة {time} دقيقة.")
    await asyncio.sleep(time * 60)
    await member.remove_roles(muted_role)

@bot.command(name="تحذير")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="غير محدد"):
    if member.id not in warnings:
        warnings[member.id] = 0
    warnings[member.id] += 1
    await ctx.send(f"⚠️ {member.mention} تم تحذيرك! عدد تحذيراتك الآن: {warnings[member.id]}\nالسبب: {reason}")
    if warnings[member.id] >= 3:
        await ctx.send(f"🚨 {member.mention} وصل لـ 3 تحذيرات وسيتم سجنه تلقائياً!")
        # سجن تلقائي لمدة 30 دقيقة
        await mute_ar(ctx, member, 30, reason="تخطي عدد التحذيرات المسموح")

@bot.command(name="طرد")
@commands.has_permissions(kick_members=True)
async def kick_ar(ctx, member: discord.Member, *, reason="غير محدد"):
    await member.kick(reason=reason)
    await ctx.send(f'🚫 تم طرد {member.display_name}')

@bot.command(name="بند")
@commands.has_permissions(ban_members=True)
async def ban_ar(ctx, member: discord.Member, *, reason="غير محدد"):
    await member.ban(reason=reason)
    await ctx.send(f'❌ تم حظر {member.display_name}')

# --- 5. قسم الألعاب والمعلومات ---

@bot.command(name="روليت")
async def roulette_ar(ctx):
    res = random.choice(['فزت! 🎉', 'مُت! 💀', 'نجوت! 🔫'])
    await ctx.send(f"**{ctx.author.display_name}** قرر يجرب حظه...\n{res}")

@bot.command(name="لعب")
async def rps_ar(ctx, choice: str):
    opt = ['حجر', 'ورقة', 'مقص']
    bot_c = random.choice(opt)
    if choice not in opt: return await ctx.send("اختار: حجر، ورقة، أو مقص")
    if choice == bot_c: r = "تعادل! 🤝"
    elif (choice=='حجر' and bot_c=='مقص') or (choice=='ورقة' and bot_c=='حجر') or (choice=='مقص' and bot_c=='ورقة'): r = "فزت! 🏆"
    else: r = "خسرت! 😎"
    await ctx.send(f"أنت: {choice} | أنا: {bot_c}\n**{r}**")

@bot.command(name="سيرفر")
async def server_info(ctx):
    embed = discord.Embed(title=f"معلومات {ctx.guild.name}", color=discord.Color.blue())
    embed.add_field(name="الأعضاء", value=ctx.guild.member_count)
    embed.add_field(name="المالك", value=ctx.guild.owner.mention)
    await ctx.send(embed=embed)

# --- 6. قائمة الأوامر ---
@bot.command(name="أوامر")
async def help_ar(ctx):
    embed = discord.Embed(title="📜 قائمة الأوامر الشاملة", color=discord.Color.gold())
    embed.add_field(name="🛡️ الإدارة", value="`!مسح` , `!سجن` , `!تحذير` , `!طرد` , `!بند`", inline=False)
    embed.add_field(name="🎮 الألعاب", value="`!روليت` , `!لعب [حجر/ورقة/مقص]`", inline=False)
    embed.add_field(name="📊 معلومات", value="`!سيرفر`", inline=False)
    await ctx.send(embed=embed)

keep_alive()
bot.run(os.getenv('TOKEN'))
