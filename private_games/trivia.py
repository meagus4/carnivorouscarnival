import asyncio
import random
import time

import disnake
import disnake.ext.commands
import database
db = database.Database()


def __init__():
    return


async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):
    # return await thread.send("Embed here!")

    answered = False
    player_score = 0

    @bot.listen("on_button_click")
    async def on_button_click(inter: disnake.MessageInteraction):
        nonlocal player_score, answered
        if inter.component.custom_id.startswith(uid) and answered == False:
            answered = True
            data = inter.component.custom_id.split("_")
            q = data[1]

            correct_answer = undertale_trivia_questions_and_answers[q][0]

            if inter.component.label == correct_answer:
                player_score += 1
                await inter.response.send_message(
                    content=f"Great work! You got that answer correct.\nYour score is {player_score}/{len(questions)}",
                    ephemeral=True)
            else:
                await inter.response.send_message(
                    content=f"Bad luck! You got that wrong.\nYour score is {player_score}/{len(questions)}",
                    ephemeral=True)

    undertale_trivia_questions_and_answers = {
        "What's the prize for answering correctly?": ["Tickets", "Money", "Mercy", "New Car"],
        "What's the king's full name?": ["Asgore Dreemurr", "Lord Fluffybuns", "Fuzzy Pushover", "King Charles III"],
        "Would you smooch a ghost?": ["Heck Yeah", "Heck Yeah", "Heck Yeah", "Heck Yeah"],
        "How many letters are in the name Mettaton?": ["8", "6", "11", "10"],
        "Who does Dr. Alphys have a crush on?": ["Undyne", "Asgore", "You!", "Don't Know"],
        "What's the name of the underground city in Undertale?": ["Snowdin", "Waterfall", "Hotland", "New Home"],
        "What's the name of the skeleton brothers in Undertale?": ["Sans and Papyrus", "Sans and Gaster",
                                                                   "Papyrus and Gaster", "Sans and Flowey"],
        "What's the main character's name in Undertale?": ["Frisk", "Chara", "Asriel", "Flowey"],
        "What is the name of the first human to fall into the Underground?": ["Chara", "Frisk", "Asriel", "Flowey"],
        "Who is the leader of the Royal Guard in Undertale?": ["Undyne", "Asgore", "Mettaton", "Sans"],
    }

    embed = disnake.Embed(title="METTATON'S **NEW** TRIVIA QUIZ", description="Guaranteed to have ALL NEW questions!")
    embed.color = disnake.Color.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    embed.set_image("https://static.wikia.nocookie.net/undertale/images/5/50/Mettaton_battle_box.gif")
    embed.add_field(name="Welcome to MTT-BRAND GAMESHOW #5!",
                    value="You will have 15 seconds to answer each question. Good luck!\nThe game will start in 10 seconds.",
                    inline=False)
    message = await thread.send(embed=embed)

    # await asyncio.sleep(10)

    questions = random.sample(sorted(undertale_trivia_questions_and_answers), k=10)

    num_to_iterate = 0

    for q in questions:

        answers = undertale_trivia_questions_and_answers[q].copy()

        embed.clear_fields()
        embed.title = q
        embed.description = f"**Time ends <t:{int(time.time()) + 15}:R>**"

        random.shuffle(answers)
        buttons = []
        for answer in answers:
            buttons.append(disnake.ui.Button(label=answer, style=disnake.ButtonStyle.secondary,
                                             custom_id=f"{uid}_{q}_{num_to_iterate}"))
            num_to_iterate += 1
        await message.edit(embed=embed, components=buttons)

        while answered is False and time.time() < int(time.time()) + 15:
            await asyncio.sleep(1)
        answered = False

    embed.title = "Congratulations, Human! I, Mettaton, have won!"
    embed.description = f"However, as a reward for getting {player_score}/{len(questions)} of my questions correct, I'm awarding you with {player_score * 100} Tickets!"
    await message.edit(embed=embed, components=[])

    db.award_tickets(player_score*100, member, "Trivia")
    # TODO: Make this give player_score*100 Tickets. Meagus.