import discord
from discord.ext import commands
import yaml

with open('config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

token = config['Token']

status = config['Status']

prefix = config['Prefix']

bot = commands.Bot(prefix)


@bot.event
async def on_ready():
    print("Bot is Ready.")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{status}"))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


@bot.command()
async def ping(ctx):
    embed = discord.Embed(
        title=f'{bot.user.name} latency',
        description="Latency",
        color=0x00FFFF)
    embed.add_field(name="🤖BOT Latency",
                    value=f"{str(round(bot.latency * 1000))}ms", inline=False)
    embed.set_footer(
        text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)

initial_extensions = ['cogs.ttt']

for ext in initial_extensions:
    bot.load_extension(ext)


bot.run(token)
