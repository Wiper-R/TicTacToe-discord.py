"""A Tic Tac Toe Command works on latest discord.py."""

import asyncio
import random
import discord
from discord.ext import commands
import yaml


with open('config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)


class TicTacToe:
    # Emotes Section
    white_page: str = config['white_page']
    X_Emoji: str = config['X_Emoji']
    O_Emoji: str = config['O_Emoji']

    top_left: str = config['top_left'].lower()
    top: str = config['top'].lower()
    top_right: str = config['top_right'].lower()
    left: str = config['left'].lower()
    mid: str = config['mid'].lower()
    right: str = config['right'].lower()
    bottom_left: str = config['bottom_left'].lower()
    bottom: str = config['bottom'].lower()
    bottom_right: str = config['bottom_right'].lower()

    # Generates A embed for Tic Tac Toe Game
    @staticmethod
    def get_ttt_embed(player1, player2, data, move_of, final=False, tie=False):
        embed = discord.Embed(title=f"Match of {player1} vs {player2}")
        embed.colour = move_of.colour if not final else player1.colour if move_of == player2 else player2.colour
        data_ = data.copy()
        for i in range(1, 10):
            if data[i] == 0:
                data_[i] = TicTacToe.white_page
            elif data[i] == 1:
                data_[i] = TicTacToe.X_Emoji
            elif data[i] == 2:
                data_[i] = TicTacToe.O_Emoji
        description = (
            f"{data_[1]}{data_[2]}{data_[3]}\n"
            f"{data_[4]}{data_[5]}{data_[6]}\n"
            f"{data_[7]}{data_[8]}{data_[9]}")
        if tie:
            description += f'\nMatch Draw!'
        elif not final:
            description += f'\n\n{move_of.name}\'s Turn'
            description += ' **(X)**' if move_of == player1 else ' **(O)**'
        else:
            if move_of == player1:
                description += f'\n\n{player2.name}#{player2.discriminator} is Winner.'
            else:
                description += f'\n\n{player1.name}#{player1.discriminator} is Winner.'

        embed.description = description
        return embed

    # Declares Winner if no one is winner, it Returns False
    @staticmethod
    def declare_winner(data):
        game = []
        for i in [1, 4, 7]:
            row = []
            for j in range(i, i + 3):
                row.append(data[j])
            game.append(row)

        def declare(game_1):
            # horizontal
            for row_1 in game_1:
                if row_1.count(row_1[0]) == len(row_1) and row_1[0] != 0:
                    return row_1[0]
            # vertical
            for col in range(len(game[0])):
                check = []
                for row_2 in game:
                    check.append(row_2[col])
                if check.count(check[0]) == len(check) and check[0] != 0:
                    return check[0]

            # / diagonal
            diagonals = []
            for idx, reverse_idx in enumerate(reversed(range(len(game)))):
                diagonals.append(game[idx][reverse_idx])

            if diagonals.count(diagonals[0]) == len(diagonals) and diagonals[0] != 0:
                return diagonals[0]

            # \ diagonal
            diagonals_reverse = []
            for ix in range(len(game)):
                diagonals_reverse.append(game[ix][ix])

            if diagonals_reverse.count(diagonals_reverse[0]) == len(diagonals_reverse) and diagonals_reverse[0] != 0:
                return diagonals_reverse[0]
            return None

        winner = declare(game)
        return winner


class TicTacToeBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage='[Member]')
    async def ttt(self, ctx, member: discord.Member):
        """A tic tac toe command with reactions. When you will use your move the reaction will be removed.
        Invite your friend to play.."""
        try:
            # Exceptions
            if member.bot:
                await ctx.send('You can\'t play with bots now.')
                return
            if member == ctx.author:
                await ctx.send("You can't play with yourself.")
                return

            message = await ctx.send(f"{member.mention} {ctx.author} wants to play 'Tic Tac Toe' with You. Accept/Deny by reacting on below buttons.")

            for r in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
                await message.add_reaction(r)
            # Wait for Confirmation..
            confirmation = None

            def check(payload):
                nonlocal confirmation
                if payload.message_id != message.id or payload.user_id != member.id:
                    return False

                codeblock = str(payload.emoji)

                if codeblock not in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
                    return False

                if codeblock == '\N{WHITE HEAVY CHECK MARK}':
                    confirmation = True
                    return True

                elif codeblock == '\N{CROSS MARK}':
                    confirmation = False
                    return True

            try:
                await self.bot.wait_for('raw_reaction_add', timeout=60, check=check)
            except asyncio.TimeoutError:
                confirmation = None

            if confirmation is None:
                return await ctx.send(f"{member} failed to accept your tic tac toe game challenge.")

            elif confirmation is False:
                return await ctx.send(f"{member} declined your tic tac toe game challenge.")

            # Choice of First Turn
            players_ = [ctx.author, member]
            player1, player1_move = random.choice(players_), 1
            player2, player2_move = players_[0] if players_.index(
                player1) == 1 else players_[1], 2
            data = {}
            for i in range(1, 10):
                data[i] = 0

            # Remaining Moves Dictionary
            remaining_moves = {
                TicTacToe.top_left: 1, TicTacToe.top: 2, TicTacToe.top_right: 3,
                TicTacToe.left: 4, TicTacToe.mid: 5, TicTacToe.right: 6,
                TicTacToe.bottom_left: 7, TicTacToe.bottom: 8, TicTacToe.bottom_right: 9
            }

            move_of, move_name = player1, player1_move
            initial_embed = TicTacToe.get_ttt_embed(
                player1, player2, data, move_of)
            initial_embed = await ctx.send(embed=initial_embed)

            # Add Emotes To Message (initial_embed)
            for emoji in remaining_moves.keys():
                await initial_embed.add_reaction(emoji)
            while True:

                # A Check to take in moves..
                def check(reaction_, user):
                    return user.id == move_of.id and initial_embed.id == reaction_.message.id

                # Wait for Reaction
                try:
                    reaction = await self.bot.wait_for('reaction_add', check=check, timeout=30)
                except asyncio.TimeoutError:
                    await ctx.send('Timed Out..{} failed to use moves.'.format(move_of.mention))
                    return

                # Converted Emoji Object to '<:UpLeftArrow:710733351991902258>'
                str_reaction = str(reaction[0])
                if str_reaction in remaining_moves.keys():
                    data[remaining_moves[str_reaction]] = move_name

                # Swap Turn
                move_of, move_name = (player1, player1_move) if move_of == player2 else (
                    player2, player2_move)

                # Generates Embed
                new_embed = TicTacToe.get_ttt_embed(
                    player1, player2, data, move_of)

                # Removes current reaction from remaining moves dictionary.
                del remaining_moves[str_reaction]
                await initial_embed.edit(embed=new_embed)
                # Declaration of winner (Returns None if no one is Winner)
                winner = TicTacToe.declare_winner(data)
                if winner is None:
                    # If moves still remaining
                    if len(remaining_moves.keys()) != 0:
                        await initial_embed.clear_reaction(str_reaction)
                    # Else Generates a Tie Embed
                    else:
                        await initial_embed.clear_reaction(str_reaction)
                        new_embed = TicTacToe.get_ttt_embed(
                            player1, player2, data, move_of, tie=True)
                        await initial_embed.edit(embed=new_embed)
                        await ctx.send('Match Draw!')
                        return
                else:
                    # Generates a winner Embed
                    new_embed = TicTacToe.get_ttt_embed(
                        player1, player2, data, move_of, final=True)
                    await initial_embed.edit(embed=new_embed)
                    if winner == 1:
                        await ctx.send(f'{player1.mention} is Winner.')
                    else:
                        await ctx.send(f'{player2.mention} is Winner.')
                    await initial_embed.clear_reactions()
                    return
        except discord.NotFound:
            return


def setup(bot):
    bot.add_cog(TicTacToeBot(bot))
