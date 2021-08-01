import random
from typing import Union, Dict
import discord
import model
import re
import yaml
from template_parser import flat_list, CategoryTemplate

model.Base.metadata.create_all(model.engine)

with open('config.yml') as file:
    config = yaml.safe_load(file)

with open('template.yml') as file:
    template = yaml.safe_load(file)

channel_templates: Dict[str, CategoryTemplate] = {}

for key in template:
    channel_templates[key] = CategoryTemplate(template[key])

client = discord.Client()

def param_parser(string)-> Union[str,None]:
    if re.compile("HELP$", re.I).search(string):
        return "HELP"
    for key in channel_templates:
        reg_list = [key] + channel_templates[key].alias
        for r in reg_list:
            reg = re.compile(r + '$', re.I)  # 大文字小文字の区別を無効
            if reg.search(string):
                return key

    return None

async def send_help_message(channel):
    message = ''
    for key in channel_templates:
        if key == "default": continue
        option = channel_templates[key]
        message += f'{key}:\n'
        message += '    '
        for p in flat_list(option.alias):
            message += f'{p}  '
        message += f'\n    {option.description}'
        message += '\n\n'
    return await channel.send(f'オプションヘルプを表示します。\n{message}', delete_after=30)

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if not message.role_mentions:
        return

    if not str(message.channel.id) == model.get_recuit(str(message.guild.id)).channel_id:
        return

    option = param_parser(message.content)
    if option == 'HELP':
        return await send_help_message(message.channel)

    if option is None or option not in channel_templates:
        option = "default"
        
    template = channel_templates[option]

    (category, channels) = await template.create_category(message.guild, message.role_mentions)

    model.add_category(str(category.id))

    resp_message = config["create_room_message"].format(channels[0].mention)
    if option != "default":
        resp_message += f'({option})'

    await message.channel.send(resp_message, delete_after=30)
    await check(message.guild, category)

@client.event
async def on_ready():
    print("On ready...")

@client.event
async def on_voice_state_update(member, before, after):
    # 移動前がNoneなら返す
    if before.channel is None:
        return

    # カテゴリのないボイチャなら返す
    ctgr = before.channel.category
    if ctgr is None:
        return

    # 移動前のチャンネルに人がいたら返す
    if before.channel.members:
        return

    # このBotが作成したカテゴリなら削除
    db_ids = [category.category_id for category in model.get_categories()]
    if str(ctgr.id) in db_ids:
        await delete_channel(ctgr)


async def delete_channel(ctgr):
    for channel in ctgr.channels:
        await channel.delete()
    ctgr_id = ctgr.id
    await ctgr.delete()
    model.delete_category(str(ctgr_id))


async def check(guild, ex_ctgr):
    for ctgr in guild.categories:
        if ctgr == ex_ctgr:
            continue
        db_ids = [category.category_id for category in model.get_categories()]
        if str(ctgr.id) in db_ids:
            for vc in ctgr.voice_channels:
                if not vc.members:
                    await delete_channel(ctgr)


@client.event
async def on_guild_join(guild):
    # 募集部屋がなければ募集部屋作成
    recuit_ch = model.get_recuit(str(guild.id))
    if recuit_ch is None:
        ctgr = await guild.create_category(config.get('recuitment_category'))
        tx_ch = await ctgr.create_text_channel(name=config.get('recuitment_room'))

        model.add_recuit(str(guild.id), str(tx_ch.id))
    else:
        ch = guild.get_channel(int(recuit_ch.channel_id))
        if ch is None:
            ctgr = await guild.create_category(config.get('recuitment_category'))
            tx_ch = await ctgr.create_text_channel(name=config.get('recuitment_room'))

            model.change_recuit(str(guild.id), str(tx_ch.id))

client.run(config.get("discord_token"))
