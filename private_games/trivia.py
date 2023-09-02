import asyncio
import random
import disnake
import disnake.ext.commands

def __init__():
    return

async def play_game(thread: disnake.Thread, member: disnake.Member, optional: str|None = None):
    #return await thread.send("Embed here!")

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
    embed.add_field(name="Welcome to MTT-BRAND GAMESHOW #5!", value="You will have 15 seconds to answer each question. Good luck!\nThe game will start in 10 seconds.", inline=False)
    message = await thread.send(embed=embed)

    player_score = 0

    #await asyncio.sleep(10)

    questions = random.sample(sorted(undertale_trivia_questions_and_answers), k=10)

    for q in questions:
        #current_question =
        question = q[0]
        answers = q[1]
        correct_answer = answers[0]

        embed.remove_field[0]
        embed.add_field(name=question, value="Which one of these answers is CORRECT?")

        random.shuffle(answers)
        buttons = []
        for answer in answers:
            buttons.append(disnake.ui.Button(label=answer, style=disnake.ButtonStyle.secondary))
        await message.edit(embed=embed, components=buttons)
        await asyncio.sleep(15)