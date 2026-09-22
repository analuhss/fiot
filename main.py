#================================IMPORT================================#

import discord
from discord import app_commands
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

funciona = os.getenv('funciona')
print(repr(os.getenv('funciona')))

import sqlite3
import time

import easy_pil
from easy_pil import Editor, Font, Canvas
import io

#=========================SQL==========================================#

conn = sqlite3.connect("sistemadexp.db")
cursor = conn.cursor()

#===================PERMISSOES=========================================#

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True

#====================PREFIXO===========================================#

fiot = commands.Bot(command_prefix="!", intents=permissoes)

#======================================================================#

@fiot.event
async def on_ready():
    await fiot.tree.sync()
    print("FIOT FUNCIONANDO")

    # mensagem quando liga
    canalID = 1551757423465996289
    canal = fiot.get_channel(canalID)

    if canal:
        embed = discord.Embed(title="estou funcionando", description="ablublulbulbu")
        embed.color = discord.Color.blue()
        embed.set_image(url="https://i.pinimg.com/736x/d4/0c/80/d40c80d32ad61f5be78b6650753e442c.jpg")
        embed.set_footer(text="imagens reais da nalu fazendo o fiot")

        await canal.send(embed=embed)

fiot.run(funciona)