import asyncio

import disnake
import disnake.ext.commands
import random
import database
db = database.Database()
def __init__():
    pass

def  progress_to_string(progress:int):
    balloon_states = {
        0: """:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::balloon::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:""",
        1: """:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::red_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::red_square::red_square::red_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::red_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::black_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:""",
        2: """:white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::red_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::red_square::red_square::red_square::white_large_square::white_large_square:
    :white_large_square::red_square::red_square::red_square::red_square::red_square::white_large_square:
    :white_large_square::white_large_square::red_square::red_square::red_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::black_large_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square::white_large_square:""",
        3: """:white_large_square::white_large_square::white_large_square::red_square::white_large_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::red_square::red_square::red_square::white_large_square::white_large_square:
    :white_large_square::red_square::red_square::red_square::red_square::red_square::white_large_square:
    :red_square::red_square::red_square::red_square::red_square::red_square::red_square:
    :white_large_square::red_square::red_square::red_square::red_square::red_square::white_large_square:
    :white_large_square::white_large_square::red_square::red_square::red_square::white_large_square::white_large_square:
    :white_large_square::white_large_square::white_large_square::black_large_square::white_large_square::white_large_square::white_large_square:"""
    }

    if progress >= 16:
        balloon_display = balloon_states[3]
    elif progress >= 9:
        balloon_display = balloon_states[2]
    elif progress >= 4:
        balloon_display = balloon_states[1]
    else:
        balloon_display = balloon_states[0]

    return balloon_display

async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):
    possible_progress = [1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 1, 1, 1, 2, 2, 2, 3, 3, 3, 5, 0]
    random.shuffle(possible_progress)
    attempts = 3
    temp = db.get_game_data("Balloon", member)
    if temp:
        progress, = temp
        progress = int(progress)
    else:
        progress = 0

    starting_progress = progress
    balloon_popped = False
    step = 10
    display = ""
    spin_button = disnake.ui.Button(label="Spin The Wheel!", style=disnake.ButtonStyle.primary, custom_id=uid)

    delay = random.randint(5, 15)

    @bot.listen("on_button_click")
    async def on_button_click(inter: disnake.MessageInteraction):
        nonlocal spin_active
        if inter.component.custom_id.startswith(uid):
            await inter.send("Inflating the Balloon!", ephemeral=True)
            spin_active = True
            spin_button.disabled = True

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

    spin_active = False
    embed = disnake.Embed(title="Balloon Popper",
                          description=f"Try and pop the balloon! You have **{attempts}** Attempts Remaining.\n{progress_to_string(progress)}\n:small_red_triangle_down:\n"
                                      f"{display}\n:small_red_triangle:")

    message = await thread.send(embed=embed, components=spin_button)

    while attempts > 0 and not balloon_popped:
        while spin_active:
            if possible_progress[step] == 1:
                display += "🟥"
            elif possible_progress[step] == 2:
                display += "🟨"
            elif possible_progress[step] == 3:
                display += "🟩"
            elif possible_progress[step] == 5:
                display += "🟦"
            elif possible_progress[step] == 20:
                display += "🪙"

            display = display[1:]

            embed = disnake.Embed(title="Balloon Popper",
                                  description=f"Try and pop the balloon! You have **{attempts}** Attempts Remaining.\n{progress_to_string(progress)}\n:small_red_triangle_down:\n"
                                              f"{display}\n:small_red_triangle:")
            await message.edit(embed=embed, components=spin_button)

            step += 1
            if len(possible_progress) - 1 < step:
                step = 0

            if delay > 0:
                delay -= 1
            else:
                spin_button.disabled = False
                delay = random.randint(5, 15)
                break
            await asyncio.sleep(1)
        progress_text = ""

        if spin_active:
            attempts -= 1

            if display[0] == "🟥":
                progress_text = f"The wheel has finished! You made a small amount of progress on inflating the balloon."
                progress += 1
            elif display[0] == "🟨":
                progress_text = f"The wheel has finished! You made a moderate amount of progress on inflating the balloon."
                progress += 2
            elif display[0] == "🟩":
                progress_text = f"The wheel has finished! You made a decent amount of progress on inflating the balloon."
                progress += 3
            elif display[0] == "🟦":
                progress_text = f"The wheel has finished! You made a large amount of progress on inflating the balloon!!"
                progress += 5
            elif display[0] == "🪙":
                progress_text ="JACKPOT! Luck shines upon you and you instantly burst the balloon!"
                progress += 20
            if progress >= 20:
                db.award_tickets(1750, member, "Balloon")
                win_text = f"\nThe balloon has burst! You earned 1750 Tickets! You now have {db.get_tickets(member)} Tickets."
                if random.randint(1, 2) == 1:

                    rarities = {
                        0: "Common",
                        1: "Rare",
                        2: "Medium-Rare",
                        3: "Well-Done"
                    }

                    draw = random.randint(1, 10)
                    if draw <= 2:
                        prize = db.award_random_prize(member, "Balloon", 1)
                    elif draw <= 7:
                        prize = db.award_random_prize(member, "Balloon", 2)
                    else:
                        prize, = db.award_random_prize(member, "Balloon", 3)
                    prize_data = db.get_prize(prize)
                    win_text += f"\nWow! You won a {rarities[prize_data[3]]} {prize_data[1]}! You can view your prizes with `/inv`"
                spin_button = []
                attempts = 0
            elif attempts == 0:
                tickets = (progress - starting_progress)*100
                db.award_tickets(tickets, member, "Balloon")
                win_text = f"\nYou ran out of breath! You earned {tickets} Tickets! You now have {db.get_tickets(member)} Tickets.\nNote: Balloon Progress persists between rounds!"
                spin_button = []
            else:
                win_text = ""

            embed = disnake.Embed(title="Balloon Popper",
                                  description=f"Try and pop the balloon! You have **{attempts}** Attempts Remaining.\n{progress_to_string(progress)}\n:small_red_triangle_down:\n"
                                              f"{display}\n:small_red_triangle:\n{progress_text}{win_text}")

            await message.edit(embed=embed, components=spin_button)
            spin_active = False
            if attempts == 0:

                if progress >= 20:
                    progress = 0
                db.set_game_data("Balloon", member, progress)
                return
        await asyncio.sleep(1)