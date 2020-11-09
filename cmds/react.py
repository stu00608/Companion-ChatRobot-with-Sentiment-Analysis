import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json


import random

with open('setting.json', 'r', encoding = 'utf8') as jfile :
    jdata = json.load(jfile)

class react(Cog_Extension) :
    @commands.command()
    async def 他愛看的圖片(self,ctx) :
        random_pic = random.choice(jdata['pic']) 
        pic = discord.File(random_pic) # 連結圖片所在位置
        await ctx.send(file = pic)

    @commands.command()
    async def 我好想你(self,ctx) :
        random_pic = random.choice(jdata['ThisMan']) 
        pic = discord.File(random_pic) # 連結圖片所在位置
        await ctx.send(file = pic)

    @commands.command()
    async def 他愛看的影片(self,ctx) :
        random_video = random.choice(jdata['url_video']) 
        await ctx.send(random_video)

    @commands.command()
    async def Add(self,ctx,word) :


        File = open('word.txt','a',encoding = 'utf8')
        File_ = open('word.txt','r',encoding = 'utf8')
        temp = File_.read().split(',')
        if(word in temp):
            
            await ctx.send("已經存在 "+str(word))
            File.close()
            File_.close()
            return
        File.write(','+str(word))
        File.close()

        await ctx.send("您輸入的是 "+str(word))
        

def setup(bot) : # 當運行 bot.py 時就會呼叫 setup
    bot.add_cog(react(bot))