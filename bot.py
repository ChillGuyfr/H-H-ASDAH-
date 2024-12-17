import discord
from discord.ext import commands
import random
import string
from datetime import datetime, timedelta
import time
import asyncio  # Added asyncio import

# Set up the bot with a command prefix (e.g., '!')
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Required for detecting new members joining

bot = commands.Bot(command_prefix='!', intents=intents)

# Define a custom check for the specific user ID
specific_user_id = 1216082044241838162

def is_specific_user():
    def predicate(ctx):
        return ctx.author.id == specific_user_id
    return commands.check(predicate)

# Lists of realistic first and last names for Gmail
first_names = ['John', 'Emily', 'Michael', 'Sophia', 'James', 'Olivia', 'David', 'Emma']
last_names = ['Smith', 'Johnson', 'Brown', 'Taylor', 'Wilson', 'White', 'Harris', 'Martin']

# Function to generate a secure password
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    while True:
        password = ''.join(random.choice(characters) for _ in range(length))
        if (any(c.islower() for c in password) and
            any(c.isupper() for c in password) and
            any(c.isdigit() for c in password) and
            any(c in string.punctuation for c in password)):
            break
    return password

# Function to generate a real-life-like name
def generate_real_name():
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Function to generate a spammy username
def generate_spam_username():
    characters = string.ascii_letters + string.digits
    username = ''.join(random.choice(characters) for _ in range(random.randint(8, 16)))
    return ''.join(char.upper() if random.choice([True, False]) else char for char in username)

# Function to generate a random birthday (with year over 18)
def generate_birthday():
    age = random.randint(18, 100)
    current_year = datetime.now().year
    birth_year = current_year - age
    birth_date = datetime(birth_year, random.randint(1, 12), random.randint(1, 28))
    return birth_date.strftime('%Y-%m-%d')

# Event when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# Event to send a DM when a new member joins the server
@bot.event
async def on_member_join(member):
    welcome_message = (
        f"Hi @{member.name}! Welcome to the server.\n\n"
        "To get started, type `!generate` in the General channel.\n\n"
        "For more information, check your DMs or type `!help`."
    )
    try:
        await member.send(
            "HOW TO USE\n\n"
            "1⃣ **Get Started**\n"
            "Type `!generate` in the General channel. The bot will DM you with the following information:\n"
            "\ud83d\udd11 Password\n\ud83d\udc64 Username\n\ud83c\udf82 Birthday\n\n"
            "2⃣ **Supported Services**\n"
            "This works for services like:\n"
            "- Gmail\n"
            "- Roblox\n"
            "- And more!\n\n"
            "3⃣ **Questions?**\n"
            "If you need any help, DM @Chillguy and we'll assist you!\n\n"
            "4⃣ **Privacy & Data**\n"
            "- We do not collect your data.\n"
            "- Your passwords, usernames, and birthdays are never stored.\n"
            "- Your privacy is our priority.\n\n"
            "5⃣ **Important Notes**\n"
            "- `!generate` can only be used in the General channel.\n"
            "- You can also use `!delMessages` in your DM with the bot to delete all of its messages.\n"
            "- There is a 5-second cooldown for each generation you do."
        )
        await member.send(welcome_message)
    except discord.Forbidden:
        pass  # No output

# Command to generate tailored username, password, and birthday
@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def generate(ctx):
    if not isinstance(ctx.channel, discord.TextChannel) or ctx.channel.name != 'general':
        await ctx.author.send("Sorry, you can only use this command in the General channel.")
        return

    await ctx.author.send(
        "Which service do you want to generate credentials for?\n"
        "Type one of the following:\n"
        "- `Gmail`\n"
        "- `Roblox`\n"
        "- `Other`\n"
        "- Or `Cancel` to exit."
    )
    await ctx.send(f"{ctx.author.mention}, check your DMs to proceed!")

    def check_dm(msg):
        return msg.author == ctx.author and isinstance(msg.channel, discord.DMChannel)

    try:
        msg = await bot.wait_for("message", check=check_dm, timeout=60)
    except asyncio.TimeoutError:
        await ctx.author.send("You took too long to respond. Please try again.")
        return

    service = msg.content.lower()

    if service == "gmail":
        username = generate_real_name()
        password = generate_password()
        birthday = generate_birthday()
        response = f"Service: Gmail\nName: {username}\nPassword: {password}\nBirthday: {birthday}"
    elif service == "roblox":
        username = generate_spam_username()
        password = generate_password()
        birthday = generate_birthday()
        response = f"Service: Roblox\nUsername: {username}\nPassword: {password}\nBirthday: {birthday}"
    elif service == "other":
        username = generate_spam_username()
        password = generate_password()
        birthday = generate_birthday()
        response = f"Service: Other Games\nUsername: {username}\nPassword: {password}\nBirthday: {birthday}"
    elif service == "cancel":
        await ctx.author.send("Command canceled. Have a nice day!")
        return
    else:
        await ctx.author.send("Invalid selection. Please try again and type one of the valid options.")
        return

    await ctx.author.send(f"Here are your generated credentials:\n\n{response}")

# Command for specific user to delete up to 1000 messages including bot messages in general with 10s cooldown
@bot.command(name="del@")
@is_specific_user()
@commands.cooldown(1, 10, commands.BucketType.user)
async def delat(ctx):
    if ctx.channel.name == 'general':
        try:
            deleted = await ctx.channel.purge(limit=1000)
            await ctx.send(f"Deleted {len(deleted)} messages in #general.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.", delete_after=5)
        except discord.HTTPException:
            await ctx.send("An error occurred while deleting messages.", delete_after=5)
    else:
        await ctx.send("This command can only be used in the #general channel.", delete_after=5)

# Command for everyone to delete bot messages in DMs
@bot.command(aliases=['delmsgs', 'delmsg', 'delMessages'])
async def delmessages(ctx):
    if isinstance(ctx.channel, discord.DMChannel):
        try:
            deleted = []
            async for message in ctx.channel.history(limit=1000):
                if message.author == bot.user:
                    await message.delete()
                    deleted.append(message)
            await ctx.send(f"Deleted {len(deleted)} bot messages.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("I don't have permission to delete messages.", delete_after=5)
        except discord.HTTPException:
            await ctx.send("An error occurred while deleting messages.", delete_after=5)
    else:
        await ctx.send("This command can only be used in DMs with the bot.")

# Run the bot with your token
bot.run('MTMxNjI4OTY2MDU0ODI4NDQyNg.G36I1c.xpNo680Ucgw652Jb-aDRZKKbAQNP-uOphvw1c8')
