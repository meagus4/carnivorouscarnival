import asyncio
import json
import random

import disnake
import disnake.ext.commands
import database

db = database.Database()


def __init__():
    return


async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str,
                    optional: str | None = None):
    stacker_board = [
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1]
    ]

    # Initializes Variables for Gameplay
    turn_active = True
    game_ongoing = True
    current_row = 9
    row_position = 2
    row_direction = 1
    width = 3
    delay = 1

    # Initializes Embed / Message
    embed = disnake.Embed(title="Stacker", description="Stacker Game Initializing...")
    message = await thread.send(embed=embed)

    # Listens for Button Clicks
    @bot.listen("on_button_click")
    async def on_button_click(inter: disnake.MessageInteraction):
        nonlocal turn_active
        if inter.component.custom_id.startswith(uid):
            await inter.response.defer(ephemeral=True)
            stacker_board[current_row] = json.loads(inter.component.custom_id.split("-")[1])
            await inter.send("You placed the row!", ephemeral=True)
            turn_active = False

    # Main Game Loop

    while game_ongoing:
        while turn_active:
            print(
                f"row_position: {row_position}, row_direction: {row_direction}, width: {width}, current_row: {current_row}")

            if row_position > 6:
                row_position = 6
            if row_position < 0:
                row_position = 0

            if (stacker_board[current_row][0] == 1 and row_direction == -1) or (
                    stacker_board[current_row][-1] == 1 and row_direction == 1):
                row_direction *= -1

            if turn_active:
                stacker_board[current_row] = [2, 2, 2, 2, 2, 2, 2]
                try:
                    for i in range(width):
                        stacker_board[current_row][row_position + (i * row_direction)] = 1
                    row_position += row_direction
                except IndexError as ex:
                    print(f"{ex}")

            stacker_board_str = ""
            for row in stacker_board[:-1]:
                for value in row:
                    if value == 0:
                        stacker_board_str += "⬛"
                    elif value == 1:
                        stacker_board_str += "🟥"
                    elif value == 2:
                        stacker_board_str += "⬜"
                stacker_board_str += "\n"

            button = disnake.ui.Button(label="Stop", style=disnake.ButtonStyle.red,
                                       custom_id=f"{uid}-{json.dumps(stacker_board[current_row])}")

            embed = disnake.Embed(title="Stacker", description=stacker_board_str)
            await message.edit(embed=embed, components=button)
            await asyncio.sleep(delay)

        for i in range(len(stacker_board[current_row])):
            if stacker_board[current_row][i] == 2:
                stacker_board[current_row][i] = 0
            if stacker_board[current_row][i] == 1 and stacker_board[current_row + 1][i] == 0:
                stacker_board[current_row][i] = 0
                width -= 1
        current_row -= 1
        if current_row == 6 and width == 3:
            width = 2
        elif current_row == 3 and width == 2:
            width = 1
        row_position = 2
        row_direction = 1  # Advances to next row and resets the variables.
        if current_row < 0 or width <= 0:
            game_ongoing = False
            turn_active = False
        else:
            turn_active = True

    score = (10 - current_row - 1) * 50
    if current_row < 0:
        score = score * 2
        desc = f"**Congratulations!**\n{stacker_board_str}\nYou won Stacker! You earned {score} Tickets."
        embed = disnake.Embed(title="Stacker",
                              description=desc)
        if random.randint(1,3) == 3:
            draw = random.randint(1, 10)
            if draw <= 2:
                prize, = db.award_random_prize(member, "Stacker", 1)
            elif draw <= 7:
                prize, = db.award_random_prize(member, "Stacker", 2)
            else:
                prize, = db.award_random_prize(member, "Stacker", 3)
            prize_data = db.get_prize(prize)
            desc += f"\nWow! You won a {prize_data[1]}! You can view your prizes with `/inv`"
    elif current_row < 2:
        score = int(score * 1.5)
        embed = disnake.Embed(title="Stacker",
                              description=f"**Game Over!**\n{stacker_board_str}\nYou earned {score} Tickets this run.")
    else:
        embed = disnake.Embed(title="Stacker",
                              description=f"**Game Over!**\n{stacker_board_str}\nYou earned {score} Tickets this run.")
    db.award_tickets(score, member, "Stacker")
    embed.add_field(name=f"You now have {db.get_tickets(member)} Tickets.", value=" ", inline=False)
    await message.edit(embed=embed, components=[])
    return
