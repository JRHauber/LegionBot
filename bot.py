import discord
from discord.ext import commands
from discord.utils import get
import random
import math
from resource_requests import Request
import pickle

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents=intents)

try:
    resource_requests = pickle.load(open("requests.p", "rb"))
except FileNotFoundError:
    resource_requests = []

profession_roles = {
    'foraging': 1267585190981796021,
    'hunting': 1267585359986823168,
    'mining': 1267585386859728927,
    'carpentry': 1267585436885323817,
    'cooking': 1267585479616893052,
    'leatherworking': 1267585503385882665,
    'masonry': 1267585535858315306,
    'smithing': 1267585569442238556,
    'tailoring': 1267585594750402581,
    'scholar': 1267585753496551627,
    'farming': 1267585784404377763,
    'fishing': 1267585808186081311,
    'forestry': 1267585920773918752
}

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    


@bot.command()
async def request(ctx, role= "foraging", *, message="Test Message"):
        id = math.ceil(random.random() * 1000)
        if id not in resource_requests:
            sent = await ctx.send(f"""
                    {get(ctx.guild.roles, id=profession_roles[role.lower()]).mention}
                    Requester: {ctx.author.mention}
                    Message: {message}
                    ID: {id}
                    """)
            r = Request(int(id), ctx.author.display_name, ctx.author.mention, ctx.author.id, 'Unclaimed', '', 0, message, sent.id)
            print(r.rname)
            resource_requests.append(r)
            print(resource_requests)
            pickle.dump( resource_requests, open("requests.p", "wb"))
            await ctx.message.delete()

@bot.command()
async def claim(ctx, id= -1):
    for i in range(len(resource_requests)):
        if resource_requests[i].id == int(id):
            await ctx.send(f"""
                           {resource_requests[i].rmention}
                           Claimant: {ctx.author.display_name.capitalize()}
                           Resource: {resource_requests[i].resource}
                           ID: {resource_requests[i].id}
                           """)
            resource_requests[i].cname = ctx.author.display_name
            resource_requests[i].cid = ctx.author.id
            resource_requests[i].cmention = ctx.author.mention
            pickle.dump( resource_requests, open("requests.p", "wb"))
            await ctx.message.delete()

@bot.command()
async def complete(ctx, id=-1):
    for i in range(len(resource_requests)):
        if resource_requests[i].id == int(id):
            await ctx.send(f"""
                           {resource_requests[i].rmention}
                           Completer: {ctx.author.display_name.capitalize()}
                           Resource: {resource_requests[i].resource}
                           ID: {resource_requests[i].id}
                           """)
            resource_requests.pop(i)
            pickle.dump( resource_requests, open("requests.p", "wb"))
            await ctx.message.delete()

@bot.command()
async def claims(ctx):
    out = ''
    for i in range(len(resource_requests)):
        if resource_requests[i].cid == ctx.author.id:
            out += ' ' + str(resource_requests[i].id) + ' - ' + resource_requests[i].rname.capitalize() + ' - ' + resource_requests[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s claims:\n {out}')
    await ctx.message.delete()

@bot.command()
async def requests(ctx):
    out = ''
    for i in range(len(resource_requests)):
        if resource_requests[i].rid == ctx.author.id:
            out += ' ' + str(resource_requests[i].id) + ' - ' + resource_requests[i].cname.capitalize() + ' - ' + resource_requests[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s requests:\n {out}')
    await ctx.message.delete()
       
bot.run('MTI2NzU4Mzk3NDE4ODkwODY0NA.GWE-ZM.uBNJbEm-KxZPIBkftv_6VECVBhiMqBi8XgJgi0')