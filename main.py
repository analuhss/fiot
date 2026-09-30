#================================IMPORT================================#

import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('tokenfiot')
if not TOKEN:
    raise RuntimeError("Token não encontrado. Verifique a variável 'tokenfiot' no arquivo .env")

import sqlite3
import time
import io

from easy_pil import Editor, Font, Canvas

#=========================SQL==========================================#

conn = sqlite3.connect("sistemadexp.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                usuario TEXT NOT NULL UNIQUE,
                xp INT NOT NULL,
                nivel INT NOT NULL)""")
conn.commit()

#===================PERMISSOES=========================================#

permissoes = discord.Intents.default()
permissoes.message_content = True
permissoes.members = True

#====================BOT===============================================#

class Fiot(commands.Bot):
    async def setup_hook(self):
        await self.tree.sync()

fiot = Fiot(command_prefix="!", intents=permissoes)

ja_avisou = False 
@fiot.event
async def on_ready():
    global ja_avisou
    print("FIOT FUNCIONANDO")

    if ja_avisou:
        return
    ja_avisou = True

    canalID = 1551757423465996289
    canal = fiot.get_channel(canalID)

    if canal:
        embed = discord.Embed(title="estou funcionando", description="ablublulbulbu")
        embed.color = discord.Color.blue()
        embed.set_image(url="https://i.pinimg.com/736x/d4/0c/80/d40c80d32ad61f5be78b6650753e442c.jpg")
        embed.set_footer(text="imagens reais da nalu fazendo o fiot")

        await canal.send(embed=embed)

#============================COOLDOWNS=================================#

cooldowns = {}
COOLDOWNS_SEGUNDOS = 30
xpImagem = 15

# verificação imagem
def temImagem(message):
    if not message.attachments:
        return False

    extensoesImagem = (".png", ".jpg", ".jpeg", ".gif", ".webp")

    for anexo in message.attachments:
        if anexo.filename.lower().endswith(extensoesImagem):
            return True
    return False

#============================XP========================================#

#cooldown:
cooldowns = {}
COOLDOWN_SEGUNDOS = 30
xpImagem = 15

# verifica se tem imagem (que tambem contam como xp):
def temImagem(message):
    if not message.attachments:
        return False
    extensoesImangem = (".png", ".jpg", ".jpeg", ".gif", ".webp")

    for anexo in message.attachments:
        if anexo.filename.lower().endswith(extensoesImangem):
            return True
    return False

# xp por caractere de mensagem:
@fiot.event
async def on_message(message):
    if message.author.bot:
        return

#   dados do author:
    nome = str(message.author.display_name)
    userID = str(message.author.id)

    agora = time.time()

# calculo de cooldown:
    if userID in cooldowns and agora - cooldowns[userID] < COOLDOWN_SEGUNDOS:
        pass
    else:

#   atualiza o tempo do cooldown:
        cooldowns[userID] = agora

# calculo xp:
        xpGanho = 0

# adição de xp das
        if temImagem(message): 
# é o mesmo que escrever:
#       resultado = temImagem(message)
#       if resultado == True:
    
            xpGanho += xpImagem
# é o mesmo que escrever:
#       xpGanho = xpGanho + xpImagem

# xp baseado no tamanho da mensagem:
        tamanhoMensagem = len(message.content)
        xpGanho += tamanhoMensagem

# return de segurança:
        if xpGanho == 0:
            await fiot.process_commands(message)
            return

        cursor.execute("""SELECT xp, nivel FROM usuarios
                    WHERE usuario = ?""",
                    (userID, )) 
#               "?" = placeholder de busca objetiva(nesse caso, o ID do usuário)

        resultado = cursor.fetchone() # traz o resultado para o código

#       se o usuário ainda não esta registrado no banco:
        if resultado is None:
            cursor.execute("""INSERT INTO usuarios (nome, usuario, xp, nivel)
                            VALUES (?, ?, ?, ?)""",
                            (nome, userID, xpGanho, 1))

#       se o usuário já estiver no banco:
        else:
            xpAtual, nivelAtual = resultado
            novoXP = xpAtual + xpGanho
            novoNivel = nivelAtual

            xpNecessario = novoNivel * 100

#           cálculo de nível:
            while novoXP >= xpNecessario:
                novoXP -= xpNecessario
                novoNivel += 1
                xpNecessario = novoNivel * 100

#           atualiza os dados do banco:
            cursor.execute("""UPDATE usuarios SET xp = ?, nivel = ?, nome = ?
                            WHERE usuario = ? """,
                        (novoXP, novoNivel, nome, userID))

        conn.commit()

    await fiot.process_commands(message)


    if novoNivel > nivelAtual:
        embed = discord.Embed(
            title="SUBIU DE NÍVEL",
            description=f"infelizmente {message.author.mention}, subiu para o nível **{novoNivel}**"
        )
        embed.color = discord.Color.gold()
        embed.set_footer(text="continue conversando para subir de nível")

        await message.channel.send(embed=embed)

#============================CARD======================================#

@fiot.tree.command(name="nivel", description="mostra seu nível atual e xp")
async def nivel(interact: discord.Interaction):

    userID = str(interact.user.id)

    cursor.execute("SELECT xp, nivel FROM usuarios WHERE usuario = ?", (userID,))
    resultado = cursor.fetchone()

    # se o usuário ainda não está no banco:
    if resultado is None:
        embed = discord.Embed(title="Nunca te vi por aqui", description="Por isso, você ainda não tem xp")
        embed.color = discord.Color.light_grey()
        embed.set_footer(text="comece a mandar mensagens para obter xp :)")

        await interact.response.send_message(embed=embed, ephemeral=True)
        return

    # se o usuário está no banco:
    xpAtual, nivelAtual = resultado
    xpProximoNivel = nivelAtual * 100
    porcentagem = min((xpAtual / xpProximoNivel) * 100, 100)

    # gerar a imagem pode demorar mais de 3s; "defer" evita o erro de interação expirada
    await interact.response.defer()

    # fundo do card:
    bg = Canvas((800, 200), color="#363636")
    editor = Editor(bg)

    # foto do usuário:
    avatarBytes = await interact.user.display_avatar.read()
    perfil = Editor(io.BytesIO(avatarBytes)).resize((160, 160)).circle_image()
    editor.paste(perfil, (30, 200 // 2 - 80))

    # fontes:
    fonteNome = Font.poppins(size=40, variant="bold")
    fonteNivel = Font.poppins(size=30)
    fonteXp = Font.poppins(size=24, variant="bold")

    # nome do usuário:
    editor.text((220, 40), interact.user.display_name, color="white", font=fonteNome)

    # nível:
    editor.text((650, 20), f"NV. {nivelAtual}", color="white", font=fonteNivel)

    # xp:
    editor.text((650, 58), f"{xpAtual} / {xpProximoNivel}", color="white", font=fonteXp)

    # contorno da barra de xp
    editor.rectangle((220, 107), width=561, height=54, outline="white", radius=15)

    # preenchimento da barra de xp
    editor.bar(
        (220, 107),
        max_width=562,
        height=55,
        percentage=porcentagem,
        color="green",
        radius=15
    )

    # card pronto:
    file = discord.File(fp=editor.image_bytes, filename="nivel.png")

    embed = discord.Embed(title=f"NÍVEL DE {interact.user.display_name}")
    embed.set_image(url="attachment://nivel.png")

    # cor da embed personalizada:
    embed.color = interact.user.color if interact.user.color != discord.Color.default() else discord.Color.light_grey()

    await interact.followup.send(embed=embed, file=file)

#======================================================================#

@fiot.command()
async def nalu(ctx: commands.Context):
    embed = discord.Embed(
        title="Quem é nalu?",
        description="Bom...\nA nalu é a criadora de todos os multiversos presentes na terra. Ela não apenas dita as regras do espaço-tempo, como cada decisão exala +100.000.00aura.\nEnquanto meros mortais tentam entender a física quântica, a NALU molda realidades paralelas antes de abrir os olhos."
    )

    embed.set_image(url="https://i.pinimg.com/736x/3c/a5/eb/3ca5ebdcc3a159df3bb1378eac2471a3.jpg")

    await ctx.reply(embed=embed)

#======================================================================#

fiot.run(TOKEN)