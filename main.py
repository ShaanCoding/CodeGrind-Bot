import asyncio
import datetime
import json
import os
import random
import string

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

load_dotenv()

session = requests.Session()
intents = discord.Intents().all()
client = commands.Bot(command_prefix=',', intents=intents)


@client.tree.command(name="setdailychannel", description="Set where the daily problem will be sent")
async def setdailychannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel is None:
        channel = interaction.channel
    # only allow this command to be used by users with the administrator permission
    if interaction.user.guild_permissions.administrator:
        # open the dailychannels.txt file in append mode
        # check if the channel is already in the file
        with open("dailychannels.txt", "r") as file:
            channels = file.readlines()
            print(channels)
            print(channel.id)
            if (str(channel.id) + "\n") in channels or channel.id in channels:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel is already set as the daily channel!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                with open("dailychannels.txt", "a") as file:
                    file.write(f"{channel.id}\n")
                embed = discord.Embed(
                    title="Success!",
                    description=f"This channel has been set as the daily channel!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    else:
        embed = discord.Embed(
            title="Error!",
            description="You do not have the administrator permission!",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


@client.tree.command(name="removedailychannel", description="Remove a daily channel")
async def removedailychannel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if channel is None:
        channel = interaction.channel
    # only allow this command to be used by users with the administrator permission
    if interaction.user.guild_permissions.administrator:
        # open the dailychannels.txt file in append mode
        # check if the channel is already in the file
        with open("dailychannels.txt", "r") as file:
            channels = file.readlines()
            print(channels)
            print(channel.id)
            if (str(channel.id) + "\n") in channels or channel.id in channels:
                with open("dailychannels.txt", "w") as file:
                    for line in channels:
                        if line.strip("\n") != str(channel.id):
                            file.write(line)
                embed = discord.Embed(
                    title="Success!",
                    description=f"This channel has been removed as the daily channel!",
                    color=discord.Color.green())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
            else:
                embed = discord.Embed(
                    title="Error!",
                    description="This channel is not set as the daily channel!",
                    color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
    else:
        embed = discord.Embed(
            title="Error!",
            description="You do not have the administrator permission!",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


@client.tree.command(name="leaderboard", description="View the leaderboard")
async def leaderboard(interaction: discord.Interaction, page: int = 1):
    print(interaction.guild.id)
    if not os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
        embed = discord.Embed(
            title="Leaderboard",
            description="No one has added their LeetCode username yet.",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    else:
        with open(f"{interaction.guild.id}_leetcode_stats.json", "r") as file:
            data = json.load(file)
        sorted_data = sorted(data.items(),
                             key=lambda x: x[1]["total_score"],
                             reverse=True)
        leaderboard = []
        start_index = (page - 1) * 10
        end_index = page * 10
        for i, (
            username,
            stats,
        ) in enumerate(sorted_data[start_index:end_index], start=start_index+1):
            profile_link = f"https://leetcode.com/{username}"
            # Get the discord_username from the stats data in the JSON file
            discord_username = stats.get("discord_username")
            # Get the link_yes_no from the stats data in the JSON file
            link_yes_no = stats.get("link_yes_no")
            if discord_username:
                if link_yes_no == "yes":
                    leaderboard.append(
                        f"**{i}. [{discord_username}]({profile_link})** Score: {stats['total_score']}"
                    )
                else:
                    leaderboard.append(
                        f"**{i}. {discord_username}** Score: {stats['total_score']}")
            else:
                leaderboard.append(
                    f"**{i}. {username}** Score: {stats['total_score']}")
        embed = discord.Embed(title="Leaderboard",
                              color=discord.Color.yellow())
        embed.description = "\n".join(leaderboard)
        # Score Methodology: Easy: 1, Medium: 3, Hard: 5
        embed.set_footer(
            text="Score Methodology: Easy: 1 point, Medium: 3 points, Hard: 5 points")
        # Score Equation: Easy * 1 + Medium * 3 + Hard * 5 = Total Score
        await interaction.response.send_message(embed=embed)
        return


@client.tree.command(name="stats", description="Prints the stats of a user")
async def stats(interaction: discord.Interaction, username: str):
    url = f"https://leetcode.com/{username}"
    print(url)
    response = requests.get(url)

    # Create a BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the <span> element with the specified class for rank
    rank_element = soup.find(
        "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
    print(rank_element)

    rank = rank_element.text.strip() if rank_element else "N/A"
    print(rank)

    # Find all the <span> elements with the specified class for question counts
    span_elements = soup.find_all(
        "span",
        class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
    )
    print(span_elements)

    # Extract the text from each <span> element and store it in an array
    numbers = [span_element.text for span_element in span_elements]

    if len(numbers) == 3:
        easy_completed = int(numbers[0])
        medium_completed = int(numbers[1])
        hard_completed = int(numbers[2])
        print(numbers)

        total_questions_done = easy_completed + medium_completed + hard_completed
        total_score = easy_completed * 1 + medium_completed * 3 + hard_completed * 5

        embed = discord.Embed(
            title=f"Rank: {rank}", color=discord.Color.green())
        embed.add_field(name="**Easy**",
                        value=f"{easy_completed}", inline=True)
        embed.add_field(name="**Medium**",
                        value=f"{medium_completed}", inline=True)
        embed.add_field(name="**Hard**",
                        value=f"{hard_completed}", inline=True)

        embed.set_footer(
            text=f"Total: {total_questions_done} | Score: {total_score}")

        embed.set_author(
            name=f"{username}",
            icon_url="https://repository-images.githubusercontent.com/98157751/7e85df00-ec67-11e9-98d3-684a4b66ae37"
        )
        await interaction.response.send_message(embed=embed)
        return
    else:
        embed = discord.Embed(
            title="Error!",
            description="The username you entered is invalid or LeetCode timed out. Try Again!",
            color=discord.Color.red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return


@client.tree.command(name="daily", description="Returns the daily problem")
async def daily(interaction: discord.Interaction):
    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName':
        'daily',
        'query':
        '''
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    difficulty
                    title
                }
            }
        }
    '''
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    # Extract and print the link
    link = response_data['data']['challenge']['link']
    # Extract and print the title
    title = response_data['data']['challenge']['question']['title']
    # Extract and print the difficulty
    difficulty = response_data['data']['challenge']['question']['difficulty']
    # Extract and print the date
    date = response_data['data']['challenge']['date']
    link = f"https://leetcode.com{link}"
    embed = discord.Embed(title=f"Daily Problem: {title}",
                          color=discord.Color.blue())
    embed.add_field(name="**Difficulty**", value=f"{difficulty}", inline=True)
    embed.add_field(name="**Link**", value=f"{link}", inline=False)

    await interaction.response.send_message(embed=embed)
    return


@client.tree.command(
    name="add",
    description="Adds a user to the leaderboard. Answer with 'yes' to link your LeetCode profile to the leaderboard."
)
async def add(interaction: discord.Interaction, username: str, link: str = None):
    if os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
        with open(f"{interaction.guild.id}_leetcode_stats.json", "r") as file:
            existing_data = json.load(file)
        if username in existing_data:
            await interaction.response.send_message(f"User {username} already exists")
            return

    generated_string = ''.join(random.choices(string.ascii_letters, k=8))
    embed = discord.Embed(title=f"Profile Update Required",
                          color=discord.Color.red())
    embed.add_field(name="Generated Sequence",
                    value=f"{generated_string}",
                    inline=False)
    embed.add_field(name="Username", value=f"{username}", inline=False)
    embed.add_field(
        name="Instructions",
        value=f"Please change your LeetCode Profile Name to the generated sequence.",
        inline=False)
    embed.add_field(
        name="Profile Name Change",
        value="You can do this by clicking [here](https://leetcode.com/profile/) and changing your Name.",
        inline=False)
    embed.add_field(
        name="Time Limit",
        value="You have 60 seconds to change your name, otherwise, you will have to restart the process.",
        inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

    for _ in range(12):
        url = f"https://leetcode.com/{username}"
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        rank_element = soup.find(
            "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
        rank = rank_element.text.strip() if rank_element else "N/A"

        profile_name_element = soup.find(
            "div",
            class_="text-label-1 dark:text-dark-label-1 break-all text-base font-semibold")
        profile_name = profile_name_element.text.strip(
        ) if profile_name_element else ""

        if profile_name == generated_string:
            break

        await asyncio.sleep(5)

    if profile_name == generated_string:
        url = f"https://leetcode.com/{username}"
        print(url)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        rank_element = soup.find(
            "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
        rank = rank_element.text.strip() if rank_element else "N/A"

        profile_name_element = soup.find(
            "div",
            class_="text-label-1 dark:text-dark-label-1 break-all text-base font-semibold")
        profile_name = profile_name_element.text.strip(
        ) if profile_name_element else ""

        span_elements = soup.find_all(
            "span",
            class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
        )

        numbers = [span_element.text for span_element in span_elements]

        easy_completed = int(numbers[0])
        medium_completed = int(numbers[1])
        hard_completed = int(numbers[2])

        total_questions_done = easy_completed + medium_completed + hard_completed
        total_score = easy_completed * 1 + medium_completed * 3 + hard_completed * 5
        discord_username = interaction.user.name

        existing_data[username] = {
            "rank": rank,
            "easy": easy_completed,
            "medium": medium_completed,
            "hard": hard_completed,
            "total_questions_done": total_questions_done,
            "total_score": total_score,
            "discord_username": discord_username,
            "link_yes_or_no": link,
            "discord_id": interaction.user.id
        }

        with open(f"{interaction.guild.id}_leetcode_stats.json", "w") as file:
            json.dump(existing_data, file)
        embed = discord.Embed(title=f"Profile Added",
                              color=discord.Color.green())
        embed.add_field(name="Username:", value=f"{username}", inline=False)
        await interaction.edit_original_response(embed=embed)

        return
    else:
        embed = discord.Embed(title=f"Profile Not Added",
                              color=discord.Color.red())
        embed.add_field(name="Username:", value=f"{username}", inline=False)
        await interaction.edit_original_response(embed=embed)
        return


@client.tree.command(name="delete", description="Delete your profile from the leaderboard.")
async def delete(interaction: discord.Interaction):
    # Check if the file exists
    if os.path.exists(f"{interaction.guild.id}_leetcode_stats.json"):
        print("File exists")
        # Open the file
        with open(f"{interaction.guild.id}_leetcode_stats.json", "r") as file:
            data = json.load(file)

            # Iterate through the data points
            for username, stats in data.items():
                if stats["discord_id"] == interaction.user.id:
                    # Found the data point with matching discord_id
                    # Delete the data point
                    del data[username]
                    # Save the updated data
                    with open(f"{interaction.guild.id}_leetcode_stats.json", "w") as file:
                        json.dump(data, file)
                    # Send a message to the user
                    embed = discord.Embed(title=f"Profile Deleted",
                                          color=discord.Color.green())
                    embed.add_field(name="Username:",
                                    value=f"{username}", inline=False)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    break
            else:
                # No matching data point found
                embed = discord.Embed(title=f"Profile Not Found",
                                      color=discord.Color.red())
                await interaction.response.send_message(embed=embed, ephemeral=True)

    else:
        # File does not exist
        embed = discord.Embed(title=f"Profile Not Found",
                              color=discord.Color.red())
        # This server does not have a leaderboard yet
        embed.add_field(name="Error:",
                        value="This server does not have a leaderboard yet.",
                        inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(
    name="question",
    description="Request a question based on difficulty or at random")
async def question(interaction: discord.Interaction, difficulty: str = "random"):
    if difficulty == "easy":
        response = requests.get("https://leetcode.com/api/problems/all/")
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all easy questions from the data
            easy_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 1
            ]

            # Select a random easy question from the list
            question = random.choice(easy_questions)

            # Extract the question title and link from the data
            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.green())
            embed.add_field(name="Easy", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return
    elif difficulty == "medium":
        response = requests.get("https://leetcode.com/api/problems/all/")
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all medium questions from the data
            medium_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 2
            ]

            # Select a random medium question from the list
            question = random.choice(medium_questions)
            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.orange())
            embed.add_field(name="Medium", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return
    elif difficulty == "hard":
        response = requests.get("https://leetcode.com/api/problems/all/")
        # Check if the request was successful
        if response.status_code == 200:
            # Load the response data as a JSON object
            data = response.json()

            # Get a list of all hard questions from the data
            hard_questions = [
                question for question in data['stat_status_pairs']
                if question['difficulty']['level'] == 3
            ]

            # Select a random hard question from the list
            question = random.choice(hard_questions)

            title = question['stat']['question__title']
            link = f"https://leetcode.com/problems/{question['stat']['question__title_slug']}/"

            embed = discord.Embed(title="LeetCode Question",
                                  color=discord.Color.red())
            embed.add_field(name="Hard", value=title, inline=False)
            embed.add_field(name="Link", value=link, inline=False)

            await interaction.response.send_message(embed=embed)
        else:
            # If the request was not successful, send an error message to the Discord channel
            await interaction.response.send_message(
                "An error occurred while trying to get the question from LeetCode.")
        return

    elif difficulty == "random":
        url = session.get(
            'https://leetcode.com/problems/random-one-question/all').url

        embed = discord.Embed(title="Random Question",
                              color=discord.Color.green())
        embed.add_field(name="URL", value=url, inline=False)

        await interaction.response.send_message(embed=embed)
        return
    else:
        await interaction.response.send_message(
            "Please enter a valid difficulty level. (easy, medium, hard, random)",
            ephemeral=True)
        return


@ client.tree.command(name="help", description="Displays the help menu")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title="LeetCode Bot Help",
                          color=discord.Color.blue())
    embed.add_field(
        name="Adding Your Account to the Leaderboard",
        value="Use `/add {username}` to add your account to the leaderboard. Say 'yes' to link your LeetCode account to the leaderboard and 'no' to not link your LeetCode account to the leaderboard.",
        inline=False)
    embed.add_field(
        name="Getting Your Stats",
        value="Use `/stats {username}` to get your LeetCode statistics.",
        inline=False)
    embed.add_field(
        name="Server Leaderboard",
        value="Use `/leaderboard {page}` to see the leaderboard of this server.",
        inline=False)
    embed.add_field(
        name="Random Questions",
        value="Use `/question {difficulty}` to get a random question of that level, or random if you want a random question of any level.",
        inline=False)
    embed.add_field(
        name="Score Calculation",
        value="The score is calculated based on the amount of questions you have solved. Easy questions are worth 1 point, medium questions are worth 3 points, and hard questions are worth 5 points.",
        inline=False)
    # for adminstrators
    if interaction.user.guild_permissions.administrator:
        embed.add_field(
            name="Set Daily LeetCode Channel",
            value="Use `/setdailychannel` to set the channel where the daily LeetCode question will be sent.",
            inline=False)
        embed.add_field(
            name="Remove Daily LeetCode Channel",
            value="Use `/removedailychannel` to remove the channel where the daily LeetCode question will be sent.",
            inline=False)

    await interaction.response.send_message(embed=embed, ephemeral=True)


@ client.event
async def on_ready():
    print(datetime.datetime.utcnow().hour, datetime.datetime.utcnow().time)
    print("Logged in as a bot {0.user}".format(client))
    server_ids = [guild.id for guild in client.guilds]
    print('Server IDs:', server_ids)
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(e)
    await send_message_at_midnight()


async def send_message_at_midnight():
    await client.wait_until_ready()
    while not client.is_closed():
        await asyncio.sleep(60)  # sleep for a minute
        now = datetime.datetime.utcnow()
        print(now.hour, now.minute)
        if now.hour == 0 and now.minute == 5:
            # get the channel object
            # send the message
            print("hi")
            url = 'https://leetcode.com/graphql'

            headers = {
                'Content-Type': 'application/json',
            }

            data = {
                'operationName':
                'daily',
                'query':
                '''
                query daily {
                    challenge: activeDailyCodingChallengeQuestion {
                        date
                        link
                        question {
                            difficulty
                            title
                        }
                    }
                }
            '''
            }

            response = requests.post(url, json=data, headers=headers)
            response_data = response.json()

            # Extract and print the link
            link = response_data['data']['challenge']['link']
            link = f"https://leetcode.com{link}"
            # Extract and print the title
            title = response_data['data']['challenge']['question']['title']
            # Extract and print the difficulty
            difficulty = response_data['data']['challenge']['question']['difficulty']
            # Extract and print the date
            embed = discord.Embed(title=f"Daily Problem: {title}",
                                  color=discord.Color.blue())
            embed.add_field(name="**Difficulty**",
                            value=f"{difficulty}", inline=True)
            embed.add_field(name="**Link**", value=f"{link}", inline=False)
            # import channels from dailychannels.txt
            with open('dailychannels.txt', 'r') as f:
                channels = f.readlines()
            channels = [channel.strip() for channel in channels]
            for channel_id in channels:
                channel = client.get_channel(int(channel_id))
                await channel.send(embed=embed)
                # Pin the message
                async for message in channel.history(limit=1):
                    await message.pin()
                    return

        if now.hour == 0 and now.minute == 5:
            # retrieve every server the bot is in
            server_ids = [guild.id for guild in client.guilds]
            print('Server IDs:', server_ids)

            # for each server, retrieve the leaderboard
            for server_id in server_ids:
                print(server_id)
                # retrieve the keys from the json file
                if os.path.exists(f"{server_id}_leetcode_stats.json"):
                    with open(f'{server_id}_leetcode_stats.json', 'r') as f:
                        data = json.load(f)
                    for username in data.keys():
                        url = f"https://leetcode.com/{username}/"
                        print(url)
                        response = requests.get(url)
                        soup = BeautifulSoup(response.text, "html.parser")

                        rank_element = soup.find(
                            "span", class_="ttext-label-1 dark:text-dark-label-1 font-medium")
                        rank = rank_element.text.strip() if rank_element else "N/A"

                        span_elements = soup.find_all(
                            "span",
                            class_="mr-[5px] text-base font-medium leading-[20px] text-label-1 dark:text-dark-label-1"
                        )

                        numbers = [
                            span_element.text for span_element in span_elements]

                        easy_completed = int(numbers[0])
                        medium_completed = int(numbers[1])
                        hard_completed = int(numbers[2])

                        total_questions_done = easy_completed + medium_completed + hard_completed
                        total_score = easy_completed * 1 + medium_completed * 3 + hard_completed * 5

                        data[username] = {
                            "rank": rank,
                            "easy": easy_completed,
                            "medium": medium_completed,
                            "hard": hard_completed,
                            "total_questions_done": total_questions_done,
                            "total_score": total_score,
                            "discord_username": data.get(username).get("discord_username"),
                            "link_yes_no": data.get(username).get("link_yes_no")
                        }

                        print(data[username])
                        # update the json file
                        with open(f"{server_id}_leetcode_stats.json", "w") as f:
                            json.dump(data, f, indent=4)


@ client.event
async def on_message(message):
    channel = client.get_channel(message.channel.id)


def get_daily_LC_link():
    url = 'https://leetcode.com/graphql'

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'operationName':
        'daily',
        'query':
        '''
        query daily {
            challenge: activeDailyCodingChallengeQuestion {
                date
                link
                question {
                    difficulty
                    title
                }
            }
        }
    '''
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()

    # Extract and print the link
    link = response_data['data']['challenge']['link']
    # Extract and print the title
    title = response_data['data']['challenge']['question']['title']
    # Extract and print the difficulty
    difficulty = response_data['data']['challenge']['question']['difficulty']
    # Extract and print the date
    date = response_data['data']['challenge']['date']


my_secret = os.environ['TOKEN']
keep_alive()
client.run(my_secret)