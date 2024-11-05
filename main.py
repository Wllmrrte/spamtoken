import asyncio
import os
import sys
import requests
from bs4 import BeautifulSoup
from pystyle import *
from telethon import TelegramClient, events

# Configuración del cliente de Telegram
API_ID = '9161657'
API_HASH = '400dafb52292ea01a8cf1e5c1756a96a'
PHONE_NUMBER = '+51981119038'
session_name = 'mi_sesion_token'

# URL del token que necesitas acceder
URL_TOKEN = 'http://161.132.49.242:1241/token/private/31317876'

# Inicializar cliente de Telegram
client = TelegramClient(session_name, API_ID, API_HASH)

# Lista de usuarios autorizados para consultar el token
USUARIOS_AUTORIZADOS = ['ABUS1VEDD', 'Asteriscom', 'usuario3']  # Agrega más usuarios aquí

def banner():
    cls()
    Write.Print("Choose an option...", Colors.dark_green, interval=0)

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def pause():
    os.system("pause>null" if os.name == "nt" else "read -n1 -r -p 'Press any key to continue...'")

async def obtener_datos_token():
    """Extrae el usuario, contraseña y token del HTML."""
    try:
        response = requests.get(URL_TOKEN)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraemos los valores de cada campo
            usuario = soup.find(text="Usuario:").find_next('input')['value']
            password = soup.find(text="Contraseña:").find_next('input')['value']
            token = soup.find(text="Token:").find_next('input')['value']

            return usuario, password, token
        else:
            return None, None, None
    except Exception as e:
        print(f"Error al obtener el token: {str(e)}")
        return None, None, None

@client.on(events.NewMessage(pattern='/token'))
async def enviar_token(event):
    """Envía el token únicamente a usuarios autorizados."""
    sender = await event.get_sender()
    username = sender.username

    if username in USUARIOS_AUTORIZADOS:
        usuario, password, token = await obtener_datos_token()

        if usuario and password and token:
            chat_id = event.chat_id
            await client.send_message(chat_id, usuario)
            await asyncio.sleep(2)
            await client.send_message(chat_id, password)
            await asyncio.sleep(2)
            await client.send_message(chat_id, token)
        else:
            await client.send_message(event.chat_id, "❌ Error al obtener los datos del token.")
    else:
        await client.send_message(event.chat_id, "❌ No estás autorizado para usar este comando.")

async def send_messages_to_groups(client, source_group_name, excluded_group_names):
    """Envía mensajes desde el grupo fuente a otros grupos, excluyendo algunos, con intervalos definidos."""
    group_ids = []
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.name != source_group_name and dialog.name not in excluded_group_names:
            group_ids.append(dialog.id)

    # Obtener hasta 10 mensajes del grupo fuente
    source_group = None
    async for dialog in client.iter_dialogs():
        if dialog.is_group and dialog.name == source_group_name:
            source_group = dialog.id
            break

    if source_group is None:
        Write.Print(f"\nGrupo '{source_group_name}' no encontrado. Verifique el nombre.", Colors.red, interval=0)
        return

    messages = []
    async for message in client.iter_messages(source_group, limit=10):
        if message.text:
            messages.append(message)

    if not messages:
        Write.Print("\nNo se encontraron mensajes en el grupo fuente.", Colors.red, interval=0)
        return

    # Enviar mensajes de forma intercalada a cada grupo con las pausas indicadas
    message_index = 0
    while True:
        current_message = messages[message_index]
        for group_id in group_ids:
            try:
                await client.forward_messages(group_id, messages=[current_message])
                Write.Print(f"\nMensaje reenviado a {group_id}", Colors.green, interval=0)
                await asyncio.sleep(4)  # Espera de 4 segundos entre envíos a cada grupo
            except Exception as e:
                Write.Print(f"\nError al reenviar al grupo {group_id}: {str(e)}", Colors.red, interval=0)
        Write.Print(f"\nEsperando 3000 segundos antes de enviar el siguiente mensaje desde {source_group_name}", Colors.orange, interval=0)
        await asyncio.sleep(3000)

        # Avanzar al siguiente mensaje o reiniciar el ciclo de mensajes
        message_index = (message_index + 1) % len(messages)

async def main():
    cls()
    banner()
    option = Write.Input("\n[~] r00t > ", Colors.dark_green, interval=0)
    if option == '1':
        cls()
        Write.Print("Escribe los nombres de los grupos a excluir (separados por comas)", Colors.dark_green, interval=0)
        excluded_group_names_input = Write.Input("[~] r00t > ", Colors.dark_green, interval=0)

        excluded_group_names = [group.strip() for group in excluded_group_names_input.split(",")]

        await client.start(PHONE_NUMBER)
        Write.Print("Bot iniciado. Esperando mensajes o ejecutando reenvío...", Colors.green, interval=0)
        
        # Iniciar la tarea de reenvío de mensajes a grupos
        await send_messages_to_groups(client, "spambotasteriscom", excluded_group_names)

        # Ejecuta el cliente hasta que se desconecte
        await client.run_until_disconnected()

    elif option == '2':
        cls()
        sys.exit()
    else:
        Write.Print("Elige una opción válida", Colors.orange, interval=0)
        pause()
        banner()

with client:
    client.loop.run_until_complete(main())
