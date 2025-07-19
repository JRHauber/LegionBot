import discord
from discord.ext import commands
from discord.utils import get
from discord.ext import tasks
from discord import app_commands
import pickle
import asyncio
import database_sqlite
import random
from datetime import datetime
import datetime as dt
import candidate as cand
import json
import os
from zoneinfo import ZoneInfo
import time
import enum

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix = '$', intents=intents)

def load_pickle_files():
    global project_list
    global votes
    global candidates
    try:
        project_list = pickle.load(open("project_list.p", "rb"))
    except FileNotFoundError:
        project_list = []

    try:
        votes = pickle.load(open("votes.p", "rb"))
    except FileNotFoundError:
        votes = []

    try:
        candidates = pickle.load(open("candidates.p", "rb"))
    except FileNotFoundError:
        candidates = []
    return

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

LEGION_ID = None
ADVERTIZER_ROLE = None
TICKET_ROLE = None
STATE = None
ANNOY_TIME = dt.time(hour = 0, minute = 0, second = 0, tzinfo=ZoneInfo("America/Chicago"))
ACTIVITY_CHECK_START = dt.datetime(2025, 6, 15, 0, 0, 0, 0, ZoneInfo("America/Chicago"))
project_list = None
votes = None
candidates = None
SENATOR_ROLE = None
ADMINISTRATOR_ROLE = None

GUILD_ID = discord.Object(id=1267584422253694996)
DISCIPLINARY_ROLES = [1367304039137542155, 1367304098659176641]
#Prob 1, Prob 2

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    global LEGION_ID
    global ADVERTIZER_ROLE
    global TICKET_ROLE
    global STATE
    global SENATOR_ROLE
    global ADMINISTRATOR_ROLE
    LEGION_ID = bot.get_guild(1267584422253694996)
    ADVERTIZER_ROLE = LEGION_ID.get_role(1360478811661144114)
    TICKET_ROLE = LEGION_ID.get_role(1324782094571798621)
    SENATOR_ROLE = LEGION_ID.get_role(1311824922301038632)
    ADMINISTRATOR_ROLE = LEGION_ID.get_role(1371792303206699040)
    STATE = load_state()
    legion_advert.start()
    ticket_remind.start()
    load_pickle_files()

#@bot.event
#async def on_reaction_add(reaction: discord.Reaction, user):
#    if reaction.message.channel.id == 1394852266309320894:
#        if not reaction.message.guild.get_role(SENATOR_ROLE) in user.roles:
#            await reaction.remove(user)
#    return

@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    guild = bot.get_guild(payload.guild_id)
    message = payload.message_id
    user = guild.get_member(payload.user_id)
    try:
        m = await guild.get_channel(1394852266309320894).fetch_message(message)
        if not SENATOR_ROLE in user.roles:
            for r in m.reactions:
                await r.remove(user)
    except:
        return

@bot.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        if message.guild.get_role(1268739778119995505) in message.author.roles:
            await db.change_user_activity("TRUE", message.author.id)
            await db.user_recent_message(message.created_at.timestamp(), message.author.id)

    await bot.process_commands(message)

@bot.event
async def on_guild_channel_create(channel):
    if "ticket" in channel.name.lower():
        await asyncio.sleep(5)
        await channel.send("""
                           Hello! Welcome to the Legion Discord Server! Please answer these questions to help us get this started!
        1) Have you read and agree to the ⁠rules?
        2) Are you over 18?
        3) Are you joining The Legion, are a member of one of its Allies, or are just here to Visit?
        4) What is your username in Bitcraft?
        5) Are you currently a member of any other group?
        6) What is your primary (and secondary if applicable) language?
        7) What made you interested in joining The Legion? Were you invited by anyone?

        If you are joining the Legion, please ensure that your discord name has your IGN somewhere in it.
                           """)

@bot.event
async def on_member_join(member: discord.Member):
    await asyncio.sleep(45)
    channel = LEGION_ID.get_channel(1373730490871185508)
    await member.add_roles(member.guild.get_role(1324782094571798621))
    await channel.send(f"""
    Hello! Thank you for joining the discord server for The Legion, our group for Bitcraft Online.
    Please make sure you head to this message in the welcome channel and click the button to create a ticket.
    This will allow you to access the rest of the server.
    https://discordapp.com/channels/1267584422253694996/1317666800896577638/1317673462495711322
    {member.mention}
    """)
    print(f"Pinged {member.name} with join info")

@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):
    legionnaire = LEGION_ID.get_role(1268739778119995505)
    federati = LEGION_ID.get_role(1383132329270054984)
    citizen = LEGION_ID.get_role(1383132292444197140)
    if legionnaire in after.roles and not legionnaire in before.roles:
        data = await db.new_user(after.id, after.joined_at.timestamp(), datetime.now().timestamp())
        await after.add_roles(citizen)
        print(data)
    if federati in after.roles and not federati in before.roles:
        data = await db.new_user(after.id, after.joined_at.timestamp(), datetime.now().timestamp())
        await after.add_roles(citizen)
        print(data)
    if legionnaire in before.roles and not legionnaire in after.roles:
        data = await db.remove_user(after.id)
        await after.remove_roles(citizen)
        print(data)
    if federati in before.roles and not federati in after.roles:
        data = await db.remove_user(after.id)
        await after.remove_roles(citizen)
        print(data)
    return

@bot.tree.command(name = "request_list", description = "Get a list of open requests")
async def request_list(interaction: discord.Interaction):
    await interaction.response.send_message("Fetching Requests...", ephemeral = True)
    output = "```"
    namePadding = 0
    requestPadding = 0
    claimantPadding = 0
    name = ''

    data = await db.get_requests(int(interaction.guild.id))
    for r in data:
        if r.claimant_id == None:
            claim_name = "Unclaimed"
        else:
            claim_name = interaction.guild.get_member(r.claimant_id).display_name[0:12]
        user_name = interaction.guild.get_member(r.requestor_id).display_name[0:14]
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
            claim_name = interaction.guild.get_member(r.claimant_id).display_name
        if len(r.resource) > 40:
            resource = r.resource[0:40]
            resource += "..."
        else:
            resource = r.resource
        user_name = interaction.guild.get_member(r.requestor_id).display_name
        if len(user_name) > 12:
            name = user_name[0:14]
            name += "..."
        else:
            name = user_name
        if len(claim_name) > 12:
            claimant = claim_name[0:12]
            claimant += "..."
        else:
            claimant = claim_name
        output += f"\n {name: <{namePadding}} - {resource: <{requestPadding}} - {claimant: <{claimantPadding}} - {r.id}"
        count += 1

        if count % 10 == 0:
            output += "```"
            await interaction.followup.send(output)
            output = "```"
        elif count == len(data):
            output += "```"
            await interaction.followup.send(output)

@bot.tree.command(name = "request", description = "Request a resource")
async def request(interaction: discord.Interaction, resource: str):
    id = await db.insert_request(interaction.guild_id, interaction.user.id, resource, datetime.now().timestamp())
    await interaction.response.send_message(f"""
    Requester: {interaction.user.mention}
    Resource: {resource}
    ID: {id}
    {interaction.guild.get_role(1386902362429325382).mention}""")

@bot.tree.command(name = "cancel", description = "Cancel a resource request")
async def cancel(interaction: discord.Interaction, id: int):
    currentRequest = None
    data = await db.get_user_requests(interaction.guild.id, interaction.user.id)
    for d in data:
        if d.id == id:
            currentRequest = await db.cancel_request(interaction.guild.id, id)

    if currentRequest == None:
        await interaction.response.send_message("That ID didn't work, please double check it!", ephemeral=True)
        return

    await interaction.response.send_message(f"""
    <@{currentRequest.requestor_id}>
        Canceler: {interaction.user.display_name.capitalize()}
        Resource: {currentRequest.resource}
        ID: {id}
    """)
    print(f"{interaction.user.display_name} canceled a request")

@bot.tree.command(name = "claim", description = "Claim a resource request")
async def claim(interaction: discord.Interaction, id: int):
    currentRequest = await db.claim_request(id, interaction.guild_id, interaction.user.id)

    if currentRequest == None:
        await interaction.response.send_message("That ID didn't work, please double check it!", ephemeral = True)
        return

    await interaction.response.send_message(f"""
    <@{currentRequest.requestor_id}>
        Claimant: {interaction.user.display_name.capitalize()}
        Resource: {currentRequest.resource}
        ID: {id}
    """)

@bot.tree.command(name = "unclaim", description = "Unclaim a request")
async def unclaim(interaction: discord.Interaction, id: int):
    currentRequest = await db.unclaim_request(id, interaction.guild_id, interaction.user.id)

    if currentRequest == None:
        await interaction.response.send_message("That ID didn't work, please double check it!", ephemeral = True)
        return

    await interaction.response.send_message(f"You have successfully unclaimed {currentRequest.resource} ({id})", ephemeral=True)

@bot.tree.command(name = "complete", description = "Complete a request")
async def complete(interaction: discord.Interaction, id: int):
    currentRequest = await db.finish_request(id, interaction.guild_id, interaction.user.id)

    if currentRequest == None:
        await interaction.response.send_message("That ID didn't work, please double check it!", ephemeral = True)
        return

    await interaction.response.send_message(f"""
    <@{currentRequest.requestor_id}>
        Completer: {interaction.user.display_name.capitalize()}
        Resource: {currentRequest.resource}
        ID: {id}
    """)
    print(f"{interaction.user.display_name} completed a request")

@bot.tree.command(name = "claims", description = "See which requests you've claimed")
async def claims(interaction: discord.Interaction):
    data = await db.get_claims(interaction.guild_id, interaction.user.id)
    out = ''

    for d in data:
        user_name = interaction.guild.get_member(d.requestor_id).display_name
        out += f" {d.id} - {user_name.capitalize()} - {d.resource}\n"
    await interaction.response.send_message(f"{interaction.user.display_name}'s requests: \n {out}", ephemeral = True)

@bot.tree.command(name = "requests", description = "See a list of requests you've made")
async def requests(interaction: discord.Interaction):
    data = await db.get_user_requests(interaction.guild_id, interaction.user.id)
    out = ''
    for d in data:
        out += f" {d.id} - {interaction.user.display_name.capitalize()} - {d.resource}\n"
    await interaction.response.send_message(f"Your requests:\n {out}", ephemeral = True)

@bot.tree.command(name = "new_project", description = "Create a new project")
async def new_project(interaction: discord.Interaction, name: str):
    data = await db.new_project(interaction.guild_id, name, time.time())

    if data == None:
        await interaction.response.send_message("Something went wrong and your project didn't get made... idk how. Contact Lanidae I guess")
    else:
        await interaction.response.send_message(f"Your project has been created! Your project's name is {name} and its id is {data}")

@bot.tree.command(name = "add_resource", description = "Add a resource to the project")
async def add_resource(interaction: discord.Interaction, resource: str, amount: int, project: int):
    await db.add_resource(resource, amount, project, interaction.guild_id)
    await interaction.response.send_message(f"You have added the resource: {amount} - {resource} to project: {project}", delete_after=60)

@bot.tree.command(name = "remove_resource", description = "Remove a resource from a project")
async def remove_resource(interaction: discord.Interaction, resource: str, project: int):
    await db.remove_resource(resource, project, interaction.guild_id)
    await interaction.response.send_message(f"You have removed {resource} from project: {project}", delete_after = 60)

@bot.tree.command(name = "list_projects", description = "Display a list of active project")
async def list_projects(interaction: discord.Interaction):
    await interaction.response.send_message("Fetching Project List...", ephemeral=True)
    data = await db.list_projects(interaction.guild_id)
    output = "```"
    count = 0
    for p in data:
        output += f"\n {p[0].title()} - {p[1]}"
        count += 1
        if count % 20 == 0:
            output += "```"
            await interaction.followup.send(output)
            output = "```"
        elif count == len(data):
            output += "```"
            await interaction.followup.send(output)

@bot.tree.command(name = "get_contributors", description = "Get a list of people who have contributed to this project")
async def get_contributors(interaction: discord.Interaction, project: int):
    await interaction.response.send_message("Fetching Contributors...", ephemeral=True)
    data = await db.list_contributors(project, interaction.guild_id)
    output = "```"
    count = 0
    for c in data:
        output += f"\n{interaction.guild.get_member(c[0]).display_name}"
        count += 1
        if count % 20 == 0:
            output += "```"
            await interaction.followup.send(output)
            output = "```"
        elif count == len(data):
            output += "```"
            await interaction.followup.send(output)

#@bot.tree.command(name = "get_contributions", description = "Get a list of what resources members have been contributed to this project")
#async def get_contributions(interaction: discord.Interaction, project: int):
#    await interaction.response.send_message("Fetching Contributions...", ephemeral=True)
#    data = await db.list_contributions(project, interaction.guild_id)
#    output = "```"
#    count = 0
#    lastid = None
#    for c in data:
#        if lastid != c[0] or count % 20 == 0:
#            lastid = c[0]
#            output += f"\n{interaction.guild.get_member(c[0]).display_name}"
#            count += 1
#        output += f"\n\t{c[1]} - {c[2]}"
#        count += 1
#        if count % 20 == 0:
#            output += "```"
#            await interaction.followup.send(output)
#            output = "```"
#        elif count >= len(data):
#            output += "```"
#            await interaction.followup.send(output)

@bot.tree.command(name = "get_resources", description = "Get a list of what resources are in this project")
async def get_resources(interaction: discord.Interaction, project: int):
    await interaction.response.send_message("Fetching Resources...", ephemeral=True)
    data = await db.list_resources(project, interaction.guild_id)
    print(data)
    if data == [] or data == None:
        output = "That project either doesn't exist or is already complete."
        await interaction.followup.send(output)
        return
    output = f"```\n{data[0][3]} - ({data[0][4]})\n"
    count = 0
    for r in data:
        if r[1] >= r[2]:
            output = output
        else:
            output += f"\n{r[0] : <18} - {r[1] : >7} / {r[2] : >7}"
        count += 1
        if count % 20 == 0:
            output += "```"
            if output != "``````":
                await interaction.followup.send(output)
            output = f"```\n{r[3]} - ({r[4]})\n"
        elif count == len(data):
            output += "```"
            if output != "``````":
                await interaction.followup.send(output)

@bot.tree.command(name = "contribute", description = "Record your contributions to a project")
async def contribute(interaction: discord.Interaction, project: int, resource: str, amount: int):
    await db.contribute_resources(project, resource, amount, interaction.user.id, interaction.guild_id)
    await interaction.response.send_message(f"Thank you for your contribution! You contributed {amount} - {resource} to project: {project}", ephemeral = True)

@bot.tree.command(name = "finish_project", description = "Finish a project, good job!")
async def finishProject(interaction: discord.Interaction, project: int):
    name = await db.complete_project(project, interaction.guild_id)
    await interaction.response.send_message(f"You've marked project {name} - {project} as complete!")

@bot.tree.command(name="search_user", description="bingus", guild=GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def search_user(interaction: discord.Interaction, uid: str):
    user = interaction.guild.get_member(int(uid))
    await interaction.response.send_message(f"That user is: {user.display_name}", ephemeral=True)

@bot.tree.command(name = "test", description= "test", guild=GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def test(interaction: discord.Interaction):


    await interaction.response.send_message("Bingus.")

@tasks.loop(minutes=67)
async def legion_advert():
    global STATE
    if int(datetime.now().timestamp()) - STATE['LAST_ANNOUNCE'] < 28800:
        return
    STATE['LAST_ANNOUNCE'] = int(datetime.now().timestamp())
    save_state(STATE)
    humans = [m for m in LEGION_ID.members if (not m.bot and (ADVERTIZER_ROLE in m.roles))]
    pinged = random.choice(humans)
    await pinged.send("Hello! You've been chosen to advertize for Legion this time! Please make sure to post something unique/fun in the Legion's Looking For Group post in the main bitcraft server!")
    print(f"Pinged {pinged.name} to advertise.")

@tasks.loop(time=ANNOY_TIME)
async def ticket_remind():
    humans = [m for m in LEGION_ID.members if (not m.bot and (TICKET_ROLE in m.roles))]
    for h in humans:
        date_check = datetime.now().replace(tzinfo=ZoneInfo("America/Chicago")) - h.joined_at.replace(tzinfo=ZoneInfo("America/Chicago"))
        if date_check.days > 7:
            try:
                await h.send(f"""
                It looks like you've been in the Legion discord for over a week without making a ticket.
                You have been automatically removed from the server to help maintain its cleanliness.
                If you believe this was in error, please rejoin the server and make a ticket.
                """)
            except:
                print(f"Couldn't send kick message to {h.display_name}")
            await h.kick()
            print(f"Kicked {h.name} for inactivity in ticket.")
        else:
            await h.send(f"""
                     Hi! You joined The Legion discord server for Bitcraft, but seem to have not made a ticket.
                     Please head to this channel: https://discord.com/channels/1267584422253694996/1317666800896577638
                     and click the ***Create ticket*** button at the top of the channel in order to finish the process of joining The Legion.
                     \n If you've already made a ticket, please make sure to read the questions in that channel and answer them in your created ticket.
                     \n Thank you for your cooperation :)
                     """)
            print(f"Pinged {h.name} to make a ticket.")

@tasks.loop(time=ANNOY_TIME)
async def purge_old_requests():
    for g in bot.guilds:
        data = db.get_requests(g.id)
        for d in data:
            if (datetime.now() - dt.timedelta(days=7)) < dt.datetime.fromtimestamp(d.claimed_at):
                db.purge_old_requests(g.id, d[0])

@tasks.loop(time=ANNOY_TIME)
async def activity_update():
    humans = [m for m in LEGION_ID.members if (not m.bot and LEGION_ID.get_role(1268739778119995505)())]

    for h in humans:
        data = await db.get_user_activity(h.id)

        #Check if they've talked since the Grace Period ended
        if data[1] == 0:
            await db.change_user_activity("FALSE", h.id)
            return

        time_difference = datetime.now() - datetime.fromtimestamp(data[1])

        if time_difference.days > 30:
            await db.change_user_activity("FALSE", h.id)
            return

    remove_data = await db.get_all_users()
    user_ids = []
    for h in humans:
        user_ids.append(h.id)

    for d in remove_data:
        if not d[0] in user_ids:
            removed = await db.remove_user(d[0])
            print(f"Removed user {removed[0]} from the guild database")

@bot.command()
async def synccmd(ctx: commands.Context):
    fmt = await bot.tree.sync(guild = GUILD_ID)
    await ctx.send(
        f"Synced {len(fmt)} commands to the current server",
        delete_after=1.0
    )
    await ctx.message.delete()

@bot.command()
async def globalsync(ctx: commands.Context):
    fmt = await bot.tree.sync()
    await ctx.send(
        f"Synced {len(fmt)} commands globally",
        delete_after = 5.0
    )
    await ctx.message.delete()

@bot.tree.command(name="candidate", description="Declare yourself as a candidate for Senate.", guild=GUILD_ID)
@app_commands.checks.has_role(1268739778119995505)
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
    data = await db.get_user(interaction.user.id)
    date_check = datetime.now().replace(tzinfo=None) - datetime.fromtimestamp(data[2])
    if date_check.days < 30:
        await interaction.response.send_message("You haven't been here long enough! You need to have been in the guild for at least one month to be a Senator!", ephemeral=True)
        return

    # Check if new candidate declarations are allowed
    if not STATE['CANDIDATES_ALLOWED']:
        await interaction.response.send_message("Sorry, the period to declare your candidacy has ended. You'll have to try again next election", ephemeral=True)
        return

    # Check if user is already a candidate
    for c in candidates:
        if c.name == interaction.user.name:
            await interaction.response.send_message("It looks like you're already a candidate, no need to put yourself in twice!", ephemeral=True)
            return

    # Check if user is Vigiles
    if interaction.guild.get_role(1382057254039064869) in interaction.user.roles:
        await interaction.response.send_message("Sorry, you are a Vigil and are thus not eligible for senate", ephemeral=True)
        return

    max_id = 0
    for x in candidates:
        if x.cid > max_id:
            max_id = x.cid
    max_id += 1
    c = cand.Candidate(interaction.user.name, interaction.user.id, max_id)
    candidates.append(c)
    print(f"{interaction.user.display_name} declared themselves a Candidate")
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
    STATE['CANDIDATES_ALLOWED'] = True
    save_state(STATE)
    await interaction.response.send_message("You've started an election!", ephemeral=True)

@bot.tree.command(name="start_voting", description = "Start voting", guild = GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def start_voting(interaction: discord.Interaction):
    global STATE
    STATE['CANDIDATES_ALLOWED'] = False
    save_state(STATE)
    await interaction.response.send_message("Stopped candidates from declaring so voting can start.", ephemeral = True)

@bot.tree.command(name="withdraw", description="Withdraw yourself as a candidate", guild=GUILD_ID)
@app_commands.checks.has_role(1268739778119995505)
async def withdraw(interaction: discord.Interaction):
    for c in candidates:
        if c.uid == interaction.user.id:
            candidates.remove(c)
            pickle.dump(candidates, open("candidates.p", "wb"))
            await interaction.response.send_message("You have removed yourself as a candidate", ephemeral = True)
            return

@bot.tree.command(name = "vote", description="Vote for a candidate!", guild = GUILD_ID)
@app_commands.checks.has_role(1268739778119995505)
async def vote(interaction: discord.Interaction, cid: int):
    for c in candidates:
        if c.cid == cid:
            c.Vote(interaction.user.id)
            await interaction.response.send_message(f"Thank you for voting for {c.name}", ephemeral=True)
            pickle.dump(candidates, open("candidates.p", "wb"))
            return

@bot.tree.command(name = "remove_vote", description = "Remove your vote for a candidate", guild = GUILD_ID)
@app_commands.checks.has_role(1268739778119995505)
async def remove_vote(interaction: discord.Interaction, cid: int):
    for c in candidates:
        if c.cid == cid:
            c.RemoveVote(interaction.user.id)
            await interaction.response.send_message(f"You have successfully remove your vote for {c.name}", ephemeral=True)
            pickle.dump(candidates, open("candidates.p", "wb"))
            return

@bot.tree.command(name = "list_candidates", description = "List all candidates for the election", guild = GUILD_ID)
@app_commands.checks.has_role(1268739778119995505)
async def list_candidates(interaction: discord.Interaction):
    output = ""
    for c in candidates:
        output += f'{c.name} - {c.cid}\n'
    if candidates == []:
        output = "There's not an election going on or no one has declared themselves a candidate yet."
    await interaction.response.send_message(output, ephemeral=True)


@bot.tree.command(name = "end_election", description = "End a senate election", guild = GUILD_ID)
@app_commands.checks.has_role(1311825324308303913)
async def end_election(interaction: discord.Interaction, senator_count: int):
    global STATE
    STATE['ELECTION_STARTED'] = False
    save_state(STATE)
    output = ""

    sorted_candidates = sorted(candidates, key = lambda x: x.votes)

    await interaction.response.send_message("Tallying the votes!", delete_after=120)

    for m in interaction.guild.members:
        if SENATOR_ROLE in m.roles:
            await m.remove_roles(SENATOR_ROLE)
            print(f"Removed senator role from: {m.display_name}")
        if ADMINISTRATOR_ROLE in m.roles:
            await m.remove_roles(ADMINISTRATOR_ROLE)
            print(f"Removed administrator role from: {m.display_name}")

    if len(sorted_candidates) <= senator_count:
        for c in sorted_candidates:
            output += f'{c.name} - ({c.cid}) - Votes: {c.votes}\n'
            m = interaction.guild.get_member(c.uid)
            print(m.display_name)
            print(output)

            await m.add_roles(SENATOR_ROLE)
    else:
        count = 1
        for c in sorted_candidates:
            if count <= senator_count:
                output += f'{c.name} - ({c.cid}) - Votes: {c.votes}\n'
                m = interaction.guild.get_member(c.uid)
                await m.add_roles(senate)

    await interaction.followup.send(output)
    candidates = []
    pickle.dump(candidates, open("candidates.p", "wb"))

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
    await interaction.response.send_message("Getting profession counts", ephemeral=True)
    output = '```'
    rcount = 0
    for k, v in profession_roles.items():
        count = 0
        rcount += 1
        role = interaction.guild.get_role(v)
        output += f"{k.title():14} -"
        for m in role.members:
            data = await db.get_user_activity(m.id)
            if (interaction.guild.get_role(1268739778119995505) in m.roles) and (data[0] == 1):
                output += f" {m.display_name},"
                count += 1
        output = output[:-1]
        output += f" - ({count})\n\n"
        if rcount %4 == 0:
            output += "```"
            await interaction.followup.send(output)
            output = "```"
        elif rcount == len(profession_roles):
            output += "```"
            await interaction.followup.send(output)
    return

@bot.tree.command(name = "add_member", description = "Add a member as part of Legion", guild = GUILD_ID)
@app_commands.checks.has_role(1311824922301038632)
async def add_member(interaction: discord.Interaction, user: discord.Member):
    data = await db.new_user(user.id, user.joined_at.timestamp(), datetime.now().timestamp())
    output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
    await interaction.response.send_message(output, ephemeral = True)

@bot.tree.command(name = "remove_member", description = "Remove a member as part of Legion", guild = GUILD_ID)
@app_commands.checks.has_role(1311824922301038632)
async def remove_member(interaction: discord.Interaction, user: discord.Member):
    data = await db.remove_user(user.id)
    output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
    await interaction.response.send_message(output, ephemeral = True)

@bot.tree.command(name = "get_member", description = "Get user data", guild = GUILD_ID)
@app_commands.checks.has_role(1311824922301038632)
async def get_member(interaction: discord.Interaction, user: discord.Member):
    data = await db.remove_user(user.id)
    output = f"Name: {interaction.guild.get_member(data[0]).display_name} - Join Date: <t:{int(data[1])}> - Member Date: <t:{int(data[2])}>"
    await interaction.response.send_message(output, ephemeral = True)

@bot.tree.command(name = "active_check", description = "This will REALLY slow the bot down. Don't run it often.", guild = GUILD_ID)
@app_commands.checks.has_role(1311824922301038632)
async def active_check(interaction: discord.Interaction, months: int):
    await interaction.response.send_message("Calculating active members, this might take a while")
    two_months = datetime.now().timestamp() - 2628288 * months
    two_months = datetime.fromtimestamp(two_months)
    active_members = {}

    async for message in interaction.guild.get_channel(1304830655921651722).history(limit = None, after = two_months):
        if not message.author.bot and interaction.guild.get_member(message.author.id):
            if interaction.guild.get_role(1268739778119995505) in message.author.roles:
                active_members[message.author.id] = message.author.name

    print("done with legion-chat")

    async for message in interaction.guild.get_channel(1267584422253694999).history(limit = None, after = two_months):
        if not message.author.bot and interaction.guild.get_member(message.author.id):
            if interaction.guild.get_role(1268739778119995505) in message.author.roles:
                active_members[message.author.id] = message.author.name

    print("done with general-chat")

    active_count = len(active_members)
    output = ""
    for v in active_members.values():
        output += f"{v}, "
    output += f"({active_count})"

    await interaction.followup.send(f"```{output}```")

    for m in interaction.guild.members:
        if interaction.guild.get_role(1268739778119995505) in m.roles:
            if m.id in active_members.keys():
                await db.change_user_activity("TRUE", m.id)
            else:
                await db.change_user_activity("FALSE", m.id)

@bot.tree.command(name="basic_active_check", description = "activity check that relies on passive tracking", guild = GUILD_ID)
async def basic_active_check(interaction: discord.Interaction):
    await interaction.response.send_message("Looking up active members, just a second.", ephemeral=True)
    humans = [m for m in LEGION_ID.members if (not m.bot and (interaction.guild.get_role(1268739778119995505) in m.roles))]

    count = 0
    for h in humans:
        data = await db.get_user_activity(h.id)
        if data == None:
            print(f"Something broke at user {h.name}")
            continue
        elif data[0] == 1:
            count += 1

    await interaction.followup.send(f"There are {count} active users.", ephemeral=True)

@bot.tree.error
async def on_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError) -> None:
    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("Sorry, you don't have the permissions to run that command.", ephemeral=True)
        return
    if isinstance(error, discord.app_commands.MissingRole):
        await interaction.response.send_message("Sorry, you don't have the right role to run that command", ephemeral=True)
        return
    if isinstance(error, discord.errors.Forbidden):
        print("Forbidden error. Probably a failed DM.")
        return
    await interaction.followup.send(f"The bot has thrown the following error: {error}. Please contact Lanidae and send a screenshot of this message.", ephemeral=True)

with open('secrets', 'r') as sf:
    token = sf.readline().strip()

bot.run(token)