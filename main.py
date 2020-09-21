import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
import asyncio
import datetime
import os
import time
import traceback
import sys
import yaml
from cogs.utils import context

with open ('config.yaml') as config_file:
    config = yaml.load(config_file, Loader=yaml.FullLoader)

token = config['Token']

status = config['Status']

prefix = config['Prefix']

class TicTac(commands.Bot):
    def __init__(self):
        self.token = token
        super().__init__(command_prefix=prefix)

    async def on_ready(self):
        print("Bot is Ready.")
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=f"{status}"))


    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return
        raise error
    
    async def get_context(self, *, cls=context.Context):
        super().get_context(cls=cls)

    def run(self):
        super().run(self.token, reconnect=True)
