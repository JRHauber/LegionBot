import discord
from discord.ext import commands
from discord.utils import get
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
        r = Request(int(id), ctx.author.display_name, ctx.author.mention, ctx.author.id, 'Unclaimed', '', 0, message)
        print(r.requestor_name)
        requests_list.append(r)
        print(requests_list)
        pickle.dump( requests_list, open("requests.p", "wb"))
        await ctx.message.delete()

@bot.command()
async def claim(ctx, id= -1):
    for i in range(len(requests_list)):
        if requests_list[i].id == int(id):
            await ctx.send(f"""
                           {requests_list[i].requestor_mention}
                           Claimant: {ctx.author.display_name.capitalize()}
                           Resource: {requests_list[i].resource}
                           ID: {requests_list[i].id}
                           """)
            requests_list[i].claimant_name = ctx.author.display_name
            requests_list[i].claimant_id = ctx.author.id
            requests_list[i].claimant_mention = ctx.author.mention
            pickle.dump( requests_list, open("requests.p", "wb"))
            await ctx.message.delete()
            return
    await ctx.send("Invalid ID! Check your numbers!")
    await ctx.message.delete()

@bot.command()
async def complete(ctx, id=-1):
    if id == -1:
        await ctx.send("Please enter an id when typing this command", delete_after=10.0)
        await ctx.message.delete()
        return
    for i in range(len(requests_list)):
        if requests_list[i].id == int(id):
            await ctx.send(f"""
                           {requests_list[i].requestor_mention}
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
        if requests_list[i].claimant_id == ctx.author.id:
            out += ' ' + str(requests_list[i].id) + ' - ' + requests_list[i].requestor_name.capitalize() + ' - ' + requests_list[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s claims:\n {out}')
    await ctx.message.delete()

@bot.command()
async def requests(ctx):
    out = ''
    for i in range(len(requests_list)):
        if requests_list[i].requestor_id == ctx.author.id:
            out += ' ' + str(requests_list[i].id) + ' - ' + requests_list[i].claimant_name.capitalize() + ' - ' + requests_list[i].resource + '\n'
    await ctx.send(f'{ctx.author.display_name}\'s requests:\n {out}')
    await ctx.message.delete()

@bot.command()
async def newProject(ctx):
    bot_message = await ctx.send("Creating a new project: What's the project's name?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    for p in project_list:
        if p.name.lower() == project_name.content.lower():
            await ctx.send("Sorry that name is in use. Please pick another!", delete_after=10.0)
            await bot_message.delete()
            await project_name.delete()
            return
    bot_confirm = await ctx.send("Okay, now we'll start adding resources. When you are done adding resources, type done")
    resources = {}
    doLoop = True
    while doLoop:
        resource_ask = await ctx.send("What's the name of the resource?")
        resource_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await resource_name.delete()
        await resource_ask.delete()
        resource_ask = await ctx.send("How many of that resource do you need?")
        resource_count = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        await resource_count.delete()
        await resource_ask.delete()
        resources[resource_name.content.lower()] = int(resource_count.content)
        resource_ask = await ctx.send("Are you done adding resources?")
        resource_ans = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
        if resource_ans.content.lower() == "done":
            doLoop = False
            await resource_ask.delete()
        else:
            await resource_ask.delete()
            await resource_ans.delete()
    temp = Project(project_name.content.lower(), resources)
    print(temp.resources)
    project_list.append(temp)
    pickle.dump( project_list, open("project_list.p", "wb"))
    await ctx.send("Your project has been created!", delete_after=10.0)
    await bot_message.delete()
    await ctx.message.delete()
    await resource_ans.delete()
    await project_name.delete()
    await bot_confirm.delete()


@bot.command()
async def contribute(ctx):
    bot_message = await ctx.send("What project did you contribute to?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    for p in project_list:
        if p.name.lower() == project_name.content.lower():
            currentProject = p
            await project_name.delete()
        else:
            await ctx.send("Sorry, I don't see a project under that name! Use the `projects` command to see a list of active projects!", delete_after=15.0)
            await bot_message.delete()
            await project_name.delete()
            return
    output = '```'
    output += f'\nProject: {currentProject.name.title()}'
    for k in currentProject.resources:
        v = currentProject.resources[k]
        for i in currentProject.maxResources:
            j = currentProject.maxResources[i]
            if i == k:
                output += f"\n{i}: {v}/{j}"
            output += "```"
    await ctx.send(output)
    resource_ask = await ctx.send("What resource did you contribute?")
    resource_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if not resource_name.content.lower() in currentProject.resources:
        await ctx.send("That resource isn't a part of this project, check pinfo and try again", delete_after=10.0)
        await bot_message.delete()
        return
    await resource_ask.delete()
    count_ask = await ctx.send("How many of that resource did you add?")
    resource_count = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    await count_ask.delete()
    if currentProject.addContribution(ctx.author.display_name.lower(), resource_name.content.lower(), int(resource_count.content)) == -1:
        await ctx.send("Sorry it doesn't look like that resource is in that project. Use the pinfo command to double check you named it right!", delete_after=30.0)
    else:
        await ctx.send("Added your contribution! Thank you for contributing!", delete_after=30.0)
    await ctx.message.delete()
    await bot_message.delete()
    await resource_name.delete()
    await resource_count.delete()
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
    project_ask = await ctx.send("What project do you want to view?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    output = "```"
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_after=15.0)
    else:
        for p in project_list:
            if p.name.lower() == project_name.content.lower():
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
                await ctx.send("Sorry, there's no project under that name. Use the projects command to see the list!", delete_after=15.0)
    await ctx.message.delete()
    await project_name.delete()
    await project_ask.delete()

@bot.command()
async def finishProject(ctx):
    project_ask = await ctx.send("What project are you completing?")
    project_name = await bot.wait_for('message', check=lambda message: message.author == ctx.author)
    if project_list == []:
        await ctx.send("There are no active projects right now!", delete_afte=30.0)
    else:
        for p in project_list:
            if p.name.lower() == project_name.content.lower():
                output1 = p.completeProject()
                output2 = p.getContributions()
                await ctx.send(output1)
                await ctx.send(output2)
                project_list.remove(p)
            else:
                await ctx.send("Sorry, there is no project under that name. Use the projects command to see the list!", delete_after=30.0)
    await project_ask.delete()
    await project_name.delete()
    await ctx.message.delete()
    pickle.dump( project_list, open("project_list.p", "wb"))

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)
