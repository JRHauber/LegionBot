import discord
from discord.ext import commands
from discord.utils import get
import random
import math
from resource_requests import Request
from projects import Project
import pickle

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents=intents)

try:
    requests_list = pickle.load(open("requests.p", "rb"))
except FileNotFoundError:
    requests_list = []
try:
    server_list = pickle.load(open("servers.p", "rb"))
except FileNotFoundError:
    server_list = []
try:
    project_list = pickle.load(open("project_list.p", "rb"))
except FileNotFoundError:
    project_list = []


# create in promise on init
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
async def setup(ctx):
    await ctx.send("Test")
@bot.command()
async def request(ctx, role= "foraging", *, message="Test Message"):
        j=1
        if requests_list != []:
            for i in range(len(requests_list)):
                if requests_list[i].id == j:
                    j += 1
        else:
            id = 1
        id = j
        sent = await ctx.send(f"""
                {get(ctx.guild.roles, id=profession_roles[role.lower()]).mention}
                Requester: {ctx.author.mention}
                Message: {message}
                ID: {id}
                """)
        r = Request(int(id), ctx.author.display_name, ctx.author.mention, ctx.author.id, 'Unclaimed', '', 0, message, sent.id)
        print(r.rname)
        requests_list.append(r)
        print(requests_list)
        pickle.dump( requests_list, open("requests.p", "wb"))
        await ctx.message.delete()

@bot.command()
async def claim(ctx, id= -1):
    for i in range(len(requests_list)):
        if requests_list[i].id == int(id):
            await ctx.send(f"""
                           {requests_list[i].rmention}
                           Claimant: {ctx.author.display_name.capitalize()}
                           Resource: {requests_list[i].resource}
                           ID: {requests_list[i].id}
                           """)
            requests_list[i].cname = ctx.author.display_name
            requests_list[i].cid = ctx.author.id
            requests_list[i].cmention = ctx.author.mention
            pickle.dump( requests_list, open("requests.p", "wb"))
            await ctx.message.delete()
            return
    await ctx.send("Invalid ID! Check your numbers!")
    await ctx.message.delete()

@bot.command()
async def complete(ctx, id=-1):
    for i in range(len(requests_list)):
        if requests_list[i].id == int(id):
            await ctx.send(f"""
                           {requests_list[i].rmention}
                           Completer: {ctx.author.display_name.capitalize()}
                           Resource: {requests_list[i].resource}
                           ID: {requests_list[i].id}
                           """)
            requests_list.pop(i)
            pickle.dump( requests_list, open("requests.p", "wb"))
            await ctx.message.delete()
            return

@bot.command()
async def claims(ctx):
    out = ''
    for i in range(len(requests_list)):
        if requests_list[i].cid == ctx.author.id:
            out += ' ' + str(requests_list[i].id) + ' - ' + requests_list[i].rname.capitalize() + ' - ' + requests_list[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s claims:\n {out}')
    await ctx.message.delete()

@bot.command()
async def requests(ctx):
    out = ''
    for i in range(len(requests_list)):
        if requests_list[i].rid == ctx.author.id:
            out += ' ' + str(requests_list[i].id) + ' - ' + requests_list[i].cname.capitalize() + ' - ' + requests_list[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s requests:\n {out}')
    await ctx.message.delete()

@bot.command()
async def newProject(ctx):
    botans = await ctx.send("Creating a new project: What's the project's name?")
    name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await ctx.send("Okay, now we'll start adding resources. When you are done adding resources, type done")
    resources = {}
    doLoop = True
    while doLoop:
        rask = await ctx.send("What's the name of the resource?")
        rname = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await rname.delete()
        await rask.delete()
        rask = await ctx.send("How many of that resource do you need?")
        rcount = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await rcount.delete()
        await rask.delete()
        resources[rname.content] = int(rcount.content)
        rask = await ctx.send("Are you done adding resources?")
        rans = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if rans.content.lower() == "done":
            doLoop = False
            await rask.delete()
        else:
            await rask.delete()
            await rans.delete()
    temp = Project(name.content.lower(), resources)
    project_list.append(temp)
    pickle.dump( project_list, open("project_list.p", "wb"))
    print("LOGGED")
    await ctx.send("Your project has been created!", delete_after=30.0)
    await botans.delete()
    await ctx.message.delete()
    await rans.delete()
    await name.delete()


@bot.command()
async def contribute(ctx):
    botans = await ctx.send("What project did you contribute to?")
    pname = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    for p in project_list:
        if p.name.lower() == pname.content.lower():
            currentProject = p
            await pname.delete()
        else:
            await ctx.send("Sorry, I don't see a project under that name! Use the `projects` command to see a list of active projects!", delete_after=30.0)
            await botans.delete()
            await pname.delete()
            return
    botask = await ctx.send("What resource did you contribute?")
    rname = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await botask.delete()
    botask = await ctx.send("How many of that resource did you add?")
    rcount = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await botask.delete()
    if currentProject.addContribution(ctx.author.display_name.lower(), rname.content.lower(), int(rcount.content)) == -1:
        await ctx.send("Sorry it doesn't look like that resource is in that project. Use the pinfo command to double check you named it right!", delete_after=30.0)
    else:
        await ctx.send("Added your contribution! Thank you for contributing!", delete_after=30.0)
    await ctx.message.delete()
    await botans.delete()
    await rname.delete()
    await rcount.delete()
    pickle.dump( project_list, open("project_list.p", "wb"))


@bot.command()
async def projects(ctx):
    output = "```"
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_after=30.0)
    else:
        for p in project_list:
            output += "\n" + p.name.lower()
        output += "```"
        await ctx.send(output)
    await ctx.message.delete()

@bot.command()
async def pinfo(ctx):
    pview = await ctx.send("What project do you want to view?")
    pname = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    output = "```"
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_after=30.0)
    else:
        for p in project_list:
            if p.name.lower() == pname.content.lower():
                output += f'\nProject: {p.name.title()}'
                for k in p.resources:
                    v = p.resources[k]
                    for i in p.maxResources:
                        j = p.maxResources[i]
                        if i == k:
                            output += f"\n{i}: {v}/{j}"
                output += "```"
                await ctx.send(output)
            else:
                await ctx.send("Sorry, there's no project under that name. Use the projects command to see the list!", delete_after=30.0)
    await ctx.message.delete()
    await pname.delete()
    await pview.delete()
@bot.command()
async def finishProject(ctx):
    pview = await ctx.send("What project are you completing?")
    pname = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_afte=30.0)
    else:
        for p in project_list:
            if p.name.lower() == pname.content.lower():
                output1 = p.completeProject()
                output2 = p.getContributions()
                await ctx.send(output1)
                await ctx.send(output2)
                project_list.remove(p)
            else:
                await ctx.send("Sorry, there is no project under that name. Use the projects command to see the list!", delete_after=30.0)
    await pview.delete()
    await pname.delete()

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)
