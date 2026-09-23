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


#============================TABELA=XP=================================#

cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL, 
                usuario TEXT NOT NULL,
                xp INT NOT NULL,
                nivel INT NOT NULL)""")
conn.commit()


#============================COOLDOWNS=================================#

cooldowns = {}
COOLDOWNS_SEGUNDOS = 30
xpImagem = 15

#verificação imagem
def temImagem(message):
    if not message.attachments:
        return False
    
    extensoesImagem = (".png",".jpg", ".jpeg", ".gif", ".webp")

    for anexo in message.attachments:
        if anexo.filename.lower().endswith(extensoesImagem):
            return True
    return False
    
#xp por caractere por
@fiot.event
async def on_message(message):
    if message.author.bot:
        return
    
    nome = str(message.author.display_name)
    userID = str(message.auhtor.id)

    agora = time.time()

    if userID in cooldowns and agora - cooldowns[userID] < COOLDOWNS_SEGUNDOS:
        pass
    else:
        cooldowns[userID] = agora 

    xpGanho = 0

    if temImagem(message):
        xpGanho += xpImagem

    tamanhoMensagem = len(message.content)
    xpGanho += tamanhoMensagem

    if xpGanho == 0:
        await fiot.process_commands(message)

    cursor.execute("""SELECT xp, nivel FROM usuarios
                    WHERE usuario = ?, (userID, )""")
    
    resultado = cursor.fetchone()

    if resultado is None:
        cursor.execute("""INSERT INTO usuarios (nome, usuario, xp, nivel)
                        VALUES (?, ?, ?, ?)""", (nome, userID, xpGanho, 1))
        
    else:
        xpAtual, nivelAtual = resultado
        novoXP = xpAtual + xpGanho
        novoNivel = nivelAtual
        xpNecessario = nivelAtual

        xpNecessario = novoNivel * 100

    while novoXP >= xpNecessario:
        novoXP -= xpNecessario
        novoNivel += 1
        xpNecessario = novoNivel * 100

    cursor.execute("""UPDATE usuarios SET xp = ?, nivel = ?, nome = ?
                    WHERE usuario = ?""", (novoXP, novoNivel, nome, userID))
    
    if novoNivel > nivelAtual:
        
        embed = discord.Embed(title = "SUBIU DE NÍVEL", description = f"infelizmente {message.author.mention}, subiu para o nível **{novoNivel}**")
        
        embed.color = discord.Color.gold()

        embed.set_footer(text="continue conversando para subir de nível")

        await message.channel.send(embed)
    
    conn.commit()