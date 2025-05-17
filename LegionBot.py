import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from discord import app_commands
import pickle
import asyncio
import database_sqlite
import random
import datetime as dt
import candidate as cand
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents=intents)

try:
    project_list = pickle.load(open("project_list.p", "rb"))
except FileNotFoundError:
    project_list = []

try:
    votes = pickle.load(open("votes.p", "rb"))
except FileNotFoundError:
    votes = []

db = database_sqlite.DatabaseSqlite()
db.setup_db()

def save_state(data, filename = 'state.json'):
    with open(filename, 'w') as f:
        json.dump(data, f)

def load_state(filename = 'state.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

annoy_time = dt.time(hour = 0, minute = 0, second = 0)

# create in promise on init

def findProject(name):
    return next((i for i in project_list if i.name.lower() == name.lower()), -1)

LEGION_ID = None
ADVERTIZER_ROLE = None
TICKET_ROLE = None
STATE = None

NEW_SENATOR_INSTRUCTION_DESCRIPTIONS = ["Ticket Guide", "Perms Description"]
NEW_SENATOR_INSTRUCTIONS = ["https://discord.com/channels/1267584422253694996/1311826613050150912/1356423214401720320", "https://discord.com/channels/1267584422253694996/1311826613050150912/1371791895390453880"]

GUILD_ID = discord.Object(id=1267584422253694996)

DISCIPLINARY_ROLES = [1367304039137542155, 1367304098659176641]
#Prob 1, Prob 2

try:
    candidates = pickle.load(open("candidates.p", "rb"))
except FileNotFoundError:
    candidates = []

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    global LEGION_ID
    global ADVERTIZER_ROLE
    global TICKET_ROLE
    global STATE
    LEGION_ID = bot.get_guild(1267584422253694996)
    ADVERTIZER_ROLE = LEGION_ID.get_role(1360478811661144114)
    TICKET_ROLE = LEGION_ID.get_role(1324782094571798621)
    STATE = load_state()
    legion_advert.start()
    ticket_remind.start()


@bot.event
async def on_guild_channel_create(channel):
    if "ticket" in channel.name.lower():
        await asyncio.sleep(5)
        await channel.send("""
                           Hello! Welcome to the Legion Discord Server! Please answer these questions to help us get this started!
        1) Have you read and agree to the ⁠rules?
        2) Are you over 18?
        3) Are you planning on joining the Legion, are a member of one of its Allies, or are just here to Visit?
        4) What is your username in Bitcraft?
        5) Are you currently a member of any other group?
        6) What is your primary (and secondary if applicable) language?
        7) What made you interested in joining The Legion? Were you invited by anyone?

                           """)

@bot.event
async def on_member_join(member):
    await asyncio.sleep(30)
    await member.send("""
    Hello! Thank you for joining the discord server for The Legion, our group for Bitcraft Online.
    Please make sure you head to this message in the welcome channel and click the button to create a ticket.
    This will allow you to access the rest of the server.
    https://discordapp.com/channels/1267584422253694996/1317666800896577638/1317673462495711322
    """)
    print(f"Pinged {member.name} with join info")

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
async def addResource(ctx, count, pid, *, resource):
    await db.add_resource(resource, int(count), int(pid), int(ctx.message.guild.id))
    await ctx.send(f"Resource added! You added {count} - {resource} to project: {pid}")

@bot.command()
async def removeResource(ctx, pid, *, resource):
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

@bot.command()
async def finishProject(ctx, pid : int):
    name = await db.complete_project(pid, ctx.message.guild.id)
    await ctx.send(f"You have marked the project {name} - {pid} as complete!")

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

@tasks.loop(minutes=971)
async def legion_advert():
    if legion_advert.current_loop == 0:
        return
    humans = [m for m in LEGION_ID.members if (not m.bot and (ADVERTIZER_ROLE in m.roles))]
    pinged = random.choice(humans)
    await pinged.send("Hello! You've been chosen to advertize for Legion this time! Please make sure to post something unique/fun in the Legion's Looking For Group post in the main bitcraft server!")
    print(f"Pinged {pinged.name} to advertise.")

@tasks.loop(time=annoy_time)
async def ticket_remind():
    if ticket_remind.current_loop == 0:
        return
    humans = [m for m in LEGION_ID.members if (not m.bot and (TICKET_ROLE in m.roles))]
    for h in humans:
        await h.send(f"""
                     Hi! You joined The Legion discord server for Bitcraft, but seem to have not made a ticket.
                     Please head to this channel: https://discord.com/channels/1267584422253694996/1317666800896577638
                     and click the ***Create ticket*** button at the top of the channel in order to finish the process of joining The Legion.
                     \n If you've already made a ticket, please make sure to read the questions in that channel and answer them in your created ticket.
                     \n Thank you for your cooperation :)
                     """)
        print(f"Pinged {h.name} to make a ticket.")

@bot.command()
async def synccmd(ctx: commands.Context):
    fmt = await bot.tree.sync(guild = GUILD_ID)
    await ctx.send(
        f"Synced {len(fmt)} commands to the current server",
        delete_after=1.0
    )
    await ctx.message.delete()
    return

@bot.tree.command(name="candidate", description="Declare yourself as a candidate for Senate.", guild=GUILD_ID)
async def candidate(interaction: discord.Interaction):
    # Check for ongoing election
    if not STATE['ELECTION_STARTED']:
        await interaction.response.send_message("There's no election running right now. Please wait for an election to declare your candidacy.", ephemeral=True)
        return

    # Check for disciplinary marks
    for r in DISCIPLINARY_ROLES:
        if interaction.guild.get_role(r) in interaction.user.roles:
            await interaction.response.send_message("Sorry, you have a disciplinary mark, only members in good standing can be Senators.", ephemeral=True)
            return

    # Check user join date
    date_check = dt.datetime.now().replace(tzinfo=None) - interaction.user.joined_at.replace(tzinfo=None)
    if date_check.days < 30:
        await interaction.response.send_message("You haven't been here long enough! You need to have been in the guild for at least one month to be a Senator!", ephemeral=True)
        return

    # Check if user is already a candidate
    for c in candidates:
        if c.name == interaction.user.name:
            await interaction.response.send_message("It looks like you're already a candidate, no need to put yourself in twice!", ephemeral=True)
            return

    max_id = 0
    for x in candidates:
        if x.cid > max_id:
            max_id = x.cid
    max_id += 1
    c = cand.Candidate(interaction.user.name, interaction.user.id, max_id)
    candidates.append(c)
    await interaction.response.send_message(f"""
    Thank you for submitting your candidacy for the Legion Senate, your details are as follows:
    Name: {c.name}
    Candidate ID: {c.cid}
    """, ephemeral = True)
    pickle.dump(candidates, open("candidates.p", "wb"))

@bot.tree.command(name="start_election", description="Start an election!", guild = GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def start_election(interaction: discord.Interaction):
    global STATE
    STATE['ELECTION_STARTED'] = True
    save_state(STATE)
    await interaction.response.send_message("You've started an election!", ephemeral=True)

@bot.tree.command(name = "vote", description="Vote for a candidate!", guild = GUILD_ID)
async def vote(interaction: discord.Interaction, cid: int):
    for c in candidates:
        if c.cid == cid:
            c.Vote(interaction.user.id)
            await interaction.response.send_message(f"Thank you for voting for {c.name}", ephemeral=True)
            pickle.dump(candidates, open("candidates.p", "wb"))
            return

@bot.tree.command(name = "remove_vote", description = "Remove your vote for a candidate", guild = GUILD_ID)
async def remove_vote(interaction: discord.Interaction, cid: int):
    for c in candidates:
        if c.cid == cid:
            c.RemoveVote(interaction.user.id)
            await interaction.response.send_message(f"You have successfully remove your vote for {c.name}", ephemeral=True)
            pickle.dump(candidates, open("candidates.p", "wb"))
            return

@bot.tree.command(name = "list_candidates", description = "List all candidates for the election", guild = GUILD_ID)
async def list_candidates(interaction: discord.Interaction):
    output = ""
    for c in candidates:
        output += f'{c.name} - {c.cid}\n'
    await interaction.response.send_message(output, ephemeral=True)


@bot.tree.command(name = "end_election", description = "End a senate election", guild = GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def end_election(interaction: discord.Interaction, senator_count: int):
    global STATE
    STATE['ELECTION_STARTED'] = False
    save_state(STATE)
    sorted_candidates = sorted(candidates, key = lambda x: x.votes, reverse=True)
    output = ""
    if len(sorted_candidates) <= senator_count:
        for c in sorted_candidates:
            output += f'{c.name} - ({c.cid}) - Votes: {c.votes}\n'
    else:
        count = 1
        for c in sorted_candidates:
            if count <= senator_count:
                output += f'{c.name} - ({c.cid}) - Votes: {c.votes}\n'
    await interaction.response.send_message(output, ephemeral=True)
    current_directory = os.getcwd()
    os.remove(f'{current_directory}\\candidates.p')

profession_roles = {
    "foraging": 1267585190981796021,
    "hunting": 1267585359986823168,
    "mining": 1267585386859728927,
    "forestry": 1267585920773918752,
    "carpentry": 1267585436885323817,
    "leatherworking": 1267585503385882665,
    "masonry": 1267585535858315306,
    "smithing": 1267585569442238556,
    "tailoring": 1267585594750402581,
    "scholar": 1267585753496551627,
    "farming": 1267585784404377763,
    "fishing": 1267585808186081311
}

@bot.tree.command(name = "count_professions", description = "Display a count of member professions", guild = GUILD_ID)
async def count_professions(interaction: discord.Interaction):
    await interaction.response.defer()
    output = '```'
    for k, v in profession_roles.items():
        count = 0
        role = interaction.guild.get_role(v)
        for m in role.members:
            if interaction.guild.get_role(1268739778119995505) in m.roles:
                count += 1
        output += f"{k:<14} - ({count})\n"
    output[:-2]
    output += "```"
    await interaction.followup.send(output, ephemeral=True)
    return
bot.run(token)