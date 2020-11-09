# Imports the Google Cloud client library
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

# Instantiates a client
# client = language.LanguageServiceClient()

import discord
from discord.ext import commands
from core.classes import Cog_Extension
import json


import random

with open('setting.json', 'r', encoding = 'utf8') as jfile :
    jdata = json.load(jfile)


client = language.LanguageServiceClient.from_service_account_json('InterdisciplinaryProject-6851d318d98b.json')

@commands.command()
async def sentiment(ctx,text):

    document = language.types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    
    sentiment = client.analyze_sentiment(document=document,encoding_type=enums.EncodingType.UTF8)


    for sentence in sentiment.sentences:
        await ctx.channel.send("輸入句子 : "+sentence.text.content)
        await ctx.channel.send("情緒數值 : "+str(round(sentence.sentiment.score,2)))
    await ctx.channel.send("輸入語言 : "+sentiment.language)


def entities_detection(text,ctx):

    document = language.types.Document(
        content=text,
        type=enums.Document.Type.PLAIN_TEXT)
    
    entities = client.analyze_entities(document=document,encoding_type=enums.EncodingType.UTF8)

    result = [][]

    # Loop through entitites returned from the API
    i=0
    for entity in entities.entities:

        print(u"Representative name for the entity: {}".format(entity.name))

        # Get entity type, e.g. PERSON, LOCATION, ADDRESS, NUMBER, et al
        print(u"Entity type: {}".format(enums.Entity.Type(entity.type).name))

        # Get the salience score associated with the entity in the [0, 1.0] range
        print(u"Salience score: {}".format(entity.salience))

        # Loop over the metadata associated with entity. For many known entities,
        # the metadata is a Wikipedia URL (wikipedia_url) and Knowledge Graph MID (mid).
        # Some entity types may have additional metadata, e.g. ADDRESS entities
        # may have metadata for the address street_name, postal_code, et al.
        for metadata_name, metadata_value in entity.metadata.items():
            print(u"{}: {}".format(metadata_name, metadata_value))

        # Loop over the mentions of this entity in the input document.
        # The API currently supports proper noun mentions.
        for mention in entity.mentions:
            print(u"Mention text: {}".format(mention.text.content))

            # Get the mention type, e.g. PROPER for proper noun
            print(
                u"Mention type: {}".format(enums.EntityMention.Type(mention.type).name)
            )

