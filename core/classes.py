# 存放屬性的定義
# 供其他檔繼承
# 避免每次新增檔案都要重新定義

import discord
from discord.ext import commands

class Cog_Extension(commands.Cog) :
    def __init__(self,bot) :
        self.bot = bot