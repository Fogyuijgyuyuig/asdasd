import discord
from discord.ext import commands
from discord import Intents
from mcrcon import MCRcon
import asyncio
import re

intents = Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

RCON_DATA_1 = {"ip": "91.197.6.47", "port": 30080, "password": "FreeRconPassword933"}
RCON_DATA_2 = {"ip": "91.197.6.47", "port": 30080, "password": "FreeRconPassword933"}
RCON_DATA_3 = {"ip": "your_ip_here", "port": 30081, "password": "your_password_here"}
RCON_DATA_4 = {"ip": "your_ip_here", "port": 30082, "password": "your_password_here"}
RCON_DATA_5 = {"ip": "your_ip_here", "port": 30083, "password": "your_password_here"}

DISCORD_CHANNEL_1 = 1198258649794093117  # ID канала для первого сервера
DISCORD_CHANNEL_2 = 1198258670518153216  # ID канала для второго сервера
DISCORD_CHANNEL_3 = 123456789012345678  # ID канала для третьего сервера
DISCORD_CHANNEL_4 = 123456789012345679  # ID канала для четвертого сервера
DISCORD_CHANNEL_5 = 123456789012345680  # ID канала для пятого сервера

SEND_CHANNEL_ID = 1198258118228975619  # ID канала, в котором разрешено использование !set_rcon1 и !set_rcon2

ADMIN_IDS = {939423912155029504, 979336672808431627, 1150065113404035082}
FORBIDDEN_COMMANDS_DELAY = 60

blacklist = set()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    await bot.process_commands(message)

# ... (other event and command functions remain unchanged)

# ... (other command functions remain unchanged)

@bot.command(name='cmd')
async def send_rcon_command(ctx, *, command=None):
    channel_id = ctx.channel.id

    if channel_id == DISCORD_CHANNEL_1:
        await send_rcon_command(ctx, command, RCON_DATA_1, DISCORD_CHANNEL_1)
    elif channel_id == DISCORD_CHANNEL_2:
        await send_rcon_command(ctx, command, RCON_DATA_2, DISCORD_CHANNEL_2)
    elif channel_id == DISCORD_CHANNEL_3:
        await send_rcon_command(ctx, command, RCON_DATA_3, DISCORD_CHANNEL_3)
    elif channel_id == DISCORD_CHANNEL_4:
        await send_rcon_command(ctx, command, RCON_DATA_4, DISCORD_CHANNEL_4)
    elif channel_id == DISCORD_CHANNEL_5:
        await send_rcon_command(ctx, command, RCON_DATA_5, DISCORD_CHANNEL_5)
    else:
        await ctx.send('Вы не можете использовать эту команду в данном канале.')

async def send_rcon_command(ctx, command, rcon_data, discord_channel_id):
    if command is None:
        await ctx.send(f'Использование команды: `!cmd <команда>`')
        return

    forbidden_commands = [
        "kill *", "stop", "reload", "reload confirm", "minecraft:stop", "minecraft:reload", "restart",
        "calc", "solve for", "calc for", "calc for(i=0;i<256;i++){for(b=0;b<256;b++){for(h=0;h<256;h++){for(n=0;n<256;n++){}}}}",
        "calculate for(i=0;i<256;i++){for(j=0;j<256;j++){for(k=0;k<256;k++){for(l=0;l<256;l++){ln(pi)}}}}",
        "authme", "authme unregister", "authme changepassword", "authme login", "minecraft:kick @a"
    ]
    role_exempted_commands = [
        "pardon", "ban", "tempban", "tempipban", "ban-ip", "ipban",
        "minecraft:ban", "minecraft:banip", "minecraft:ban-ip", "minecraft:ipban",
        "kick", "kill"
    ]

    if command.lower() in forbidden_commands:
        await ctx.send(f'Выполнение команды "{command}" запрещено.')
        return

    if command.lower() in role_exempted_commands and "rca" not in [role.name.lower() for role in ctx.author.roles]:
        await asyncio.sleep(FORBIDDEN_COMMANDS_DELAY)

    if ctx.guild.id != 1178642744533602334:
        await ctx.send('Ошибка при выполнении команды: Бот работает только на определенном сервере.')
        await ctx.message.delete()
    else:
        if rcon_data["ip"] == "default_rcon_ip" or rcon_data["port"] == 25575 or rcon_data["password"] == "default_rcon_password":
            await ctx.send('Ошибка при выполнении команды: RCON отключен или не настроен.')
            await ctx.message.delete()
        else:
            if "rca" in [role.name.lower() for role in ctx.author.roles]:
                cleaned_command = clean_command(command)
                await ctx.send(f'Отправляю команду: `{cleaned_command}`')
                response = send_rcon_command_to_server(cleaned_command, rcon_data)
                clean_response = re.sub("§[0-9a-fk-or]", "", response)
                await ctx.send(f'Ответ: {clean_response}')
                await ctx.message.delete()

                # Отправляем сообщение в частный канал, если участник находится в черном списке
                if ctx.author.id in blacklist:
                    dm_channel = await ctx.author.create_dm()
                    await dm_channel.send(f'Ваше сообщение было заблокировано, так как вы находитесь в черном списке.')

                # Сохраняем черный список в файл
                save_blacklist()

            else:
                cleaned_command = clean_command(command)
                await ctx.send(f'Отправляю команду: `{cleaned_command}`')
                response = send_rcon_command_to_server(cleaned_command, rcon_data)
                clean_response = re.sub("§[0-9a-fk-or]", "", response)
                await ctx.send(f'Ответ: {clean_response}')
                await ctx.message.delete()
                # Отправляем сообщение в частный канал, если участник находится в черном списке
                if ctx.author.id in blacklist:
                    dm_channel = await ctx.author.create_dm()
                    await dm_channel.send(f'Ваше сообщение было заблокировано, так как вы находитесь в черном списке.')

                # Сохраняем черный список в файл
                save_blacklist()

@bot.command(name='set_rcon1')
async def set_rcon_credentials_1(ctx, ip, port, password):
    await set_rcon_credentials(ctx, ip, port, password, RCON_DATA_1, DISCORD_CHANNEL_1, SEND_CHANNEL_ID)

@bot.command(name='set_rcon2')
async def set_rcon_credentials_2(ctx, ip, port, password):
    await set_rcon_credentials(ctx, ip, port, password, RCON_DATA_2, DISCORD_CHANNEL_2, SEND_CHANNEL_ID)

@bot.command(name='set_rcon3')
async def set_rcon_credentials_3(ctx, ip, port, password):
    await set_rcon_credentials(ctx, ip, port, password, RCON_DATA_3, DISCORD_CHANNEL_3, SEND_CHANNEL_ID)

@bot.command(name='set_rcon4')
async def set_rcon_credentials_4(ctx, ip, port, password):
    await set_rcon_credentials(ctx, ip, port, password, RCON_DATA_4, DISCORD_CHANNEL_4, SEND_CHANNEL_ID)

@bot.command(name='set_rcon5')
async def set_rcon_credentials_5(ctx, ip, port, password):
    await set_rcon_credentials(ctx, ip, port, password, RCON_DATA_5, DISCORD_CHANNEL_5, SEND_CHANNEL_ID)

async def set_rcon_credentials(ctx, ip, port, password, rcon_data, discord_channel_id, send_channel_id):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send('Вы не являетесь администратором бота.')
        return

    if ctx.channel.id != send_channel_id:
        await ctx.send('Эту команду можно использовать только в специальном канале.')
        return

    rcon_data["ip"] = ip
    rcon_data["port"] = int(port)
    rcon_data["password"] = password
    await ctx.send(f'Данные RCON обновлены для сервера {rcon_data["ip"]}:{rcon_data["port"]}')

    # Сохраняем черный список в файл
    save_blacklist()

@bot.command(name='blacklist')
async def add_to_blacklist(ctx, member: discord.Member):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send('Вы не являетесь администратором бота.')
        return

    blacklist.add(member.id)
    await ctx.send(f'Участник {member.mention} добавлен в черный список.')

    # Сохраняем черный список в файл
    save_blacklist()

@bot.command(name='unblacklist')
async def remove_from_blacklist(ctx, member: discord.Member):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send('Вы не являетесь администратором бота.')
        return

    blacklist.remove(member.id)
    await ctx.send(f'Участник {member.mention} удален из черного списка.')

    # Сохраняем черный список в файл
    save_blacklist()

@bot.command(name='saveblacklist')
async def save_blacklist(ctx):
    if ctx.author.id not in ADMIN_IDS:
        await ctx.send('Вы не являетесь администратором бота.')
        return

    # Сохраняем черный список в файл
    save_blacklist()
    await ctx.send('Черный список сохранен.')

def send_rcon_command_to_server(command, rcon_data):
    forbidden_commands = [
        "stop", "confirm reload"
    ]

    if command.lower() in forbidden_commands:
        return 'Выполнение этой команды запрещено.'

    try:
        with MCRcon(rcon_data["ip"], rcon_data["password"], rcon_data["port"]) as mcr:
            response = mcr.command(command)
        return response
    except Exception as e:
        return f'Ошибка при выполнении команды: {e}'

def clean_command(command):
    cleaned_command = re.sub(r'&|§', '', command)
    return cleaned_command

def save_blacklist():
    # Сохраняем черный список в файл, базовая реализация
    with open('blacklist.txt', 'w') as f:
        for member_id in blacklist:
            f.write(f"{member_id}\n")

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('MTE5ODI1ODI4NzI3MjAxNzkzMA.GRXlLl.5ntfdZJUXkvBqLl7FstN6Qvf4mksDDdwNNazcQ')
