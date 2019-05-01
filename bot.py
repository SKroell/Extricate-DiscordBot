import math
import discord
import asyncio
import steamlb as sl
import datetime
import yaml

config = yaml.safe_load(open("config.yaml"))
icon_url = "https://cdn.discordapp.com/avatars/542096662894608405/c2dbfde314c1f2a12da25ea489a0e98c.webp"
steam_url = "https://store.steampowered.com/app/1012970/Extricate/"

# Leaderboard Stuff
steam_lb = sl.SteamLeaderboard(1012970, config['steam_api_key'])
leaderboards = [
    3236666, 3236720, 3236721, 3236723, 3236724, 3236725, 3236726, 3236727, 3236728, 3236729,  # Section A
    3236730, 3236731, 3236732, 3236733, 3236734, 3236735, 3236736, 3236737, 3236738, 3236739,  # Section B
    3236741, 3236742, 3236743, 3236744, 3236745, 3236746, 3236747, 3236748, 3236749, 3236750,  # Section C
    3236751, 3236752, 3236753, 3236754, 3236756, 3236757, 3236758, 3236759, 3236760, 3236761,  # Section D
    3236762, 3236763, 3236764, 3236765, 3236766, 3236767, 3236768, 3236769, 3236770, 3236771,  # Section E
]

leaderboards_exp = [
    3272402, 3272403, 3272404, 3272405, 3272406, 3272407, 3272408, 3272409, 3272410, 3272412,  # Section A EXP
    3272414, 3272416, 3272417, 3272418, 3272419, 3272420, 3272421, 3272422, 3272424, 3272425,  # Section B EXP
    3272427, 3272428, 3272429, 3272430, 3272431, 3272432, 3272433, 3272435, 3272436, 3272437,  # Section C EXP
    3272439, 3272440, 3272441, 3272442, 3272443, 3272444, 3272445, 3272446, 3272447, 3272448,  # Section D EXP
    3272449, 3272450, 3272452, 3272453, 3272454, 3272455, 3272456, 3272457, 3272458, 3272459,  # Section E EXP
]

# Discord emotes instead of numbers
lb_index = [
    ":trophy:",
    ":second_place:",
    ":third_place:",
    ":four:",
    ":five:",
    ":six:",
    ":seven:",
    ":eight:",
    ":nine:",
    ":keycap_ten:",
]


# Calculates scores for all players
# Scores are calculated with sqrt(n)/sqrt(k/10)
# Where n is the amount of entries and k is the rank
def calculate_leaderboard_scores(exp):
    player_scores = {}
    leaderboard_ids = leaderboards_exp if exp else leaderboards

    print("Getting leaderboard scores...")

    # Loop trough the leaderboard
    for lbid in leaderboard_ids:
        lb = steam_lb.get(lbid=lbid)

        # Skip if leaderboard contains no entries
        if lb is None:
            continue

        # Calculate score for player
        for score in lb.entries:
            lb_score = math.sqrt(len(lb.entries)) / math.sqrt(score.rank / 10)
            current_score = player_scores.get(score.steam_id, 0)
            player_scores[score.steam_id] = current_score + lb_score

    # Return playerscores
    return player_scores


def sort_entries(entries):
    entries = [(v, k) for k, v in entries.items()]
    entries.sort()
    entries.reverse()  # Highest first
    return [(k, v) for v, k in entries]


def create_lb_embed(msg, exp):
    now = datetime.datetime.now()
    title = "Leaderboard (EXP)" if exp else "Leaderboard"
    embed = discord.Embed(title=title, description=msg, color=0xd30106)
    embed.set_author(name="Extricate Game", url=steam_url, icon_url=icon_url)
    embed.set_footer(text="Updated: " + now.strftime("%Y-%m-%d %H:%M") + "(UTC)")
    return embed


class ExtricateBot(discord.Client):
    last_msg = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.update_leaderboard())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def update_leaderboard(self):
        await self.wait_until_ready()
        channel = self.get_channel(559037968720068611)  # channel ID goes here
        while not self.is_closed():
            msg = ""
            msg_exp = ""

            stable_scores = sort_entries(calculate_leaderboard_scores(exp=False))
            exp_scores = sort_entries(calculate_leaderboard_scores(exp=True))

            for x in range(10):
                if len(stable_scores) > x:
                    username = sl.get_username(config['steam_api_key'], stable_scores[x][0])
                    msg += lb_index[x] + " **" + str(username) + "** [**" + str("%.2f" % stable_scores[x][1]) + "** pts]\n"
                if len(exp_scores) > x:
                    username_exp = sl.get_username(config['steam_api_key'], exp_scores[x][0])
                    msg_exp += lb_index[x] + " **" + str(username_exp) + "** [**" + str("%.2f" % exp_scores[x][1]) + "** pts]\n"
            msg += "\nPoints are awarded for every leaderboard (not EXP). Refreshed every 15 minutes"
            msg_exp += "\nPoints are awarded for every EXP leaderboard. Refreshed every 15 minutes"

            if len(await channel.history(limit=5).flatten()) >= 2:
                history = await channel.history(limit=5).flatten()
                await history[1].edit(embed=create_lb_embed(msg, False))
                await history[0].edit(embed=create_lb_embed(msg_exp, True))
                print("EDITED")
            else:
                await channel.send(embed=create_lb_embed(msg_exp, True))
            await asyncio.sleep(900)  # task runs every 15 minutes (roughly since we dont count for running time)


client = ExtricateBot()
client.run(config['discord_auth'])
