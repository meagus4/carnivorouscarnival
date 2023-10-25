import asyncio

import disnake
import disnake.ext.commands
import random
import database
db = database.Database()
def __init__():
    pass
async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):

    possible_progress = [1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 0]
    random.shuffle(possible_progress)
    attempts = 3
    progress = db.get_game_data("Balloon", member)
    print(progress)
    balloon_popped = False
    step = 10
    display = ""
    message = await thread.send(embed=disnake.Embed(title="Balloon Burst Initializing..."))
    delay = random.randint(3, 7)

    for i in possible_progress[0:10]:
        if i == 1:
            display += "🟥"
        elif i == 2:
            display += "🟨"
        elif i == 3:
            display += "🟩"
        elif i == 5:
            display += "🟦"
        elif i == 0:
            display += "🪙"

    while attempts > 0 and not balloon_popped:

        if possible_progress[step] == 1:
            display += "🟥"
        elif possible_progress[step] == 2:
            display += "🟨"
        elif possible_progress[step] == 3:
            display += "🟩"
        elif possible_progress[step] == 5:
            display += "🟦"
        elif possible_progress[step] == 0:
            display += "🪙"

        display = display[1:]

        embed = disnake.Embed(title="Balloon Popper",
                              description=f"Try and pop the balloon! You have **{attempts}** Attempts Remaining.\n"
                                          f"[{display}]")
        await message.edit(embed=embed)

        step += 1
        if len(possible_progress)-1 < step:
            step = 0


        await asyncio.sleep(1)