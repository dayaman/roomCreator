import random
import discord
import model
import dsctoken
import re

client = discord.Client()

SPOTS = {
    'WORLDS_EDGE':['試練', 'スカイフック', '調査キャンプ', '製錬所', 'カウントダウン', 'エピセンター', 'フラグメント', '列車庫', '溶岩湖', 'ハーベスター', '仕分け工場', 'ラバシティー', '火力発電所', 'ザ・ツリー', 'ザ・ドーム', '展望', '発射場', '間欠泉'],
    'KINGS_CANYON':['砲台','両椎','ファーム','リレー','湿地','沼沢','ブリッジ','ハイドロダム','リパルサー','リバーズエンド','南監視塔','水処理施設','マーケット','東居住区','南居住区','スカルタウン','サンダードーム','西居住区','ゴールデンサンズ','クロスロード','航空基地','リバーセンター','ハイデザート','バンカー','ランオフ','オアシス','ザ・ピット','スラムレイク','カスケーズ','北監視塔','ザ・ケージ','収容所','丘陵前線基地','サルベージ','キャパシター','マップルーム'],
    'WEAPONS':['フラットライン','G7スカウト','ヘムロック','R-301','ハボック','オルタネーター','プラウラー','R-99','ボルト','ディヴォーション','スピットファイア','L-スター','ロングボウ','クレーバー','トリプルテイク','センチネル','チャージライフル','EVA-8オート','マスティフ','モザンビーク','ピースキーパー','P2020','RE-45','ウィングマン']
}

options = {
        'WORLDS_EDGE':{
            'help':'命名テーブルをWorldsEdge基準に設定',
            'patterns':[r'-w',r'--worlds_edge']
        },
        'KINGS_CANYON':{
            'help':'命名テーブルをKingsCanyon基準に設定',
            'patterns':[r'-k',r'--kings_canyon']
        },
        'WEAPONS':{
            'help':'命名テーブルをWeapons基準に設定',
            'patterns':[r'-p',r'--weapons']
        },
        'HELP':{
            'help':'ヘルプを表示',
            'patterns':[r'-h',r'--help']
        }
    }

def param_parser(string):
    for key in options:
        reg_list = options[key]['patterns']
        for r in reg_list:
            reg = re.compile(r + '$',re.I) # 大文字小文字の区別を無効
            if reg.search(string):
                return key

    return None

async def send_help_message(channel):
    message = ''
    for key in options:
        option = options[key]
        message += f'{key}:\n'
        message += '    '
        for p in option['patterns']:
            message += f'{p}  '
        message += f'\n    {option["help"]}'
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
    
    overwrites = {
        message.guild.default_role: discord.PermissionOverwrite(view_channel=False),
        message.guild.me: discord.PermissionOverwrite(view_channel=True)
    }

    for role in message.role_mentions:
        overwrites[role] = discord.PermissionOverwrite(view_channel=True)

    option = param_parser(message.content)
    if option == 'HELP':
        return await send_help_message(message.channel)

    if option is not None:
        table = SPOTS[option]
    else:
        (key,table) = random.choice(list(SPOTS.items()))


    spot = random.choice(table)

    ctgr = await message.guild.create_category(spot, overwrites=overwrites)
    tx_ch = await ctgr.create_text_channel(name='チャット')
    await ctgr.create_voice_channel(name='わいわい')

    model.add_category(str(ctgr.id))

    resp_message = f'{tx_ch.mention}を作りました。'
    if option is not None:
        resp_message += f'({option})'

    await message.channel.send(resp_message, delete_after=30)
    await check(message.guild, ctgr)

@client.event
async def on_voice_state_update(member, before, after):
    if after.channel is not None:
        return
    if before.channel.members:
        return
    ctgr = before.channel.category

    if ctgr is None:
        return

    db_ids = [ category.category_id for category in model.get_categories()]
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
        db_ids = [ category.category_id for category in model.get_categories()]
        if str(ctgr.id) in db_ids:
            for vc in ctgr.voice_channels:
                if not vc.members:
                    await delete_channel(ctgr)

@client.event
async def on_guild_join(guild):
    # 募集部屋がなければ募集部屋作成
    recuit_ch = model.get_recuit(str(guild.id))
    if recuit_ch is None:
        ctgr = await guild.create_category('room-creator')
        tx_ch = await ctgr.create_text_channel(name='ぼしゅー')

        model.add_recuit(str(guild.id), str(tx_ch.id))
    else:
        ch = guild.get_channel(int(recuit_ch.channel_id))
        if ch is None:
            ctgr = await guild.create_category('room-creator')
            tx_ch = await ctgr.create_text_channel(name='ぼしゅー')

            model.change_recuit(str(guild.id), str(tx_ch.id))

client.run(dsctoken.tkn)