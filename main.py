from discord.ext import commands
from alive import keepAlive
from replit import db
import discord
import os

# database
# db['chats'] = {}
# db['connected'] = {}

client = commands.Bot(command_prefix='::', help_command=None)

@client.event
async def on_ready():
  print(client.user)

@client.event
async def on_message(message):
  if str(message.author.id) in db['connected']:
    if db['connected'][str(message.author.id)] != None:
      if not message.content.startswith('::'):
        db['chats'][db['connected'][str(message.author.id)]]['messages'].append({
          'author': str(message.author),
          'message': message.content
        })
  await client.process_commands(message)

@client.command()
async def help(ctx):
  embed = discord.Embed()
  embed.title = 'ChatBot Help'
  embed.description = '''
  ChatBot is a bot that you can use to talk to people across various servers that ChatBot is also added to. To get started, create or join a chat using `::createchat <name>` and `::viewchats`

  **Commands:**
  `::help`: Shows this help command.
  `::connect <chatname>` Connects to chat with specified name.
  `::disconnect <chatname>` Disconnects from chat with specified name.
  `::createchat <name>`: Creates a chat with specified name or password.
  `::deletechat <name>`: Deletes specified chat if you're the owner.
  `::viewchats`: Shows list of avaliable chatrooms.
  `::connected`: Shows which chat you are connected to.
  '''
  embed.color = 0x0a5cff
  await ctx.send(embed=embed)

@client.command()
async def connect(ctx, chatname, password=None):
  if chatname in db['chats']:
    if db['chats'][chatname]['password'] != None:
      if password != None:
        if db['chats'][chatname]['password'] == password:
          await ctx.message.delete()
        else:
          await ctx.send('Incorrect password.')
          return
      else:
        await ctx.send(f'**{chatname}** requires a password.')
        return
    else: pass
    try:
      if db['connected'][str(ctx.message.author.id)] != chatname:
        db['chats'][chatname]['messages'].append({'author': '[Server', 'message': f'{str(ctx.message.author)} has connected.]'})
    except KeyError:
      db['chats'][chatname]['messages'].append({'author': '[Server', 'message': f'{str(ctx.message.author)} has connected.]'})
    db['connected'][str(ctx.message.author.id)] = chatname
    items = []
    messages = db['chats'][chatname]['messages']
    for i in range(10):
      try:
        message = messages[len(messages)-(i+1)]
        if not (len(messages)-(i+1)) < 0:
          items.append(f'{message["author"].split("#")[0]}: {message["message"]}')
      except IndexError:
        pass
    await ctx.send(f'You are now connected to **{chatname}**```ini\n'+'\n'.join(items[::-1])+'```')
  else:
    await ctx.send('Chat does not exist.')

@client.command()
async def disconnect(ctx):
  if str(ctx.message.author.id) in db['connected']:
    if db['connected'][str(ctx.message.author.id)] != None:
      db['chats'][db['connected'][str(ctx.message.author.id)]]['messages'].append({'author': '[Server', 'message': f'{str(ctx.message.author)} has disconnected.]'})
      await ctx.send(f'Disconnected from **{db["connected"][str(ctx.message.author.id)]}**!')
      db['connected'][str(ctx.message.author.id)] = None
    else:
      await ctx.send('You are not connected to a chat.')
  else:
    await ctx.send('You are not connected to a chat.')

@client.command()
async def createchat(ctx, chatname, password=None):
  if len(chatname) > 20:
    await ctx.send('Chat name must be less than 20 character.')
  elif chatname in db['chats']:
    await ctx.send('There is already another chat with that name.')
  else:
    chats = 0
    for item in db['chats']:
      if db['chats'][item]['owner'] == str(ctx.message.author): chats += 1
    if chats == 5:
      await ctx.send(f'You can only create 5 chats.')
    else:
      db['chats'][chatname] = {
        'owner': str(ctx.message.author),
        'messages': [],
        'password': password
      }
      await ctx.send(f'Chat **{chatname}** created!')

@client.command()
async def deletechat(ctx, chatname):
  if chatname in db['chats']:
    if db['chats'][chatname]['owner'] == str(ctx.message.author) or str(ctx.message.author) == 'walker#1693':
      del db['chats'][chatname]
      for user in db['connected']:
        if db['connected'][user] == chatname:
          db['connected'][user] = None
      await ctx.send(f'Deleted **{chatname}**!')
    else:
      await ctx.send('You do not own this chat.')
  else:
    await ctx.send('Chat does not exist.')

@client.command()
async def viewchats(ctx):
  embed = discord.Embed()
  embed.color = 0x0a5cff
  embed.title = 'Chatrooms'
  if db['chats'] == {}:
    embed.description = '```None```'
  else:
    items = []
    for item in db['chats']:
      locked = '🔒' if db['chats'][item]['password'] != None else ''
      items.append(f'{item}{" "*(20-len(item))}| {db["chats"][item]["owner"]} {locked}')
    embed.description = '```'+'\n'.join(items)+'```'
  await ctx.send(embed=embed)

@client.command()
async def connected(ctx):
  if str(ctx.message.author.id) in db['connected']:
    await ctx.send(f'You are connected to **{db["connected"][str(ctx.message.author.id)]}**!')
  else:
    await ctx.send('You are not connected to a chat.')

keepAlive()
client.run(os.environ['TOKEN'])
