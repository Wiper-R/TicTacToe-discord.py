from discord.ext import commands
import asyncio
import discord
import io


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    async def prompt(self, message, *, timeout=60.0, delete_after=True, reacquire=False, author_id=None, clear_reactions_after=False):
        if not self.channel.permissions_for(self.me).add_reactions:
            raise RuntimeError('Bot does not have Add Reactions permission.')

        fmt = f'{message}\n\nReact with \N{WHITE HEAVY CHECK MARK} to confirm or \N{CROSS MARK} to deny.'

        author_id = author_id or self.author.id
        msg = await self.send(fmt)

        confirm = None

        def check(payload):
            nonlocal confirm

            if payload.message_id != msg.id or payload.user_id != author_id:
                return False

            codepoint = str(payload.emoji)

            if codepoint == '\N{WHITE HEAVY CHECK MARK}':
                confirm = True
                return True
            elif codepoint == '\N{CROSS MARK}':
                confirm = False
                return True

            return False

        for emoji in ('\N{WHITE HEAVY CHECK MARK}', '\N{CROSS MARK}'):
            await msg.add_reaction(emoji)

        try:
            await self.bot.wait_for('raw_reaction_add', check=check, timeout=timeout)
        except asyncio.TimeoutError:
            confirm = None

        try:
            if clear_reactions_after and not delete_after:
                await msg.clear_reactions()
            if delete_after:
                await msg.delete()
        finally:
            return confirm
