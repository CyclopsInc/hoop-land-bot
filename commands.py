@bot.command()
async def hello(ctx):
    await ctx.send('Hello!')

@bot.command()
@commands.has_permissions(manage_channels=True)
async def upload(ctx):
    # Check if a file was uploaded with the command
    if len(ctx.message.attachments) == 0:
        await ctx.send("Please upload a JSON file with the command.")
        return

    # Get the first attachment from the message
    attachment = ctx.message.attachments[0]

    # Check if the attachment is a JSON file
    if not attachment.filename.endswith(".json"):
        await ctx.send("Please upload a valid JSON file.")
        return

    # Download the file
    file_data = await attachment.read()

    # Decode the file data as a JSON object
    try:
        json_data = json.loads(file_data)
    except json.JSONDecodeError:
        await ctx.send("Failed to parse the JSON file.")
        return

    # Get the current working directory
    current_directory = os.getcwd()

    # Define the directory name
    directory_name = "save_files"

    # Create the directory path by joining the current directory and the directory name
    directory_path = os.path.join(current_directory, directory_name)

    # Check if the directory already exists
    if not os.path.exists(directory_path):
        # Create the directory
        os.makedirs(directory_path)
        print(f"Directory '{directory_name}' created successfully.")
    else:
        print(f"Directory '{directory_name}' already exists.")

    # Save the JSON data to a file
    file_path = f"save_files/{ctx.guild.id}.json"  # Use a unique file name based on the Discord server ID or any other identifier
    with open(file_path, "w") as file:
        json.dump(json_data, file)

    await ctx.send("File uploaded and saved successfully.")

    try:
        teams = json_data["teams"]  # Assuming 'Teams' is the key for the array of teams
        for team in teams:
            roster = team["roster"]  # Assuming 'Roster' is the key for the array of players in each team
            for player in roster:
                firstName = player["firstName"]
                lastName = player["lastName"]
                age = player["age"]
                experience = player["currentSeason"]
                shooting = player["shooting"]
                inside = player["dunking"]
                dribbling = player["dribbling"]
                passing = player["passing"]
                rebounding = player["rebound"]
                stealing = player["steal"]
                blocking = player["block"]
                seasonStats = player["seasonStats"]
                careerStats = player["careerStats"]
                hiPTS = player["hiPTS"]
                hiFGM = player["hiFGM"]
                hiTPM = player["hiTPM"]
                hiREB = player["hiREB"]
                hiAST = player["hiAST"]
                hiSTL = player["hiSTL"]
                hiBLK = player["hiBLK"]
                hiTO = player["hiTO"]

                print(f"Successfully extracted player data from the JSON file.")
    except KeyError:
        await ctx.send("Failed to extract player data from the JSON file.")
        return

    await ctx.send("Player data extracted successfully.")


@upload.error
async def upload_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command. Channel management permissions are required.")

def extract_names(player_name, json_data):
    player_name = player_name.strip()
    player_name = unicodedata.normalize('NFD', player_name)
    player_name = player_name.replace('\u2019', "'")  # Replace curly apostrophes with straight apostrophes

    # Find the last space in the name
    last_space_index = player_name.rfind(' ')

    if last_space_index != -1:
        # Split the name into first name and last name
        last_name = player_name[last_space_index + 1:].rstrip("'")  # Remove any trailing apostrophes from last name
        first_name = player_name[:last_space_index].rstrip("'")  # Remove any trailing apostrophes from first name
    else:
        first_name = player_name.rstrip("'")  # Remove any trailing apostrophes from the single name
        last_name = ""

    # Check if the exact name exists in the JSON data
    for team in json_data.get("teams", []):
        for player in team.get("roster", []):
            if player.get("firstName") == first_name and player.get("lastName") == last_name:
                return first_name, last_name

    # If the exact name is not found, use fuzzy matching to find the best match
    players = []
    for team in json_data.get("teams", []):
        players.extend(team.get("roster", []))

    names = [f"{player.get('firstName')} {player.get('lastName')}" for player in players]
    match = fuzzywuzzy.process.extractOne(f"{first_name} {last_name}", names)

    if match and match[1] >= 80:
        matched_name = match[0]
        matched_first_name, matched_last_name = matched_name.split(" ", 1)
        return matched_first_name, matched_last_name

    return None, None

@bot.command()
async def stats(ctx, *, player_name):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        # Read the JSON data outside the with statement and store it in the 'data' variable
        with open(file_path, "r") as file:
            data = json.load(file)
        
        first_name, last_name = extract_names(player_name, data)

        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)
            
            season_stats = player_data["seasonStats"]
            # Extract the desired values from the "seasonStats" object
            GP = season_stats["gamesPlayed"]
            GS = season_stats["gamesStarted"]
            PTS = season_stats["PTS"]
            FGM = season_stats["FGM"]
            FGA = season_stats["FGA"]
            TPM = season_stats["TPM"]
            TPA = season_stats["TPA"]
            REB = season_stats["REB"]
            AST = season_stats["AST"]
            STL = season_stats["STL"]
            BLK = season_stats["BLK"]
            TO = season_stats["TO"]

            response = f"Season stats for {player_name}:\n\n**Games Played:** {GP}\n**Games Started:** {GS}\n**PTS:** {PTS}\n**FGM:** {FGM}\n**FGA:** {FGA}\n**TPM:** {TPM}\n**TPA:** {TPA}\n**REB:** {REB}\n**AST:** {AST}\n**STL:** {STL}\n**BLK:** {BLK}\n**TO:** {TO}"
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")
    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}")
      
@bot.command()
async def career(ctx, *, player_name):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        # Read the JSON data outside the with statement and store it in the 'data' variable
        with open(file_path, "r") as file:
            data = json.load(file)
        
        first_name, last_name = extract_names(player_name, data)

        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)
            career_stats = player_data["careerStats"]  
            
            GP = career_stats["gamesPlayed"]
            GS = career_stats["gamesStarted"]
            PTS = career_stats["PTS"]
            FGM = career_stats["FGM"]
            FGA = career_stats["FGA"]
            TPM = career_stats["TPM"]
            TPA = career_stats["TPA"]
            REB = career_stats["REB"]
            AST = career_stats["AST"]
            STL = career_stats["STL"]
            BLK = career_stats["BLK"]
            TO = career_stats["TO"]

            response = f"Career stats for {player_name}:\n\n**Games Played:** {GP}\n**Games Started:** {GS}\n**PTS:** {PTS}\n**FGM:** {FGM}\n**FGA:** {FGA}\n**TPM:** {TPM}\n**TPA:** {TPA}\n**REB:** {REB}\n**AST:** {AST}\n**STL:** {STL}\n**BLK:** {BLK}\n**TO:** {TO}"
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")
    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}.")
      
@bot.command()
async def highs(ctx, *, player_name):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        # Read the JSON data outside the with statement and store it in the 'data' variable
        with open(file_path, "r") as file:
            data = json.load(file)
        
        first_name, last_name = extract_names(player_name, data)

        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)

            # Access the career highs stats directly from the player_data object
            hiPTS = player_data["hiPTS"]
            hiFGM = player_data["hiFGM"]
            hiTPM = player_data["hiTPM"]
            hiREB = player_data["hiREB"]
            hiAST = player_data["hiAST"]
            hiSTL = player_data["hiSTL"]
            hiBLK = player_data["hiBLK"]
            hiTO = player_data["hiTO"]

            response = f"Career Highs for {player_name}:\n\n**Points:** {hiPTS}\n**Field Goals Made:** {hiFGM}\n**Three-Pointers Made:** {hiTPM}\n**Rebounds:** {hiREB}\n**Assists:** {hiAST}\n**Steals:** {hiSTL}\n**Blocks:** {hiBLK}\n**Turnovers:** {hiTO}"
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")
    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}")

      
@bot.command()
async def careeravg(ctx, *, player_name):
    first_name, last_name = player_name.split(" ", 1)
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)
            career_stats = player_data["careerStats"]  # Assuming the stats are stored in an object with key "careerStats"

            games_played = career_stats["gamesPlayed"]

            if games_played == 0:
                await ctx.send(f"{player_name} has not played any games yet.")
                return

            # Calculate per-game averages by dividing the stats by the number of games played
            pts_per_game = round(career_stats["PTS"] / games_played, 1)
            fgm_per_game = round(career_stats["FGM"] / games_played, 1)
            fga_per_game = round(career_stats["FGA"] / games_played, 1)
            tpm_per_game = round(career_stats["TPM"] / games_played, 1)
            tpa_per_game = round(career_stats["TPA"] / games_played, 1)
            reb_per_game = round(career_stats["REB"] / games_played, 1)
            ast_per_game = round(career_stats["AST"] / games_played, 1)
            stl_per_game = round(career_stats["STL"] / games_played, 1)
            blk_per_game = round(career_stats["BLK"] / games_played, 1)
            to_per_game = round(career_stats["TO"] / games_played, 1)

            response = f"Career Per Game Averages for {player_name}:\n\n**Games Played:** {games_played}\n**PPG:** {pts_per_game}\n**FGM:** {fgm_per_game}\n**FGA:** {fga_per_game}\n**3PM:** {tpm_per_game}\n**3PA:** {tpa_per_game}\n**REB:** {reb_per_game}\n**APG:** {ast_per_game}\n**SPG:** {stl_per_game}\n**BPG:** {blk_per_game}\n**TOPG:** {to_per_game}"
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")
    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}")


@bot.command()
async def averages(ctx, *, player_name):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        # Read the JSON data outside the with statement and store it in the 'data' variable
        with open(file_path, "r") as file:
            data = json.load(file)
        
        first_name, last_name = extract_names(player_name, data)
        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)
            season_stats = player_data["seasonStats"]  # Assuming the stats are stored in an object with key "seasonStats"

            games_played = season_stats["gamesPlayed"]

            if games_played == 0:
                await ctx.send(f"{player_name} has not played any games yet.")
                return

            # Calculate per-game averages by dividing the stats by the number of games played
            pts_per_game = round(season_stats["PTS"] / games_played, 1)
            fgm_per_game = round(season_stats["FGM"] / games_played, 1)
            fga_per_game = round(season_stats["FGA"] / games_played, 1)
            tpm_per_game = round(season_stats["TPM"] / games_played, 1)
            tpa_per_game = round(season_stats["TPA"] / games_played, 1)
            reb_per_game = round(season_stats["REB"] / games_played, 1)
            ast_per_game = round(season_stats["AST"] / games_played, 1)
            stl_per_game = round(season_stats["STL"] / games_played, 1)
            blk_per_game = round(season_stats["BLK"] / games_played, 1)
            to_per_game = round(season_stats["TO"] / games_played, 1)

            response = f"Per Game Averages for {player_name}:\n\n**Games Played**: {games_played}\n**PPG**: {pts_per_game}\n**FGM**: {fgm_per_game}\n**FGA**: {fga_per_game}\n**3PM**: {tpm_per_game}\n**3PA**: {tpa_per_game}\n**REB**: {reb_per_game}\n**APG**: {ast_per_game}\n**SPG**: {stl_per_game}\n**BPG**: {blk_per_game}\n**TOPG**: {to_per_game}"
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")

    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}")


@bot.command()
async def ratings(ctx, *, player_name):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        # Read the JSON data outside the with statement and store it in the 'data' variable
        with open(file_path, "r") as file:
            data = json.load(file)
        
        first_name, last_name = extract_names(player_name, data)
        if any(player["firstName"] == first_name and player["lastName"] == last_name for team in data["teams"] for player in team["roster"]):
            player_data = next((player for team in data["teams"] for player in team["roster"] if player["firstName"] == first_name and player["lastName"] == last_name), None)

            shooting = player_data["shooting"]
            inside = player_data["dunking"]
            dribbling = player_data["dribbling"]
            passing = player_data["passing"]
            rebounding = player_data["rebound"]
            stealing = player_data["steal"]
            blocking = player_data["block"]
          
            response = f"Ratings for {player_name}:\n\n" \
                       f"**Shooting:** {shooting}\n" \
                       f"**Inside:** {inside}\n" \
                       f"**Dribbling:** {dribbling}\n" \
                       f"**Passing:** {passing}\n" \
                       f"**Rebounding:** {rebounding}\n" \
                       f"**Stealing:** {stealing}\n" \
                       f"**Blocking:** {blocking}"
            
            await ctx.send(response)
        else:
            await ctx.send(f"No stats found for {player_name}")
    except FileNotFoundError:
        await ctx.send(f"No save file found for {player_name}")

@bot.command()
async def joni (ctx):
    await ctx.send("https://media.discordapp.net/attachments/758042011172471005/1131747633581531156/image0.jpg?width=840&height=840")

season_category_mapping = {
    "GP": "gamesPlayed",
    "GS": "gamesStarted",
    "PTS": "PTS",
    "FGM": "FGM",
    "FGA": "FGA",
    "TPM": "TPM",
    "TPA": "TPA",
    "REB": "REB",
    "AST": "AST",
    "STL": "STL",
    "BLK": "BLK",
    "TO": "TO",
    "FG%": lambda player: player["seasonStats"]["FGM"] / (player["seasonStats"]["FGA"] or 1),
    "3P%": lambda player: player["seasonStats"]["TPM"] / (player["seasonStats"]["TPA"] or 1),
    "PPG": lambda player: player["seasonStats"]["PTS"] / player["seasonStats"]["gamesPlayed"],
    "RPG": lambda player: player["seasonStats"]["REB"] / player["seasonStats"]["gamesPlayed"],
    "APG": lambda player: player["seasonStats"]["AST"] / player["seasonStats"]["gamesPlayed"],
    "SPG": lambda player: player["seasonStats"]["STL"] / player["seasonStats"]["gamesPlayed"],
    "BPG": lambda player: player["seasonStats"]["BLK"] / player["seasonStats"]["gamesPlayed"],
    "TOPG": lambda player: player["seasonStats"]["TO"] / player["seasonStats"]["gamesPlayed"]
}

def get_season_stat_value(player, category):
    if callable(season_category_mapping[category]):
        return round(season_category_mapping[category](player), 2)
    else:
        return round(player["seasonStats"][season_category_mapping[category]], 2)


def get_career_stat_value(player, category):
    if callable(career_category_mapping[category]):
        return round(career_category_mapping[category](player), 2)
    else:
        return round(player["careerStats"][career_category_mapping[category]], 2)
      
@bot.command()
async def leaderboard(ctx, category):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    valid_categories = list(season_category_mapping.keys())

    if category.upper() not in valid_categories:
        await ctx.send("Invalid category. Available categories are: " + ", ".join(valid_categories))
        return

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            players = []
            for team in data["teams"]:
                players.extend(team["roster"])

            players = [player for player in players if player["seasonStats"]["gamesPlayed"] > 0]

            sorted_players = sorted(players, key=lambda player: get_season_stat_value(player, category), reverse=True)
            top_players = sorted_players[:15]
            leaderboard_message = f"**Top 15 Players - {category.capitalize()}**\n\n"

            for i, player in enumerate(top_players, start=1):
                player_name = f"{player['firstName']} {player['lastName']}"
                games_played = player["seasonStats"]["gamesPlayed"]
                if games_played == 0:
                    leaderboard_message += f"{i}. {player_name} - N/A (No games played)\n"
                else:
                    stat_value = get_season_stat_value(player, category)
                    leaderboard_message += f"{i}. {player_name} - {stat_value}\n"

            await ctx.send(leaderboard_message)
    except FileNotFoundError:
        await ctx.send("No save file found.")


career_category_mapping = {
    "GP": "gamesPlayed",
    "GS": "gamesStarted",
    "PTS": "PTS",
    "FGM": "FGM",
    "FGA": "FGA",
    "TPM": "TPM",
    "TPA": "TPA",
    "REB": "REB",
    "AST": "AST",
    "STL": "STL",
    "BLK": "BLK",
    "TO": "TO",
    "FG%": lambda player: player["careerStats"]["FGM"] / (player["careerStats"]["FGA"] or 1),
    "3P%": lambda player: player["careerStats"]["TPM"] / (player["careerStats"]["TPA"] or 1),
    "PPG": lambda player: player["careerStats"]["PTS"] / player["careerStats"]["gamesPlayed"],
    "RPG": lambda player: player["careerStats"]["REB"] / player["careerStats"]["gamesPlayed"],
    "APG": lambda player: player["careerStats"]["AST"] / player["careerStats"]["gamesPlayed"],
    "SPG": lambda player: player["careerStats"]["STL"] / player["careerStats"]["gamesPlayed"],
    "BPG": lambda player: player["careerStats"]["BLK"] / player["careerStats"]["gamesPlayed"],
    "TOPG": lambda player: player["careerStats"]["TO"] / player["careerStats"]["gamesPlayed"]
}

@bot.command()
async def careerboard(ctx, category):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    valid_categories = list(career_category_mapping.keys())

    if category.upper() not in valid_categories:
        await ctx.send("Invalid category. Available categories are: " + ", ".join(valid_categories))
        return

    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            players = []
            for team in data["teams"]:
                players.extend(team["roster"])

            players = [player for player in players if player["careerStats"]["gamesPlayed"] > 0]

            sorted_players = sorted(players, key=lambda player: get_career_stat_value(player, category), reverse=True)
            top_players = sorted_players[:15]
            leaderboard_message = f"**Top 15 Players - {category.capitalize()}**\n\n"
            for i, player in enumerate(top_players, start=1):
                player_name = f"{player['firstName']} {player['lastName']}"
                stat_value = get_career_stat_value(player, category)
                leaderboard_message += f"{i}. {player_name} - {stat_value}\n"            

            await ctx.send(leaderboard_message)

    except FileNotFoundError:
        await ctx.send("No save file found.")
     
@bot.command()
async def exportcareer(ctx):
    file_path = f"save_files/{ctx.guild.id}.json"  # Update the file path based on your directory structure

    try:
        with open(file_path, "r") as file:
            data = json.load(file)

        fieldnames = ["Player", "Games Played", "PTS", "Wins", "FGM", "FGA", "TPM", "TPA", "REB", "AST", "STL", "BLK", "TO"]

        with open("career_stats.csv", mode='w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

            for team in data["teams"]:
                for player in team["roster"]:
                    writer.writerow({
                        "Player": f"{player['firstName']} {player['lastName']}",
                        "Games Played": player["careerStats"]["gamesPlayed"],
                        "PTS": player["careerStats"]["PTS"],
                        "Wins": player["careerStats"]["win"],
                        "FGM": player["careerStats"]["FGM"],
                        "FGA": player["careerStats"]["FGA"],
                        "TPM": player["careerStats"]["TPM"],
                        "TPA": player["careerStats"]["TPA"],
                        "REB": player["careerStats"]["REB"],
                        "AST": player["careerStats"]["AST"],
                        "STL": player["careerStats"]["STL"],
                        "BLK": player["careerStats"]["BLK"],
                        "TO": player["careerStats"]["TO"]
                    })
            for player in data["freeAgents"]:
              writer.writerow({
                "Player": f"{player['firstName']} {player['lastName']}",
                "Games Played": player["careerStats"]["gamesPlayed"],
                "PTS": player["careerStats"]["PTS"],
                "Wins": player["careerStats"]["win"],
                "FGM": player["careerStats"]["FGM"],
                "FGA": player["careerStats"]["FGA"],
                "TPM": player["careerStats"]["TPM"],
                "TPA": player["careerStats"]["TPA"],
                "REB": player["careerStats"]["REB"],
                "AST": player["careerStats"]["AST"],
                "STL": player["careerStats"]["STL"],
                "BLK": player["careerStats"]["BLK"],
                "TO": player["careerStats"]["TO"]
                    })
        await ctx.send("Career stats exported successfully to 'career_stats.csv'.")
    except FileNotFoundError:
        await ctx.send("No save file found.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        print(f'{error}')
        return
    if isinstance(error, commands.CheckFailure):
        print(f'{error} ({ctx.invoked_with})')
        return
    await ctx.send(f'`ERROR: {error}`')
    raise error

    # Ensure that the code is indented properly within the `on_command_error` function
    await bot.process_commands(ctx.message)

def find_general_channel(guild):
    for channel in guild.channels:
        if channel.name == "general" and isinstance(channel, discord.TextChannel):
            return channel
    return None

@bot.event
async def on_message(message):
    if message.author == bot.user:
      return

    print(f"Received message: '{message.content}'")
    await bot.process_commands(message)

@bot.command()
async def announce(ctx, *, message):
    if str(ctx.author.id) == '613406805694873601':
        # Loop through all the guilds the bot is a member of
        for guild in bot.guilds:
            # Find the #general channel in the guild
            general_channel = discord.utils.get(guild.channels, name='general', type=discord.ChannelType.text)

            if general_channel:
                await general_channel.send(message)
            else:
                await ctx.send(f"The #general channel was not found in {guild.name}.")
