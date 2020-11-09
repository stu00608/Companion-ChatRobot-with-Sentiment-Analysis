import discord
from discord.ext import commands
from core.classes import Cog_Extension

class main(Cog_Extension) :

    @commands.command()
    async def ping(self, ctx) : # 在 Discord 裡可輸入的指令 => T!ping
        # ctx => 使 bot 知道要在哪個使用者、ID、伺服器、頻道回覆訊息
        await ctx.send(f'延遲 {round(self.bot.latency * 1000)} 毫秒') # 送出延遲時間
        
    '''
    @commands.command()
    async def clean(self, ctx, num : int) :
        await ctx.channel.purge(limit = num)'''


def setup(bot) : # 當運行 bot.py 時就會呼叫 setup
    bot.add_cog(main(bot))