import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# نظام التشغيل 24 ساعة
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive():
    t = Thread(target=run)
    t.start()

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send("Pong! البوت يعمل بنجاح")

keep_alive()
bot.run(os.getenv('TOKEN'))
