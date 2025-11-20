import discord
import random
from os import getenv
from dotenv import load_dotenv
from cons.gifts import *
from cons.phra import *
from cons.videos import *
from discord.ext import commands
from deepseek import DeepSeekAPI
import asyncio

load_dotenv()

global mensaje_evento_id
mensaje_evento_id = None  # ID del mensaje del evento

discordToken = getenv("DISCORD_TOKEN")

# Intents necesarios
intents = discord.Intents.default()
intents.members = True  # Necesario para detectar nuevos miembros
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

# Cliente de DeepSeek (usa DEEPSEEK_API_KEY si está en env)
deepseek_api_key = getenv("DEEPSEEK_API_KEY")
if deepseek_api_key:
    deepseek_client = DeepSeekAPI(deepseek_api_key)
else:
    deepseek_client = DeepSeekAPI()  # intenta leer de env por defecto

@client.event
async def on_ready():
    print(f'✅ Bot conectado como {client.user}')

@client.command()
async def chat(ctx, *, mensaje):
    await ctx.send("💬 **Pensando...**")

    if deepseek_client is None:
        await ctx.send("❌ No se encontró la variable de entorno `DEEPSEEK_API_KEY`. Añádela y reinicia el bot.")
        return

    try:
        # Ejecutar la llamada a la librería de DeepSeek en un thread para no bloquear el event loop
        response = await asyncio.to_thread(deepseek_client.chat_completion, mensaje)

        # Extraer texto de la respuesta (según formato que devuelva la SDK)
        texto = ""
        try:
            # si la respuesta tiene estructura estilo choices -> message -> content
            texto = response["choices"][0]["message"]["content"]
        except Exception:
            # fallback: convertir a string
            texto = str(response)

        await ctx.send(texto)

    except Exception as e:
        await ctx.send(f"❌ Ocurrió un error al conectarse con DeepSeek: {e}")
        return

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

    # El bloque de detección/solución de imágenes (OpenAI) fue eliminado por petición.

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

    # (El resto de comandos como !integracion, !sustitucion, etc. se mantienen igual)
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

    # ... (resto de comandos sin cambios) ...
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
