#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import os
import discord
from discord.ext import commands
import json
import asyncio
import time
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import jieba
import jieba.analyse
import jieba.posseg as pseg
from opencc import OpenCC
import RPi.GPIO as GPIO
import subprocess
import smtplib
import re 
from datetime import datetime as dt
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

cc = OpenCC('tw2sp')

client = language.LanguageServiceClient.from_service_account_json('InterdisciplinaryProject-6851d318d98b.json')

time_per_type = 0.1

cmdchar = 'T!'
bot = commands.Bot(command_prefix = cmdchar) # 命令字首

passList = ['zg','y','e','ul','x','n']

# zg y e e ul y y y zg

responseList = { -9:["冷靜一下，有我在身邊呢。","有我還在，別擔心！","我不希望看到你這樣。","你的生命不再只屬於你自己，而是屬於所有愛你的人！"], #-9
                 -8:["還好嗎...記得讓身邊的人多照顧你。","看到你這樣我也會很傷心的。","抱歉，沒能留下什麼給你。"], #-8
                 -7:["我知道我不在讓你很傷心，但我還能像現在這樣子陪著你的。"], #-7
                 -6:["不妨聽我說個祕密吧，其實我一直都很愛你。","振作點，一切會好起來的。"], #-6
                 -5:["要不要去休息一下呢，有時候睡個覺會讓心情好一點呢。","時間總會過去的，讓時間流走你的煩惱吧！","看你這麼難過，我也很難過，我會陪著你一起走出來。"], #-5
                 -4:["其實我一直都有一些話想跟你說。","你要相信你自己總有一天可以走出來，你不孤單還有我在！"], #-4
                 -3:["如果人生能夠重來，我想我會更珍惜你一些。","雖然我沒辦法真正去體會你正在經歷的，但我會盡我所能去了解你的處境。"], #-3
                 -2:["希望你可以慢慢放下。","你不用自己一個人承擔這些，我會幫你。","沒關係的，我陪你。"], #-2
                 -1:["沒事的，去散散心怎麼樣。","一步一步來，我會一直在你身邊。","跟隨你的內心走吧。","慢慢來，時常保持樂觀。"], #-1
                 0:["恩~","是嗎","是喔","真的啊"], #0
                 1:["我想我會去找些朋友散散心。","你的身邊充滿了值得你開心的人事物，讓我們來一起發掘他們！","不管怎麼樣，過得平順最重要。"], #1
                 2:["但願來世還能夠再相見。","我一直都在。","笑是身體最好的良藥。","多希望我們在一起的時光能繼續下去。"], #2
                 3:["記得照顧好自己的身體。","生活有慢慢好起來了呢"], #3
                 4:["還記得以前我都會吵著要去那裡玩嗎，真想再去一次呢。"], #4
                 5:["看起來你最近過得還不錯呢。","真的嗎!","聽起來很不錯呢。"], #5
                 6:["忽然想到，以前我很喜歡去吃珍寶呢。","我很開心你能跟我分享這麼多事。"], #6
                 7:["看到你過的順遂，我也放心了。","如果我還在你身邊的話，就能跟你一起分享喜悅了。"], #7
                 8:["這能讓我想起以前的那些時光，非常的美好。",""], #8
                 9:["那真是太棒了!","我很開心能夠聽到這個消息。","真的啊!太好了。"], #9
                }

hello_ = ['你好','早','hello','您好','妳好'] #獨立
hello = ['你好','早','hello','您好','妳好',"哈囉","早安",'午安','安安','嗨']
hello_response = ["很高興見到你。","你好。","今天天氣很不錯呢。","見到你很開心。"]

bye = ["掰掰",'掰','再見','明天見','bye','保重','晚安','保重','下次見']
bye_response = ["再見，多注意身體喔。","可以跟你聊天很開心，再見。","記得早一點休息喔。","下次再多聊會吧。","期待我們再一起像這樣聊天。",]

memberID = {}

LED = [7,11,13]
logLED = 13

QAflag = 0

def GPIOsetup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    for pins in LED:
        GPIO.setup(pins,GPIO.OUT)
        GPIO.output(pins,GPIO.LOW)# setup end

def log(msg):
    print(msg)
    try:
        with open("./log/syslog/"+'Syslog_'+dt.now().strftime("%Y%m%d")+".txt","a",encoding='utf8')as File:
            Now = dt.now().strftime("%Y/%m/%d %H:%M:%S")
            File.write(f"[{Now}] ")
            File.write(msg+"\n")
    except:
        return -1
    GPIO.output(logLED,GPIO.LOW)

def readMemberID():
    with open("./member.txt","r",encoding='utf8') as File:
        data = File.readline().strip("\n")
        while(data!=""):
            name,flag=data.split(':')
            memberID[name]=int(flag)
            data = File.readline().strip("\n")

def writeMemberID():
    with open("./member.txt","w",encoding='utf8') as File:
        for name,flag in memberID.items():
            File.write(name+':'+str(flag)+'\n')



# print([len(responseList[i]) for i in range(len(responseList))])   #資料長度



with open('setting.json', 'r', encoding = 'utf8') as jfile :
    jdata = json.load(jfile)

# Linux Version
def writeLog(msg,score,response,time):
    if score<0:
        score_f='_'+str(int(abs(score)))
    else:
        score_f=str(int(score))
    fileID = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ1234567890',6))
    with open("./log/"+score_f+'/'+msg+'.txt','w', encoding = 'utf8') as F:
        F.write("輸入語句 : "+msg+'\n\n')
        F.write("情緒分數 : "+score_f+'\n\n')
        F.write("回覆語句 : "+response+'\n\n')
        F.write("使用時間 : "+str(time)+'\n\n')
        
        F.write("此分數之回覆列表 : \n\n")
        for i in range(len(responseList[int(score)])):
            F.write(responseList[int(score)][i]+'\n')
        F.write("---------------------------\n")
    with open('./log/general.txt','a',encoding='utf8') as F:
        F.write("輸入語句 : "+msg+'\n\n')
        F.write("情緒分數 : "+score_f+'\n\n')
        F.write("回覆語句 : "+response+'\n\n')
        F.write("使用時間 : "+str(time)+'\n\n')
        F.write("此分數之回覆列表 : \n")
        for i in range(len(responseList[int(score)])):
            F.write(responseList[int(score)][i]+'\n')
        F.write("---------------------------\n\n")
        
        
        

    

@bot.event
async def on_ready() :
    GPIOsetup()
    channel = bot.get_channel(int(jdata['Welcome_Channel_ID']))
    #jieba初始化
    log("jieba初始化...")
    jieba.initialize()
    log("讀取成員ID...")
    readMemberID()
    log("推送歡迎訊息...")
    await channel.send('我回來了~')
    log('system setup')
    GPIO.output(LED[0],GPIO.HIGH)

@bot.event
async def on_member_join(member) : # 成員加入
    log(f'{member}歡迎你!') # 在終端機 print 訊息
    channel = bot.get_channel(int(jdata['Welcome_Channel_ID'])) # 抓頻道 ID
    log(f'{member} 簽博囉!')
    await channel.send(f'{member} 歡迎你!') # 在頻道送訊息

@bot.event
async def on_member_remove(member) : # 成員離開
    print(f'{member}再見啦!')
    channel = bot.get_channel(int(jdata['Welcome_Channel_ID']))
    log(f'{member} 再見啦!')
    await channel.send(f'{member} 再見啦!')

@bot.event
# 測試回答內容是否有在list內
# async def on_message(msg) :

#     if(msg.content[0:2]=="T!"):
#         await bot.process_commands(msg) # 與 command 指令會互相衝突
#         return
#     else:
#         if msg.author != bot.user :
#             keyword = readFile()
#             await msg.channel.send(keyword)            
#             for key in keyword :
#                 if key in msg.content:
#                     await msg.channel.send('嗚呼!')
#                     break

async def on_message(msg) :
    
    if msg.author != bot.user :

        
        
        if(str(msg.author) not in memberID):
            memberID[str(msg.author)] = 0

        if(msg.content[0:2]==cmdchar):
            await bot.process_commands(msg) # 與 command 指令會互相衝突
            log(str(msg.author)+' cmd : ' + msg.content)
            return

        log(str(msg.author)+' on_message : ' + msg.content)

        if(msg.content=='是' or msg.content=='否' or msg.content.lower()=='y' or msg.content.lower()=='n'):
            log(" QAflag detect ")
            #await msg.channel.send("菇兔君")
            return
        else:
            #依照情緒分數給予答案
            GPIO.output(LED[1],GPIO.HIGH)
            # words = pseg.cut(cc.convert(msg.content))
            # for w,f in words:
            #     await msg.channel.send("%s  %s"%(w, f))

            # seg_list = jieba.cut(cc.convert(msg.content),HMM=True)
            # await msg.channel.send("Full Mode: " + "/ ".join(seg_list))

            # seg_list = jieba.cut_for_search(cc.convert(msg.content))
            # await msg.channel.send("Search Mode: " + "/ ".join(seg_list))
            
            # data = jieba.analyse.extract_tags(cc.convert(msg.content), topK=20, withWeight=False, allowPOS=())
            # await msg.channel.send(data)
            score=0

            catagory = sentenceCheck(msg.content)
            if(catagory==0):
                memberID[str(msg.author)] = 0
                async with msg.channel.typing():
                    GPIO.output(LED[2],GPIO.HIGH)
                    response = random.sample(bye_response,1)[0]
                    waitTime = (len(response)-response.count("，")) * time_per_type
                    await asyncio.sleep(waitTime)
                    await msg.channel.send(response)
                    log(str(msg.author)+' bye : '+response)
                GPIO.output(LED[2],GPIO.LOW)
            elif(catagory==1):
                memberID[str(msg.author)] = 1
                async with msg.channel.typing():
                    GPIO.output(LED[2],GPIO.HIGH)
                    response = random.sample(hello_response,1)[0]
                    waitTime = (len(response)-response.count("，")) * time_per_type
                    await asyncio.sleep(waitTime)
                    await msg.channel.send(response)
                    log(str(msg.author)+' greet : '+response)
                GPIO.output(LED[2],GPIO.LOW)
            elif(catagory==-1 and memberID[str(msg.author)]==1):
                now_time = time.time()
                async with msg.channel.typing():
                    GPIO.output(LED[2],GPIO.HIGH)
                    document = language.types.Document(
                        content=msg.content,
                        type=enums.Document.Type.PLAIN_TEXT)
                    log("輸入語句 : "+msg.content)
                    log("情緒分析開始")
                    sentiment = client.analyze_sentiment(document=document,encoding_type=enums.EncodingType.UTF8)
                    # score=0
                    for sentence in sentiment.sentences:
                        score = round(sentence.sentiment.score*10,0)
                    log("情緒分析成功")
                    # await msg.channel.send("情緒數值 : "+str(score))
                    log("情緒數值 : "+str(score))
                    

                    response = random.sample(responseList[int(score)],1)[0]
                    waitTime = (len(response)-response.count("，")) * time_per_type

                    use_time = time.time()-now_time

                    # await asyncio.sleep(time)
                    await asyncio.sleep(2)
                    await msg.channel.send(response)
                    log(str(msg.author)+' response : '+ response)
                    writeLog(msg.content,score,response,use_time)

                GPIO.output(LED[2],GPIO.LOW)
                log("輸出完成")
                log('\n')
            GPIO.output(LED[1],GPIO.LOW)
        writeMemberID()
        return

@bot.command()
async def load(ctx, extension) :
    bot.load_extension(f'cmds.{extension}')
    await ctx.send(f'Loaded {extension} done')

@bot.command()
async def unload(ctx, extension) :
    bot.unload_extension(f'cmds.{extension}')
    await ctx.send(f'Unloaded {extension} done')

@bot.command()
async def sentiment(ctx,text):

    document = language.types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    await ctx.send("----Sentiment Analysis Start----")
    sentiment = client.analyze_sentiment(document=document,encoding_type=enums.EncodingType.UTF8)


    for sentence in sentiment.sentences:
        await ctx.send("輸入句子 : "+sentence.text.content)
        await ctx.send("情緒數值 : "+str(round(sentence.sentiment.score,2)))
    await ctx.send("輸入語言 : "+sentiment.language)
    await ctx.send("----Sentiment Analysis Start----")

@bot.command()
async def entities(ctx,text):
    
    document = language.types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    
    await ctx.send("----Entities Analysis Start----")
    entities = client.analyze_entities(document=document,encoding_type=enums.EncodingType.UTF8)

    # Loop through entitites returned from the API
    for entity in entities.entities:

        log(u"Representative name for the entity: {}".format(entity.name))
        await ctx.send(u"Representative name for the entity: {}".format(entity.name))


        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        await ctx.send(u"Entity type: {}".format(enums.Entity.Type(entity.type).name))
        

        # Get the salience score associated with the entity in the [0, 1.0] range
        await ctx.send(u"Salience score: {}".format(entity.salience))
        

        # Loop over the metadata associated with entity. For many known entities,
        # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        for metadata_name, metadata_value in entity.metadata.items():
            await ctx.send(u"{}: {}".format(metadata_name, metadata_value))      

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        for mention in entity.mentions:
            await ctx.send(u"Mention text: {}".format(mention.text.content))
        

            # Get the mention type, e.g. PROPER for proper noun
            await ctx.send(
                u"Mention type: {}".format(enums.EntityMention.Type(mention.type).name)
            )
    await ctx.send("----Entities Analysis End----")


def is_correct(m):
    return m.content=='是'

def mailCheck(mail):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    # pass the regular expression 
    # and the string in search() method 
    if(re.search(regex,mail)):  
        return 1
    else:  
        return 0 

@bot.command()
async def scan(ctx):
    ps = subprocess.Popen(['iwgetid'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    wifi_name = subprocess.check_output(['grep','ESSID'],stdin=ps.stdout)
    wifi_name = wifi_name.decode(encoding='ascii')
    wifi_name = wifi_name[wifi_name.find(":")+1:]
    await ctx.send(f"目前連接網路名稱 : {wifi_name}")


@bot.command()
async def sys(ctx,option):
    for pins in LED:
        GPIO.output(pins,GPIO.HIGH)
    if(option=='shutdown'):
        await ctx.send("將在5秒後關機...")
        log("將在5秒後關機...")
        await asyncio.sleep(5)
        await ctx.send("再見! 下次再繼續聊天吧。")
        log("system shutdown")
        await asyncio.sleep(1)
        subprocess.Popen(['sudo','shutdown','-h','now'])
    elif(option=='reboot'):
        await ctx.send("將在5秒後重新開機...")
        log("將在5秒後重新開機...")
        await asyncio.sleep(5)
        await ctx.send("等等再繼續聊天吧。")
        log("system reboot")
        await asyncio.sleep(1)
        subprocess.Popen(['sudo','reboot'])    
    
    GPIO.output(LED[1],GPIO.LOW)
    GPIO.output(LED[2],GPIO.LOW)
    GPIO.output(LED[0],GPIO.HIGH)
    return

@bot.command()
async def maillog(ctx,mail,date):

    if(not mailCheck(mail)):
        await ctx.send("電子郵件格式錯誤，請重新執行")
        log("invalid mail format")
        return
    
    try:
        today = dt.strptime(date, "%Y%m%d").strftime("%Y%m%d")
    except:
        await ctx.send("日期格式有誤，請重新執行")
        log("invalid date format")
        return

    for pins in LED:
        GPIO.output(pins,GPIO.HIGH)


    try:

        
        #Email Variables
        SMTP_SERVER = 'smtp.gmail.com' #Email Server (don't change!)
        SMTP_PORT = 587 #Server Port (don't change!)
        GMAIL_USERNAME = 'nicebrotheritachi@gmail.com' #change this to match your gmail account
        GMAIL_PASSWORD = 'cilabe520'  #change this to match your gmail password

        


        emailSubject = "SystemLog_"+today
        emailContent = "This is a test of my Emailer Class"


        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = GMAIL_USERNAME
        message['To'] = mail
        message['Subject'] = emailSubject
        #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(emailContent, 'plain'))
        attach_file_name = './log/syslog/Syslog_'+today+".txt"
        try: 
            attach_file = open(attach_file_name, 'rb') # Open the file as binary mode
        except:
            await ctx.send("沒有該日期之紀錄")
            log("invalid log file")
            return
        payload = MIMEBase('application', 'octate-stream')
        payload.set_payload((attach_file).read())
        encoders.encode_base64(payload) #encode the attachment
        #add payload header with filename
        payload.add_header('Content-Decomposition', 'attachment', filename=attach_file_name)
        message.attach(payload)
        #Create SMTP session for sending the mail
        session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT) #use gmail with port
        session.starttls() #enable security
        session.login(GMAIL_USERNAME, GMAIL_PASSWORD) #login with mail_id and password
        text = message.as_string()
        session.sendmail(GMAIL_USERNAME, mail, text)
        session.quit()
        log("log file send")
        await ctx.send("記錄檔已傳送")
    except:
        await ctx.send("傳送錯誤，請重新執行")
    
    await asyncio.sleep(1)
    
    GPIO.output(LED[1],GPIO.LOW)
    GPIO.output(LED[2],GPIO.LOW)
    GPIO.output(LED[0],GPIO.HIGH)
    return


# keywordScoreInput
# @bot.command()
# async def a(ctx,text,score):

#     await ctx.send("輸入語句："+text)
#     await ctx.send("輸入評分："+score)
#     await ctx.send("確定寫入資料嗎(y/n)")
#     def is_correct(m):
#         return m.content.isalpha()
#     ans = await bot.wait_for('message', check=is_correct)
#     ans = ans.content
#     if(ans.lower()=='y'):
#         await ctx.send("寫入資料...")
#         fileID = ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMOPQRSTUVWXYZ1234567890',6))
#         File = open("C:\\Users\\USER\\Desktop\\dataset\\"+str(score)+"\\"+"Sentence"+fileID+".txt","w")
#         File.write(text)
#         File.close()
#         await ctx.send("寫入完成!")
#     elif(ans.lower()=='n'):
#         await ctx.send("取消寫入")
#         return
#     else:
#         await ctx.send("輸入錯誤，請重新執行")
#         return


# #keywordScoreInput
# @bot.command()
# async def b(ctx,text):
#     await ctx.send("輸入語句："+text)
#     await ctx.send("確定寫入資料嗎(y/n)")
#     def is_correct(m):
#         return m.content.isalpha()
#     ans = await bot.wait_for('message', check=is_correct)
#     ans = ans.content
#     if(ans.lower()=='y'):
#         await ctx.send("寫入資料...")
#         File = open("C:\\Users\\USER\\Desktop\\dataset\\buf\\NonLabeledSentence.txt","a")
#         File.write(text+'\n')
#         File.close()
#         await ctx.send("寫入完成!")
#     elif(ans.lower()=='n'):
#         await ctx.send("取消寫入")
#         return
#     else:
#         await ctx.send("輸入錯誤，請重新執行")
#         return

#---------------------------------------------Function-----------------------------------------------#

def sentenceCheck(text):
    # 1打招呼 0道別 -1都不是
    text+="。"
    for item in hello:
        if item in text:
            if(text==item):
                return 1
            if(item=='妳好' or item=='你好' or item=='您好'):
                words = pseg.cut(text)
                flag=0
                for word,tag in words:
                    # print(word,tag)
                    if(flag):
                        if(tag in passList):
                            return 1
                        else:
                            return -1
                    elif word in hello:
                        #第三次檢測
                        flag = 1                     
                return -1
            else:
                return 1
    
    for item in bye:
        if item in text:
            return 0
    
    return -1
    
#----------------------------------------------------------------------------------------------------#

# 也可用 import 導入
# 但是檔案多時太麻煩了
for filename in os.listdir('./cmds') : # 列出 cmds 資料夾中所有的文件
    if filename.endswith('py') : # 結尾是否為 py 的文件
        bot.load_extension(f'cmds.{filename[:-3]}') # 導入文件 


if __name__ == "__main__":
    bot.run(jdata['TOKEN'])


