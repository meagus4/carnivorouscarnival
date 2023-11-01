import asyncio

import disnake
import disnake.ext.commands
import time
import random
import database
db = database.Database()

def __init__():
    return
async def play_game(channel: disnake.TextChannel, bot:disnake.ext.commands.Bot, optional: str|None = None):
    uid = f"undertle-{int(time.time() * 1000)}"

    wordle_button = disnake.ui.Button(label="Guess the word", custom_id=uid, style=disnake.ButtonStyle.primary)
    start_embed = disnake.Embed(title="Let's Play WORDLE!", description="This is an original game idea that has never been done before.\nGuess the word!")
    message = await channel.send(embed=start_embed, components=[wordle_button])

    with open('resources/wordle-list.txt', 'r') as f:
        wordlist = f.read().splitlines()

    guesses = {}
    winners = []

    word = random.choice(wordlist)
    @bot.listen("on_button_click")
    async def on_wordle_click(interaction: disnake.MessageInteraction):
        if interaction.component.custom_id == uid:
            await interaction.response.send_modal(
                title="Undertle",
                custom_id=f"modal-{uid}",
                components=[
                    disnake.ui.TextInput(label="Guess the word", custom_id=uid, style=disnake.TextInputStyle.short)
                ]
            )

    @bot.listen("on_modal_submit")
    async def on_wordle_submit(interaction: disnake.MessageInteraction):
        nonlocal winners
        if interaction.custom_id == f"modal-{uid}":

            hidden_guess = ""

            guess = interaction.data.components[0]['components'][0]['value'].lower()

            if interaction.author in winners:
                await interaction.send("You have already guessed this word!", ephemeral=True)
                return

            if len(guess) != 5:
                await interaction.send("Your guess must be 5 letters long!", ephemeral=True)
                return
            if guess not in wordlist:
                await interaction.send("Your guess is not in the word list!", ephemeral=True)
                return

            if interaction.author.id not in guesses:
                guesses[interaction.author.id] = 5

            if guesses[interaction.author.id] <= 0:
                await interaction.send("You have no guesses left!", ephemeral=True)
                return

            guesses[interaction.author.id] -= 1

            if guess == word:
                embed = disnake.Embed(title="🟩🟩🟩🟩🟩", description=f"You guessed the word! You earned {800 - (len(winners)*100)} Tickets.")
                await interaction.send(embed=embed, ephemeral=True)
                db.award_tickets(800 - (len(winners)*100), interaction.author,  "Wordle")
                winners.append(interaction.author)

                if len(winners) == 3:
                    start_embed.add_field(name="Three People have guessed the word!", value=f"Thanks for playing! The word was {word}")
                    await message.edit(embed=start_embed, components=[])
                    bot.remove_listener(on_wordle_click)
                return

            else:
                index = 0
                for g in guess:
                    if g not in word:
                        hidden_guess += "⬛"
                    else:
                        if g == word[index]:
                            hidden_guess += "🟩"
                        else:
                            hidden_guess += "🟨"
                    index += 1
            embed = disnake.Embed(title=hidden_guess, description=f"You have {guesses[interaction.author.id]} guesses left", color=0x65EA00)
            await interaction.response.send_message(embed=embed, ephemeral=True)

            return
        else:
            return

    await asyncio.sleep(1200)
    start_embed.description = f"Time out! {len(winners)} people guessed the word\n The word was {word}"
    await message.edit(embed=start_embed, components=[])
    bot.remove_listener(on_wordle_click)
    bot.remove_listener(on_wordle_submit)
    return