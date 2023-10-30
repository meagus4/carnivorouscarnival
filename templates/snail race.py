import asyncio
import random
import time
import disnake
import disnake.ext.commands


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
    uid = f"snail-{int(time.time() * 1000)}"
    snails = []

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

    embed = disnake.Embed(title="Snail Race", description="Cheer your snail onto victory!", color=0x0000ff)
    racing = True
    message = False

    # Start Race
    while racing:
        embed.clear_fields()
        for s in snails:
            s.make_progress()

            progress_str = ""
            for i in range(80):
                if i == s.progress:
                    progress_str += "🐌"
                else:
                    progress_str += "-"
            embed.add_field(name=s.name, value=progress_str, inline=False)
        if message:
            await message.edit(embed=embed)
        else:
            message = await channel.send(embed=embed)
        await asyncio.sleep(1)