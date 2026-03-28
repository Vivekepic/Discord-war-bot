import discord
from discord.ext import commands
import os
import random
import geopandas as gpd
import matplotlib.pyplot as plt

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

countries = {}
alliances = {}
daily_claimed = set()

# 🗺️ Generate real map
def generate_map():
    world = gpd.read_file("ne_110m_admin_0_countries.shp")
    world["color"] = "white"

    for country_name, data in countries.items():
        world.loc[world["NAME"] == country_name, "color"] = data["color"]

    fig, ax = plt.subplots(figsize=(12, 6))
    world.plot(color=world["color"], edgecolor="black", ax=ax)

    plt.axis("off")
    plt.savefig("map.png", bbox_inches="tight")
    plt.close()

# 🎮 Create country
@bot.command()
async def create(ctx, country_name: str, color: str):
    if ctx.author.id in countries:
        await ctx.send("You already own a country!")
        return

    countries[country_name] = {
        "owner": ctx.author.id,
        "color": color,
        "money": 1000,
        "gdp": 100,
        "troops": 50,
        "alliance": None
    }

    await ctx.send(f"{country_name} created with color {color}!")

# 💰 Daily income
@bot.command()
async def daily(ctx):
    user_country = None

    for name, data in countries.items():
        if data["owner"] == ctx.author.id:
            user_country = data
            break

    if not user_country:
        await ctx.send("You don't own a country!")
        return

    if ctx.author.id in daily_claimed:
        await ctx.send("You already claimed today!")
        return

    income = user_country["gdp"] - 10  # maintenance
    user_country["money"] += income
    daily_claimed.add(ctx.author.id)

    await ctx.send(f"You earned {income}! Total money: {user_country['money']}")

# 🪖 Buy troops
@bot.command()
async def buy_troops(ctx, amount: int):
    for name, data in countries.items():
        if data["owner"] == ctx.author.id:
            cost = amount * 5
            if data["money"] >= cost:
                data["money"] -= cost
                data["troops"] += amount
                await ctx.send(f"Bought {amount} troops!")
            else:
                await ctx.send("Not enough money!")
            return

# ⚔️ Declare war
@bot.command()
async def war(ctx, target: discord.Member):
    attacker = None
    defender = None

    for name, data in countries.items():
        if data["owner"] == ctx.author.id:
            attacker = data
        if data["owner"] == target.id:
            defender = data

    if not attacker or not defender:
        await ctx.send("Both players need countries!")
        return

    if attacker["alliance"] and attacker["alliance"] == defender["alliance"]:
        await ctx.send("You can't attack alliance members!")
        return

    if attacker["troops"] > defender["troops"]:
        attacker["troops"] -= 10
        defender["troops"] = max(0, defender["troops"] - 20)
        await ctx.send("You are winning the war!")
    else:
        attacker["troops"] = max(0, attacker["troops"] - 20)
        await ctx.send("You are losing!")

# 🤝 Alliance system
pending_alliances = {}

@bot.command()
async def ally(ctx, target: discord.Member):
    pending_alliances[target.id] = ctx.author.id
    await ctx.send(f"{target.mention}, type !accept to form alliance!")

@bot.command()
async def accept(ctx):
    if ctx.author.id not in pending_alliances:
        await ctx.send("No pending alliance!")
        return

    requester_id = pending_alliances.pop(ctx.author.id)

    alliance_id = random.randint(1000, 9999)

    for data in countries.values():
        if data["owner"] == requester_id or data["owner"] == ctx.author.id:
            data["alliance"] = alliance_id

    await ctx.send("Alliance formed!")

# 🗺️ Show map
@bot.command()
async def map(ctx):
    generate_map()
    await ctx.send(file=discord.File("map.png"))

bot.run(os.getenv("MTQ4NzEwMTkwMTc0NDExNTg1Mg.GCHg_n.GT_GVe-U2jtl00TeMByuaNNDO6q3Z9ekNTKuWs"))