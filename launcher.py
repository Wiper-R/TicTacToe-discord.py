from main import TicTac
import discord
import traceback

bot = TicTac()


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
if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Failed to load extension {extension}.', file=sys.stderr)
            traceback.print_exc()

bot.run()
