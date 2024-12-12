import discord
from discord.ext import commands
from discord.utils import get
from resource_requests import resourceRequest
from projects import Project
import pickle
import time
import database_sqlite

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

db = database_sqlite.DatabaseSqlite()
db.setup_db()

# create in promise on init

def findProject(name):
    return next((i for i in project_list if i.name.lower() == name.lower()), -1)
def findRequest(id):
    return next((i for i in requests_list if i.id == id), -1)

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
async def newProject(ctx):
    maxTime = time.time() + 60
    bot_message = await ctx.send("Creating a new project: What's the project's name?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    if findProject(project_name.content.lower()) != -1:
        await ctx.send("Sorry that name is in use. Please pick another!", delete_after=10.0)
        await bot_message.delete()
        await project_name.delete()
        return

    bot_confirm = await ctx.send("Okay, now we'll start adding resources. When you are done adding resources, type done")
    resources = {}
    doLoop = True
    while doLoop:
        if time.time() > maxTime:
            await ctx.send("Sorry you took too long! This has a maximum time of 60 seconds.", delete_after=10.0)
            await bot_message.delete()
            await project_name.delete()
            await bot_confirm.delete()
            return

        resource_ask = await ctx.send("Please type in the next resource in the format name|amount, or type done to finish")
        resource_ans = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if resource_ans.content.lower() == "done":
            doLoop = False
            await resource_ask.delete()
            await resource_ans.delete()
            await project_name.delete()
        elif not '|' in resource_ans.content.lower():
            await ctx.send("Please make sure you include a | between the name and quantity of the item! Or type done to finish.", delete_after=5.0)
            maxTime = time.time() + 60
        else:
            ans = resource_ans.content.lower().split('|')
            resources[ans[0].lower()] = int(ans[1])
            maxTime = time.time() + 60

    temp = Project(project_name.content.lower(), resources)
    project_list.append(temp)
    pickle.dump( project_list, open("project_list.p", "wb"))
    await ctx.send("Your project has been created!", delete_after=10.0)

    await bot_message.delete()
    await bot_confirm.delete()


@bot.command()
async def contribute(ctx):
    output = "```"
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_after=10.0)
        return
    for p in project_list:
        output += "\n" + p.name.title()
    output += "```"
    await ctx.send(output)
    bot_message = await ctx.send("What project did you contribute to?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    current_project = findProject(project_name.content.lower())

    if current_project == -1:
        await ctx.send("Sorry, I don't see a project under that name! Use the `projects` command to see a list of active projects!", delete_after=10.0)
        await bot_message.delete()
        await project_name.delete()
        return
    await project_name.delete()

    count = 0
    output = "```"
    for k in current_project.resources:
        v = current_project.resources[k]
        w = current_project.maxResources[k]
        if (w - (w-v)) == 0:
            output += f"\n{k: <16}:           Completed"
            count += 1
        else:
            output += f"\n{k: <16}:      {w : >7} total - {w - (w-v): <4} remaining"
            count += 1
        if count % 25 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

    resource_ask = await ctx.send("What resource did you contribute?")
    resource_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if not resource_name.content.lower() in current_project.resources:
        await ctx.send("That resource isn't a part of this project, check pinfo and try again", delete_after=10.0)
        await bot_message.delete()
        return
    await resource_ask.delete()

    count_ask = await ctx.send("How many of that resource did you add?")
    resource_count = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await count_ask.delete()
    if current_project.addContribution(ctx.author.display_name.lower(), resource_name.content.lower(), int(resource_count.content)) == -1:
        await ctx.send("Sorry it doesn't look like that resource is in that project. Use the pinfo command to double check you named it right!", delete_after=10.0)
        return
    await ctx.send("Added your contribution! Thank you for contributing!", delete_after=10.0)

    await bot_message.delete()
    await resource_name.delete()
    await resource_count.delete()
    pickle.dump( project_list, open("project_list.p", "wb"))

@bot.command()
async def projects(ctx):
    output = "```"
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_after=10.0)
        return
    for p in project_list:
        output += "\n" + p.name.title()
    output += "```"
    await ctx.send(output)
    await ctx.message.delete()

@bot.command()
async def pinfo(ctx):
    project_ask = await ctx.send("What project do you want to view?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    output = "```"

    current_project = findProject(project_name.content.lower())
    if current_project == -1:
        await ctx.send("Sorry, there's no project under that name. Use the projects command to see the list!", delete_after=10.0)
        return

    output += f'\nProject: {current_project.name.title()}'
    output = '```'
    output += f'\nProject: {current_project.name.title()}'
    count = 0

    for k in current_project.resources:
        v = current_project.resources[k]
        w = current_project.maxResources[k]
        if (w - (w-v)) == 0:
            output += f"\n{k: <16}:           Completed"
            count += 1
        else:
            output += f"\n{k: <16}:      {w : >7} total - {w - (w-v): <4} remaining"
            count += 1
        if count % 25 == 0:
            output += "```"
            await ctx.send(output)
            output = "```"
    output += "```"
    await ctx.send(output)

    await project_name.delete()
    await project_ask.delete()

@bot.command()
async def finishProject(ctx):
    project_ask = await ctx.send("What project are you completing?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)

    current_project = findProject(project_name.content.lower())
    if current_project == -1:
        await ctx.send("Sorry, there's no project under that name. Use the projects command to see the list!", delete_after=10.0)
        return

    output1 = current_project.completeProject()
    output2 = current_project.getContributions()
    await ctx.send(output1)
    await ctx.send(output2)
    project_list.remove(current_project)

    await project_ask.delete()
    await project_name.delete()
    pickle.dump( project_list, open("project_list.p", "wb"))

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)
