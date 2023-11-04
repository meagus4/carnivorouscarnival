import asyncio
import random
import time
import disnake
import disnake.ext.commands
import database
db = database.Database()

def __init__():
    return


class Snail():

    def __init__(self, name: str):
        self.name = name
        self.progress = 0
        self.happiness = 0
        self.interacted = []
        self.friends = []

    def make_progress(self):
        self.progress += random.randint(0, 3 + self.happiness)

    def cheer(self, user):
        if user in self.interacted:
            return False

        if user in self.friends:
            self.happiness += 1
        else:
            self.happiness -= 1

        if self.happiness < -2:
            self.happiness = -2
        elif self.happiness > 5:
            self.happiness = 5

        self.interacted.append(user)
        return True


async def play_game(channel: disnake.TextChannel, bot: disnake.ext.commands.Bot, optional: str | None = None):
    # Initialize Variables for Race
    uid = f"snail-{int(time.time() * 1000)}"
    snails = []
    recent_cheers = []
    racing = False
    # Create Snails

    # Snail Name Generation
    with open('resources/names.txt', 'r') as f:
        names = f.read().splitlines()
    with open('resources/adjectives.txt', 'r') as f:
        adjectives = f.read().splitlines()

    for s in range(4):
        name = random.choice(names)
        alliteration_adjective = [i for i in adjectives if i.startswith(name[0].lower())]
        adjective = random.choice(alliteration_adjective)
        snails.append(Snail(name=f"{adjective} {name}".title()))
    del names, adjectives, alliteration_adjective

    embed = disnake.Embed(title="Snail Race", description="Cheer your snail onto victory, or slow down enemy snails!\nPick your Snail now! The race will begin in 1 minute.", color=0x0000ff)
    message = False
    # Snail Buttons
    components = []
    for s in snails:
        components.append(disnake.ui.Button(label=s.name, custom_id=uid + f"-{s.name}"))

    # Snail Button Listener
    @bot.listen("on_button_click")
    async def snail_press(inter):
        nonlocal racing
        if not inter.component.custom_id.startswith(uid):
            return

        selected_snail = inter.component.custom_id.split("-")[2]
        if not racing:
            for s in snails:

                if inter.author in s.friends:
                    s.friends.remove(inter.author)

                if s.name == selected_snail:
                    s.friends.append(inter.author)
                    await inter.send(f"{s.name} has been set as your active snail!", ephemeral=True)
        else:
            if inter.author in recent_cheers:
                await inter.send("You have already cheered a snail in the last 30 seconds! Please wait and try again", ephemeral=True)
                return
            recent_cheers.append(inter.author)
            for s in snails:
                if s.name == selected_snail:
                    s.cheer(inter.author)
                    if inter.author in s.friends:
                        action = "cheer on"
                        speed = "boost!"
                    else:
                        action = "jeer at"
                        speed = "penalty!"
                    await inter.send(f"You {action} {s.name}, giving them a small speed {speed}", ephemeral=True)
            await asyncio.sleep(30)
            recent_cheers.remove(inter.author)

    # Announce Snail Race
    message = await channel.send(embed=embed, components=components)
    timer = 60
    while timer > 0:
        timer -= 1
        await asyncio.sleep(1)
    racing = True
    embed.description = "The race is now underway! Pick your snail to give them a boost, or choose another snail to slow them down!"
    # Start Race
    while racing:
        embed.clear_fields()
        for s in snails:
            s.make_progress()

            progress_str = ""
            for i in range(81):
                if i == int(s.progress/2):
                    progress_str += "🐌"
                else:
                    progress_str += "-"
                if int(s.progress/2) >= 80 and i >= int(s.progress/2):
                    progress_str += "🎆"
                    racing = False
            embed.add_field(name=s.name, value=progress_str, inline=False)
        if message:
            await message.edit(embed=embed)
        else:
            message = await channel.send(embed=embed, components=components)
        await asyncio.sleep(1)

    # Announce Winner
    bot.remove_listener(snail_press)
    winner = max(snails, key=lambda s: s.progress)

    tickets = 120 - (len(winner.friends)-1 * 10)

    total_players = 0
    for s in snails:
        total_players += len(s.friends)
    if total_players > 10:
        total_players = 10
    tickets = tickets * total_players

    if tickets < 500:
        tickets = 500

    prizes_string = ""

    for u in winner.friends:
        db.award_tickets(tickets, u, "Snail Race")
        if random.randint(1, 100) >= 90:
            prizes_string += f"\n{u.name} has won a **GOLDEN SNAIL**!"
            db.award_prize(u, "Snail Race", 48)

    embed.description = f"The winner is {winner.name}! All supporters of {winner.name} have been rewarded with {tickets} Tickets!{prizes_string}"
    await message.edit(embed=embed, components=[])