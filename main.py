import discord
import random
from os import getenv
from dotenv import load_dotenv
from cons.gifts import *
from cons.phra import *
from cons.videos import *   
from discord.ext import commands
from openai import OpenAI

load_dotenv()

global mensaje_evento_id
mensaje_evento_id = None  # ID del mensaje del evento

discordToken = getenv("DISCORD_TOKEN")
chatgptToken = getenv("OPENAI_API_KEY")

# Intents necesarios
intents = discord.Intents.default()
intents.members = True  # Necesario para detectar nuevos miembros
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Cliente del bot


# --- Inicializar OpenAI ---
openai_client = OpenAI(api_key=chatgptToken)

@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}')

@client.command()
async def chat(ctx, *, mensaje):
    await ctx.send("💬 **Pensando...**")

    respuesta = openai_client.responses.create(
        model="gpt-4o-mini",
        input=mensaje
    )

    texto = respuesta.output_text

    await ctx.send(texto)

@client.event
async def on_member_join(member):
    # ID del canal donde quieres enviar la bienvenida
    canal_id = 1440543212967301151

    canal_bienvenida = client.get_channel(canal_id)

    # Si no encuentra el canal, evita error
    if canal_bienvenida is None:
        print("⚠ ERROR: No se encontró el canal de bienvenida o el bot no tiene permisos.")
        return

    # Primer mensaje
    await canal_bienvenida.send(
        f'👋 ¡Bienvenido/a al servidor, {member.mention}! Esperamos que disfrutes tu estadía 🎉\n'
        f'Si quieres saber mis funciones, escribe `opciones`.'
    )

    # Segundo mensaje con GIF
    mensaje = (
        f'✨ ¡Bienvenido {member.mention} a **{member.guild.name}**!\n'
        f'Por favor revisa las reglas para evitar conflictos 🙌'
    )

    gif_aleatorio = random.choice(math_gifs)

    embed = discord.Embed(description=mensaje, color=0x00ffcc)
    embed.set_image(url=gif_aleatorio)

    await canal_bienvenida.send(embed=embed)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.attachments and not message.author.bot:

        imagen_url = message.attachments[0].url

        # Guardamos la imagen en memoria del bot
        if not hasattr(client, "ultima_imagen"):
            client.ultima_imagen = {}

        client.ultima_imagen[message.author.id] = imagen_url

        await message.channel.send(
            "📸 He detectado una imagen. ¿Quieres que te dé la solución?"
        )
        return

    # --- BLOQUE PARA RESPONDER "sí" ---
    if message.content.lower() in ["si", "sí", "dale", "ok"]:

        if hasattr(client, "ultima_imagen") and message.author.id in client.ultima_imagen:

            imagen_url = client.ultima_imagen[message.author.id]

            # Llamada a ChatGPT visión
            respuesta = openai_client.responses.create(
            model="gpt-4o-mini",
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Resuelve esta imagen paso a paso:"
                        },
                        {
                            "type": "input_image",
                            "image_url": imagen_url
                        }
                    ]
                }
            ]
        )

        texto = respuesta.output_text
        await message.channel.send(texto)
        return

            # Limpiar imagen usada
        del client.ultima_imagen[message.author.id]
        return

    
    if message.content.lower() == "!ayuda":
         await message.channel.send("📩 Para enviar un problema al servidor que no entiendes en anonimo, escríbeme por **mensaje directo** así:\n`!ayuda necesito que alguien me ayude en esta integral`")
    
    if isinstance(message.channel, discord.DMChannel):
        if (message.content.lower().startswith("!ayuda")):
            # Extraemos el texto sin el comando
            texto_confesion = message.content[len("!ayuda"):].strip()

            if not texto_confesion:
                await message.channel.send("✏️ Escribe algo después de `!ayuda` para enviarlo.")
                return

            # ID del canal de confesiones (cambia esto por el ID real)
            canal_id = 1431371973153521799  # Reemplaza con el ID de tu canal #confesiones

            canal = client.get_channel(canal_id)

            if canal:
                embed = discord.Embed(
                    title="📢 Nueva ayuda anónima",
                    description=texto_confesion,
                    color=0xffc0cb
                )
                await canal.send(embed=embed)
                await message.channel.send("✅ ¡Tu confesión se ha enviado de forma anónima!")
            else:
                await message.channel.send("❌ No se encontró el canal de confesiones.")
        return  

    if message.content.lower() == '!video_curioso':
        random_video = random.choice(videos)
        await message.channel.send(f'🎬 Aquí tienes un video: {random_video}')

    if message.content.lower() == '!evento':
        embed = discord.Embed(
            title="🎨 ¡Evento matematico del Mes!",
            description=(
                "🗓️ **Tema:** Métodos de Integración — Creatividad y precisión en el cálculo.\n"
                "📅 **Inicio:** 15 de noviembre\n"
                "🕒 **Plazo:** 30 de noviembre\n\n"
                "📌 **Reglas:**\n"
                "- El trabajo debe ser original y propio (no copiado de internet).\n"
                "- Puedes usar notación matemática clara (LaTeX, foto de cuaderno).\n"
                "- Se puede participar individualmente o en equipo (máximo 3 personas).\n"
                "- Cada participante puede enviar hasta 3 integrales diferentes..\n"
                "- Respeta el formato de entrega:.\n"
                "- 📂 Publica en el canal #eventos-matemáticos.\n"
                "- Incluye el hashtag #MaestrosDeLaIntegración.\n"
                "- Añade tu método: “por partes”, “sustitución trigonométrica”, etc..\n"
                "- Los ganadores se eligen por:.\n"
                "- Exactitud (40%)n.\n"
                "- Claridad en la explicación (30%).\n"
                "- Creatividad en la presentación (30%).\n"
                "🎁 **Premio:** Se le dara su buena apreciativa a su nota 🎉\n\n"
                "✅ **¿Quieres participar? Reacciona a este mensaje con ✅**\n"           
            ),
            color=0x6e00ff
        )
        embed.set_thumbnail(url="https://media.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif")

        mensaje_evento = await message.channel.send(embed=embed)
        await mensaje_evento.add_reaction("✅")

        # Guarda el ID del mensaje para manejar las reacciones
        global mensaje_evento_id
        mensaje_evento_id = mensaje_evento.id

     
    if message.content.lower() == '!integracion':
        img = random.choice(integracion_por_partes)
        await message.channel.send(f'🎯 **integral propuesta:**\n{img}')

    if message.content.lower() == "!formula_partes":
        imagen_url = "https://media.discordapp.net/attachments/1401037204213727283/1440184816149467156/image.png?ex=691d3c21&is=691beaa1&hm=a9e7c2f620de4bc6a0f361678cf86887bdfa95fe79b8ff76ae864826c48f9779&=&format=webp&quality=lossless"

        embed = discord.Embed(
            title="📘 Fórmula del Método de integracion por partes",
            description="Aquí tienes la fórmula general del método de integracion por partes:",
            color=0x00b7ff
        )
        embed.set_image(url=imagen_url)

        await message.channel.send(embed=embed)
        return

    if message.content.lower() == '!sustitucion':
        img = random.choice(metodo_de_sustitucion)
        await message.channel.send(f'🎯 **integral propuesta:**\n{img}')

    # ---------------- COMANDO: !formula_sustitucion ----------------
    if message.content.lower() == "!formula_sustitucion":
        imagen_url = "https://media.discordapp.net/attachments/1401037204213727283/1440178407328583700/image.png?ex=691d3629&is=691be4a9&hm=8527d2d0c0e1e56da977e0776143c1a6170669bc0fab365b079437fbaf8a55a7&=&format=webp&quality=lossless"

        embed = discord.Embed(
            title="📘 Fórmula del Método de Sustitución",
            description="Aquí tienes la fórmula general del método de sustitución:",
            color=0x00b7ff
        )
        embed.set_image(url=imagen_url)

        await message.channel.send(embed=embed)
        return

    if message.content.lower() == '!trigonometrica':
        img = random.choice(sustitucion_trigonometrica)
        await message.channel.send(f'🎯 **integral propuesta:**\n{img}')

    if message.content.lower() == "!formula_integrales_trigonometricas":

        imagen1 = "https://media.discordapp.net/attachments/1401037204213727283/1440186897061253153/image.png?ex=691d3e11&is=691bec91&hm=963180d33b7644f414408cc2db46ac89668d759090c96838bdabb0e0db0764d8&=&format=webp&quality=lossless"
        imagen2 = "https://media.discordapp.net/attachments/1401037204213727283/1440186973418422283/image.png?ex=691d3e23&is=691beca3&hm=f68ea57ee0ee1f243bc0cd711e9328db16890d2115793908c47e18c9bdbb2b2d&=&format=webp&quality=lossless"
        imagen3 = "https://media.discordapp.net/attachments/1401037204213727283/1440194421860864113/image.png?ex=691d4513&is=691bf393&hm=fdc9450879874dbff62109887fe8d96e18f3d404a40ab95f53ab8ce8c4a9df43&=&format=webp&quality=lossless"
        
        # Primer embed
        embed1 = discord.Embed(
            title="📘 Fórmulas de integrales trigonométricas (Parte 1)",
            description="Primera parte de las fórmulas:",
            color=0x00b7ff
        )
        embed1.set_image(url=imagen1)

        # Segundo embed
        embed2 = discord.Embed(
            title="📘 Fórmulas de integrales trigonométricas (Parte 2)",
            description="Segunda parte de las fórmulas:",
            color=0x00b7ff
        )
        embed2.set_image(url=imagen2)

        # tercer embed
        embed3 = discord.Embed(
            title="📘 Fórmulas de integrales trigonométricas (Parte 3)",
            description="tercera parte de las fórmulas:",
            color=0x00b7ff
        )
        embed3.set_image(url=imagen3)

        # Enviar ambos
        await message.channel.send(embed=embed1)
        await message.channel.send(embed=embed2)
        await message.channel.send(embed=embed3)
        return

    if message.content.lower() == "!formula_sustitucion_trigonometrica":
        imagen_url = "https://media.discordapp.net/attachments/1401037204213727283/1440196301735067722/image.png?ex=691d46d3&is=691bf553&hm=4d5f7aafeb188f0cd83f503f7da39c4e1b3cfda0ff3175bc3b2bc1deb7537089&=&format=webp&quality=lossless"

        embed = discord.Embed(
            title="📘 Fórmulas del Método de Sustitución trigonometrica",
            description="Aquí tienes las fórmulas en general del método de sustitución trigonometrica:",
            color=0x00b7ff
        )
        embed.set_image(url=imagen_url)

        await message.channel.send(embed=embed)
        return

    if message.content.lower() == '!parciales':
        img = random.choice(fracciones_parciales)
        await message.channel.send(f'🎯 **integral propuesta:**\n{img}')

    if message.content.lower() == "!casos_fracciones_parciales":

        imagen4 = "https://media.discordapp.net/attachments/1401037204213727283/1440198673740070952/image.png?ex=691d4909&is=691bf789&hm=082d1d7f5830c0d09ef67a9bf4f866b84b19208664f1f02a515c44554fc551d0&=&format=webp&quality=lossless"
        imagen5 = "https://media.discordapp.net/attachments/1401037204213727283/1440199288767385702/image.png?ex=691d499c&is=691bf81c&hm=63a6bd5f2b381c2674eb19460e8dde37c9125ca330496157c6cedbae0bdbf975&=&format=webp&quality=lossless"
        imagen6 = "https://media.discordapp.net/attachments/1401037204213727283/1440199484339519578/image.png?ex=691d49ca&is=691bf84a&hm=f11f36441700245947c02d37cd885b60d99e077cd88fb800638c4f3c2061ed81&=&format=webp&quality=lossless"
        
        # Primer embed
        embed4 = discord.Embed(
            title="📘 Caso 1 de fracciones parciales",
            description="Primera parte de fracciones parciales:",
            color=0x00b7ff
        )
        embed4.set_image(url=imagen4)

        # Segundo embed
        embed5 = discord.Embed(
            title="📘 Caso 2 de fracciones parciales",
            description="Segunda parte de fracciones parciales:",
            color=0x00b7ff
        )
        embed5.set_image(url=imagen5)

        # tercer embed
        embed6 = discord.Embed(
            title="📘 Caso 3 de fracciones parciales",
            description="tercera parte de fracciones parciales:",
            color=0x00b7ff
        )
        embed6.set_image(url=imagen6)

        # Enviar ambos
        await message.channel.send(embed=embed4)
        await message.channel.send(embed=embed5)
        await message.channel.send(embed=embed6)
        return

    if message.content.lower() == '!estrategias':
        img = random.choice(estrategias_integracion)
        await message.channel.send(f'🎯 **integral propuesta:**\n{img}')
    
    if message.content.lower() == "!formulas_integrales":
        imagen_url = "https://media.discordapp.net/attachments/1401037204213727283/1440203715079442452/image.png?ex=691d4dbb&is=691bfc3b&hm=16166c06276edb00223c3e68818b604294c51e6867b84fc14983077e7155c407&=&format=webp&quality=lossless"

        embed = discord.Embed(
            title="📘 tabla de Fórmulas de integracion ",
            description="Aquí tienes las fórmulas en general de las método de las integrales:",
            color=0x00b7ff
        )
        embed.set_image(url=imagen_url)

        await message.channel.send(embed=embed)
        return

    if message.content.lower() == '!reto':
        reto = random.choice(retos)
        await message.channel.send(f'🎯 **Reto matematico:**\n{reto}')

    # Mensaje de introducción
    if message.content.lower().startswith("funciones"):
        await message.channel.send(
            "👋 ¡Hola! A continuación encontrarás algunas funciones que puedo hacer.\n"
            "Escribe `opciones` para ver el menú."
        )

    # Mostrar opciones disponibles
    elif message.content.lower().startswith("opciones"):
        await message.channel.send(
            "**📋 Opciones disponibles:**\n"
            "1. `!integracion` → te dare al azar algunas integrales por partes 🗣️\n"
            "2. `!formula_partes` → te dare la formula de las integraciones por partes 🗣️\n"
            "3. `!sustitucion` → te dare al azar algunas integrales por sustitucion🗣️\n"
            "4. `!formula_sustitucion` → te dare la formula de las integraciones por sustitucion 🗣️\n"
            "5. `!trigonometrica` → te dare al azar algunas integrales trigonometricas 🗣️\n"
            "6. `!formula_integrales_trigonometricas` → te dare las formulas de las integrales trigonometricas  🗣️\n"
            "7. `!formula_sustitucion_trigonometrica` → te dare las formulas de las integrales de sustitucion trigonometricas 🗣️\n"
            "8. `!parciales` → te dare al azar algunas fracciones parciales 🗣️\n"
            "9. `!casos_fracciones_parciales` → Te dare los 3 casos de las fracciones parciales 🗣️\n"
            "10. `!estrategias` → te dare al azar algunas estrategias de integrales 🗣️\n"
            "11. `!formulas_integrales` → Te dare la tabla de las integrales 🗣️\n"
            "12. `!video_curioso` → Video relacionado con las matematicas, quizas te pueda interesar 📹\n"
            "13. `!reto` → te dara un reto, para que pongas a prueba tus capacidades matematicas 😎\n"
            "14. `!ayuda` → busca ayuda en los demas, si tiedes problemas para resolver tus integrales! 🤐\n"
            "15 `!chat` → Pide ayuda o si tienes alguna duda a mi atraves de este comando, yo te ayudare! 👏🏼\n"
        )   
    await client.process_commands(message)
   
@client.event
async def on_raw_reaction_add(payload):
    global mensaje_evento_id
    if payload.message_id != mensaje_evento_id:
        return

    if str(payload.emoji) == "✅": 
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if member and not member.bot:
            channel = guild.get_channel(payload.channel_id)
            await channel.send(f"🙌 {member.mention} se ha unido al evento matematico. ¡Buena suerte!")

client.run(discordToken)