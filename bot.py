import discord
from discord.ext import commands
from discord.utils import get
from resource_requests import resourceRequest
import pickle
import time
import database_sqlite

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents=intents)

try:
    project_list = pickle.load(open("project_list.p", "rb"))
except FileNotFoundError:
    project_list = []

db = database_sqlite.DatabaseSqlite()
db.setup_db()

# create in promise on init

def findProject(name):
    return next((i for i in project_list if i.name.lower() == name.lower()), -1)

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")

@bot.command()
async def requestlist(ctx):
    output = "```"
    namePadding = 0
    requestPadding = 0
    claimantPadding = 0

    data = await db.get_requests(int(ctx.message.guild.id))
    for r in data:
        if r.claimant_id == None:
            claim_name = "Unclaimed"
        else:
            claim_name = ctx.message.guild.get_member(int(r.claimant_id)).display_name
        user_name = ctx.message.guild.get_member(int(r.requestor_id)).display_name
        resource = r.resource[0:40]
        namePadding = max(namePadding, len(user_name))
        requestPadding = max(requestPadding, len(resource))
        claimantPadding = max(claimantPadding, len(claim_name))

    namePadding += 4
    requestPadding += 4
    claimantPadding += 4
    count = 0

    for r in data:
        if r.claimant_id == None:
            claim_name = "Unclaimed"
        else:
            claim_name = ctx.message.guild.get_member(int(r.claimant_id)).display_name
        if len(r.resource) > 40:
            resource = r.resource[0:40]
            resource += "..."
        else:
            resource = r.resource
        user_name = ctx.message.guild.get_member(int(r.requestor_id)).display_name
        output += f"\n {user_name: <{namePadding}} - {resource: <{requestPadding}} - {claim_name: <{claimantPadding}} - {r.id}"
        count += 1

        if count % 10 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

@bot.command()
async def setup(ctx):
    await ctx.send("Test")

@bot.command()
async def request(ctx, *, message="Test Message"):
    id = await db.insert_request(ctx.message.guild.id, int(ctx.author.id), message)
    await ctx.send(f"""
        Requester: {ctx.author.mention}
        Message: {message}
        ID: {id}
        """)

@bot.command()
async def claim(ctx, id= -1):
    currentRequest = await db.claim_request(int(id), int(ctx.message.guild.id), int(ctx.author.id))
    if currentRequest == None:
        await ctx.send("Invalid ID, double check that the request ID is right!", delete_after=10.0)
        return

    await ctx.send(f"""
    <@{currentRequest.requestor_id}>
        Claimant: {ctx.author.display_name.capitalize()}
        Resource: {currentRequest.resource}
        ID: {currentRequest.id}
        """)

@bot.command()
async def unclaim(ctx, id = -1):
    currentRequest = await db.unclaim_request(int(id), int(ctx.message.guild.id), int(ctx.author.id))
    if currentRequest == None:
        await ctx.send("Invalid ID, double check that the request ID is right!", delete_after=10.0)
        return
    await ctx.send("You have successfully unclaimed " + currentRequest.resource + "!")

@bot.command()
async def complete(ctx, id=-1):
    currentRequest = await db.finish_request(int(id), int(ctx.message.guild.id), int(ctx.author.id))
    if currentRequest == None:
        await ctx.send("Please enter a proper ID!", delete_after=10.0)
        return

    await ctx.send(f"""
        <@{currentRequest.requestor_id}>
        Completer: {ctx.author.display_name.capitalize()}
        Resource: {currentRequest.resource}
        ID: {currentRequest.id}
    """)

@bot.command()
async def claims(ctx):
    data = await db.get_claims(int(ctx.message.guild.id), int(ctx.author.id))
    out = ''
    for d in data:
        user_name = ctx.message.guild.get_member(int(d.requestor_id)).display_name
        out += ' ' + str(d.id) + ' - ' + user_name.capitalize() + ' - ' + d.resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s claims:\n {out}')

@bot.command()
async def requests(ctx):
    data = await db.get_user_requests(int(ctx.message.guild.id), int(ctx.author.id))
    out = ''
    for d in data:
        user_name = ctx.message.guild.get_member(int(d.requestor_id)).display_name
        out += ' ' + str(d.id) + ' - ' + user_name.capitalize() + ' - ' + d.resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s requests:\n {out}')

@bot.command()
async def newProject(ctx, name : str):
    data = await db.new_project(int(ctx.message.guild.id), name, time.time())
    if data == None:
        await ctx.send("Something went wrong and your project didn't get made... idk what happened. Contact Lanidae I guess.")
    else:
        await ctx.send(f"Your project has been created! Your project name is {name} and your project id is {data}")

@bot.command()
async def addResource(ctx, resource, count, pid):
    await db.add_resource(resource, int(count), int(pid), int(ctx.message.guild.id))
    await ctx.send(f"Resource added! You added {count} - {resource} to project: {pid}")

@bot.command()
async def removeResource(ctx, resource, pid):
    await db.remove_resource(resource, int(pid), int(ctx.message.guild.id))
    await ctx.send(f"Resource removed! You removed {resource} from project: {pid}")

@bot.command()
async def listProjects(ctx):
    data = await db.list_projects(int(ctx.message.guild.id))
    output = "```"
    count = 0
    for p in data:
        output += "\n" + p[0].title() + " - " + str(p[1])
        count += 1
        if count % 20 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

@bot.command()
async def getContributors(ctx, pid):
    data = await db.list_contributors(pid, int(ctx.message.guild.id))
    output = "```"
    count = 0
    for c in data:
        output += "\n" + ctx.message.guild.get_member(int(c[0])).display_name
        count += 1
        if count % 20 == 0:
            output += "```"
            await ctx.send("output")
            output = "```"
    output += "```"
    await ctx.send(output)

@bot.command()
async def getContributions(ctx, pid):
    data = await db.list_contributions(pid, int(ctx.message.guild.id))
    output = "```"
    count = 0
    lastid = None
    for c in data:
        if lastid != c[0]:
            output += f"\n{ctx.message.guild.get_member(int(c[0])).display_name}"
            lastid = c[0]
            count += 1
        output += f"\n\t{c[1]} - {c[2]}"
        count += 1
        if count % 20 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

@bot.command()
async def getResources(ctx, pid):
    data = await db.list_resources(pid, int(ctx.message.guild.id))
    output = "```"
    count = 0
    for c in data:
        output += f"\n{c[0] : <16} - {c[1] : >7} / {c[2] : >7}"
        count += 1
        if count % 20 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

@bot.command()
async def contribute(ctx, pid : int, amount : int, * , name : str):
    await db.contribute_resources(pid, name, amount, ctx.author.id, int(ctx.message.guild.id))
    await ctx.send(f"Thank you for your contribution! You contributed {amount} - {name} to project: {pid}")

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)
