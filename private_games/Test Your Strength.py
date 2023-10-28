import random

import disnake
import disnake.ext.commands
import asyncio
import database
db = database.Database()

def __init__():
    return

def compare(count, medium_value, high_value):
    if count == high_value:
        value = 7
        style = disnake.ButtonStyle.red
    elif count == medium_value:
        value = 4
        style = disnake.ButtonStyle.green
    else:
        value = 1
        style = disnake.ButtonStyle.primary
    return(value, style)
async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):

    strength = 0
    strength_display = ""
    empty_bar = ["⬛⬛⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬜⬛","⬛⬛⬛"]

    newline = "\n"
    embed = disnake.Embed(title="Test Your Strength!", description=f"Hit as many buttons as possible in the time alotted to win!\n{newline.join(empty_bar)}")

    row1 = disnake.ui.ActionRow()
    row2 = disnake.ui.ActionRow()
    row3 = disnake.ui.ActionRow()
    count = 0
    value = 1
    components = []
    game_active = True
    message = await thread.send(embed=embed, components=components)
    time = -11
    @bot.listen("on_button_click")
    async def on_button_click(inter: disnake.MessageInteraction):
        nonlocal strength, message, strength_display, components, time
        if inter.component.custom_id.startswith(uid) and time < 10:
            await inter.response.defer(ephemeral=True)

            strength += int(inter.component.custom_id.split("-")[2])

            if strength > 50:
                strength = 50

            strength_display = "⬛⬛⬛"

            for i in range(10):
                if strength/5 >= i:
                    strength_display = f"⬛🟥⬛\n{strength_display}"
                else:
                    strength_display = f"⬛⬜⬛\n{strength_display}"

            strength_display = f"⬛⬛⬛\n{strength_display}"

            await inter.send("Whack!", ephemeral=True)
            embed = disnake.Embed(title="Test Your Strength!",
                                  description=f"Hit as many buttons as possible in the time allotted to win!\n{strength_display}")

            row1 = disnake.ui.ActionRow()
            row2 = disnake.ui.ActionRow()
            row3 = disnake.ui.ActionRow()
            count = 0
            medium_value = random.randint(0, 9)
            high_value = random.randint(0, 9)
            for i in range(3):
                value, style = compare(count, medium_value, high_value)
                row1.add_button(label="Hit Me!", style=style, custom_id=f"{uid}-{count}-{value}")
                count += 1
                value, style = compare(count, medium_value, high_value)
                row2.add_button(label="Hit Me!", style=style, custom_id=f"{uid}-{count}-{value}")
                count += 1
                value, style = compare(count, medium_value, high_value)
                row3.add_button(label="Hit Me!", style=style, custom_id=f"{uid}-{count}-{value}")
                count += 1
            components = [row1, row2, row3]
            await message.edit(embed=embed, components=components)

    while time < 10:
        time += 1
        if time < 0:
            embed = disnake.Embed(title="Test Your Strength!",
                                  description=f"Hit as many buttons as possible in the time allotted to win!\nThe game starts in {0-time} Seconds.\n{newline.join(empty_bar)}")
        elif time == 0:
            for i in range(3):
                row1.add_button(label="Hit Me!", style=disnake.ButtonStyle.primary, custom_id=f"{uid}-{count}-{value}")
                count += 1
                row2.add_button(label="Hit Me!", style=disnake.ButtonStyle.primary, custom_id=f"{uid}-{count}-{value}")
                count += 1
                row3.add_button(label="Hit Me!", style=disnake.ButtonStyle.primary, custom_id=f"{uid}-{count}-{value}")
                count += 1
            components = [row1, row2, row3]
            strength_display = newline.join(empty_bar)
            embed = disnake.Embed(title="Test Your Strength!",
                                  description=f"Hit as many buttons as possible in the time allotted to win!\nThe game ends in {10-time} Seconds.\n{strength_display}")
        else:
            embed = disnake.Embed(title="Test Your Strength!",
                                  description=f"Hit as many buttons as possible in the time allotted to win!\nThe game ends in {10-time} Seconds.\n{strength_display}")
        await message.edit(embed=embed, components=components)
        await asyncio.sleep(1)

    tickets = strength*20
    if strength >= 40:
        if strength == 50:
            tickets = int(tickets*1.25)
        embed = disnake.Embed(title="Test Your Strength!", description=f"Game Over!\nWow! You're pretty strong! You earned {tickets} Tickets!\n{strength_display}")
    else:
        embed = disnake.Embed(title="Test Your Strength!", description=f"Game Over! You earned {tickets} Tickets!\n{strength_display}")
    db.award_tickets(tickets, member, "Test Your Strength")
    embed.add_field(name="Tickets", value=f"You now have {db.get_tickets(member)} Tickets")
    await message.edit(embed=embed, components=[])
    return