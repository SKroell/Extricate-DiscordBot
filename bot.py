import os
import discord
from discord.ext import commands
import asyncio
import steamlb as sl


class ExtricateBot(commands.Bot):
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

            stable_scores = sl.sort_entries(sl.calculate_leaderboard_scores(exp=False))
            exp_scores = sl.sort_entries(sl.calculate_leaderboard_scores(exp=True))

            for x in range(10):
                if len(stable_scores) > x:
                    username = sl.get_username(os.environ['steam_api_key'], stable_scores[x][0])
                    msg += sl.lb_index[x] + " **" + str(username) + "** [**" + str("%.2f" % stable_scores[x][1]) + "** pts]\n"
                if len(exp_scores) > x:
                    username_exp = sl.get_username(os.environ['steam_api_key'], exp_scores[x][0])
                    msg_exp += sl.lb_index[x] + " **" + str(username_exp) + "** [**" + str("%.2f" % exp_scores[x][1]) + "** pts]\n"
            msg += "\nPoints are awarded for every leaderboard (not EXP). Refreshed every 15 minutes"
            msg_exp += "\nPoints are awarded for every EXP leaderboard. Refreshed every 15 minutes"

            if len(await channel.history(limit=5).flatten()) >= 2:
                history = await channel.history(limit=5).flatten()
                await history[1].edit(embed=sl.create_lb_embed(msg, "Leaderboard"))
                await history[0].edit(embed=sl.create_lb_embed(msg_exp, "Leaderboard (EXP)"))
                print("Leaderboard Updated!")
            else:
                await channel.send(embed=sl.create_lb_embed(msg_exp, "Leaderboard (EXP)"))
            await asyncio.sleep(900)  # task runs every 15 minutes (roughly since we dont count for running time)

    # Commands
    @commands.command()
    async def leaderboard(ctx, lb):
        # Get leaderboard for specific leaderboard
        times = sl.sort_entries(sl.get_leaderboard_times(lb, 'EXP' in lb), False)
        msg = ""
        for x in range(10):
            username = sl.get_username(os.environ['steam_api_key'], times[x][0])
            msg += sl.lb_index[x] + " **" + str(username) + "** [**" + sl.convert_to_nicetime(times[x][1]) + "**]\n"
        await ctx.send(embed=sl.create_lb_embed(msg, "Leaderboard {}".format(lb)))


client = ExtricateBot(command_prefix='?', description="ExtricateBot")
client.add_command(client.leaderboard)
client.run(os.environ['discord_auth'])
