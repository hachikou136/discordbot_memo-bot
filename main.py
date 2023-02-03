import sqlite3
import discord
import os
import subprocess
from keep_alive import keep_alive
import random

Intents = discord.Intents.default()
Intents.message_content = True
client = discord.Client(intents=Intents)


@client.event
async def on_ready():
  print('Logged in as')
  print(client.user.name)
  print(client.user.id)
  print('------')
  # await client.change_presence(
  #   game=discord.Game(name="!m?|discha.net", url="https://discha.net"))


@client.event
async def on_server_join(server):
  return


@client.event
# async def on_message(message):
#   # print('printf0')
#   if not message.content.startswith('!'): return
#   if not message.content.startswith('!m'): return
#   if message.content.startswith('!mlist'):
#     # print('printf1')
#     return await memo_list(message)
#   if message.content.startswith('!madd '):
#     return await memo_add(message)
#   if message.content.startswith('!mrm '):
#     return await memo_rm(message)
#   if message.content.startswith('!m '):
#     return await memo_show(message)
#   if message.content.startswith('!m?') or message.content.startswith('!memo'):
#     return await memo_man(message)
async def on_message(message):
  # print('printf0')
  # print(message.content)
  # if not message.content.startswith('!'): return
  # if not message.content.startswith('!m'): return
  if message.content.startswith('!mlist'):
    # print('printf1')
    return await memo_list(message)
  if message.content.startswith('!madd '):
    return await memo_add(message)
  if message.content.startswith('!mrm '):
    return await memo_rm(message)
  if message.content.startswith('!m '):
    return await memo_show(message)
  if message.content.startswith('はき！ '):
    const_message = 'はき！ パワー！'
    if not message.content.startswith(const_message):
      return await memo_show(message)
    one_or_two = random.randint(1, 2)
    if one_or_two == 1:
      return await text_show(message, 'ヤー！！')
    return await text_show(message, '💪')
  if message.content.startswith('!m?') or message.content.startswith('!memo'):
    return await memo_man(message)


# CREATE TABLE memo(user_id integer, user_name string, memo_title string, memo_content string);
# create index memo_user_id_index on memo(user_id);
if os.environ['IS_INITIALISED_SQLITEDB3'] == "False":
  print('=== Start initializing database. ===')
  print(
    '=== You can prevent initializind database file by change secret to True. ==='
  )
  # create database file memo.db.
  p = subprocess.Popen("touch memo.db", stdout=subprocess.PIPE, shell=True)
  print(p.communicate())
  # create table in memo.db and index in table.
  conn = sqlite3.connect("memo.db")
  conn.execute(
    "CREATE TABLE memo(user_id integer, user_name string, memo_title string, memo_content string)"
  ).fetchone()
  conn.execute("create index memo_user_id_index on memo(user_id)").fetchone()
  # It does not looks working, so you have to set secret by manually:
  # os.environ['IS_INITIALISED_SQLITEDB3'] = "True"


async def memo_man(message):
  # print(message.channel)
  return await message.channel.send("""使えるコマンド:
        メモを出す: !m [タイトル]
        メモを書く: !madd [タイトル] [内容]
        メモを消す: !mrm [タイトル]
        一覧を見る: !mlist
        ヘルプ: !m?
        """)


async def memo_add(message):
  memo_message = message.content.split(" ")
  if len(memo_message) < 3:
    return await message.channel.send(
      "正しく入力してください。\nメモを追加するには\n!madd [タイトル] [内容]")
  memo_content = message.content[message.content.find(' ', 6) + 1:]
  if len(memo_content) > 1000:
    return await message.channel.send("メモが長すぎます。\n登録できる最大文字数は1000文字です。")
  conn = sqlite3.connect("memo.db")
  count = conn.execute("select count(*) from memo WHERE user_id=?",
                       (message.author.id, )).fetchone()
  if count[0] > 1000:
    return await message.channel.send("メモが多すぎます。\n登録できる最大メモ数は1000です。")
  memo = conn.execute("SELECT * FROM memo WHERE user_id=? and memo_title=?",
                      (message.author.id, memo_message[1])).fetchone()
  if memo:
    return await message.channel.send(
      "{0}は {1} にすでにメモを登録しています\n削除するには以下を実行してください。\n!mrm {0}".format(
        message.author.name, memo_message[1]))
  conn.execute(
    "insert into memo values( ?, ?, ?, ? )",
    [message.author.id, message.author.name, memo_message[1], memo_content])
  conn.commit()
  return await message.channel.send("{0}の {1} にメモを登録しました。".format(
    message.author.name, memo_message[1]))


async def memo_list(message):
  memos = sqlite3.connect("memo.db").execute(
    "SELECT * FROM memo WHERE user_id=?", (message.author.id, ))
  return await message.channel.send("{0}のメモ帳に登録されているメモ:\n{1}".format(
    message.author.name, ', '.join([memo[2] for memo in memos])))


async def memo_rm(message):
  memo_message = message.content.split(" ")
  if len(memo_message) < 2:
    return await message.channel.send("正しく入力してください。\nメモを削除するには\n!mrm [タイトル]")
  conn = sqlite3.connect("memo.db")
  memo = conn.execute("SELECT * FROM memo WHERE user_id=? and memo_title=?",
                      (message.author.id, memo_message[1])).fetchone()
  if not memo:
    return await message.channel.send("{0}は {1} にメモを登録していません。".format(
      message.author.name, memo_message[1]))
  conn.execute("delete from memo where user_id=? and memo_title=?",
               (message.author.id, memo_message[1]))
  conn.commit()
  return await message.channel.send("{0}の {1} のメモを削除しました。".format(
    message.author.name, memo_message[1]))


async def memo_show(message):
  memo_message = message.content.split(" ")
  if len(memo_message) != 2:
    return await message.channel.send("正しく入力してください。\nヘルプは\n!memo? [タイトル]")
  memo = sqlite3.connect("memo.db").execute(
    "SELECT * FROM memo WHERE user_id=? and memo_title=?",
    (message.author.id, memo_message[1])).fetchone()
  if not memo:
    return await message.channel.send("{0}は {1} にメモを登録していません。".format(
      message.author.name, memo_message[1]))
  return await message.channel.send(memo[3])


async def text_show(message, text):
  return await message.channel.send(text)


keep_alive()

client.run(os.environ['TOKEN'])
