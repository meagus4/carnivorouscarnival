import asyncio
import random
import time
import database

db = database.Database()
import disnake.ext.commands

action_to_process = False

enemy_list = {
    ':ghost: :crossed_swords: :ghost:': {'name': 'Dueling Ghouls',
                                         'description': 'They seem to be more focused on each other than on you...'},
    ':merman::skateboard::merman:': {'name': 'Merbros',
                                     'description': 'You\'re not sure how they are standing, but they\'re both on the board, each kicking off one side.'},
    '<a:krisnite:508437089130512416> <:susieSlap:890360533566492712>': {'name': 'KRIS WHERE THE FUCK ARE WE?',
                                                                        'description': 'They seem to be lost, but have decided to attack you anyway. So much for asking for directions.'},
    '🦷': {'name': 'Trickor-Teeth', 'description': 'It doesn\'t seem to believe in dentists. Or hygiene. '},
    '🎃 🍮': {'name': 'Jack-O-Flantern', 'description': 'Doesn\'t emit light, just a sickly-sweet smell.'},
    '👹 🐎': {'name': 'Poni', 'description': 'It is neither little, nor under your ownership.'},
    '🐌': {'name': 'Pale Snale', 'description': 'Actually prefers a good lager.'},
    '🕴️🦞🚬 🕴️': {'name': 'The Lobfather', 'description': 'Mobster with a lobster'},
    '<:wormie:887839709672407072>': {'name': 'Wormie',
                                     'description': 'You can\'t tell if that\'s an eye or a nose, but it\'s horrifying either way.'},
    ':hole:': {'name': 'A Hole', 'description': 'Bottomless? Maybe, but I wouldn\'t try to find out myself.'},
    '<:napstablook:278804489639690241>': {'name': 'a friend',
                                          'description': 'This ghosts idea of friendship seems to be a fight to the death. Perhaps it\'s time to set them right. By killing them.'},
    '<:mimic:902037857269608478>': {'name': 'Mimic',
                                    'description': 'An ordinary chest! Why don\'t you go closer to see if there\'s any Tickets inside..?'},
    ':eggplant:': {'name': 'Suspicious Plant',
                   'description': 'For legal reasons, you are not allowed to say what this vegetable resembles.'},
    '🌜🌚🌛': {'name': 'Broken Moon',
            'description': 'It broke apart to reveal that there was a moon inside the moon all along!'},
    '<:madDummyBro:764589495379034162>': {'name': 'Bruh Dummy',
                                          'description': 'The long-lost cousin of someone you think you met once. Don\'t scare it away again!'},
    '🙊 🙊': {'name': 'Snickers',
            'description': 'These monkeys seem to be having far too much fun considering the circumstances.'},
    ':green_square: :skull_crossbones: :green_square:': {'name': 'Dancing Greenscreen Skeleton',
                                                         'description': "Thinks you're in for a bad chroma-key"},
    ':race_car: :police_car:': {'name': 'Hot Pursuit', 'description': 'They feel a need... a need for...'},
    ':flag_gb:': {'name': 'The British Empire',
                  'description': 'You\'re surprised there\'s still enough government left to fight you.'},
    ':heart:': {'name': 'DETERMINATION',
                'description': 'Fighting the abstract concept of determination fills you with determination'},
    '<:botsanstroll:902416763478761474>': {'name': '\"Sans\"', 'description': 'Thinks you\'re in for a bad troll.'},
    '<:sansbadtime:278804488889040896>': {'name': 'Sans', 'description': 'Thinks you\'re in for a bad fight.'},
    ':red_circle::knife:     :blue_circle:': {'name': 'Crewmates',
                                              'description': 'Several are pointing fingers at you and shouting accusations while another runs around stabbing various other ones in the back.'},
    ':hedgehog: :ring: :ring: :ring:': {'name': 'Sonic The Hedgehog',
                                        'description': 'What he lacks in good games, he has in fandom. Careful before the Sonic Mania gets to you!'},
    ':tophat:\n:bat:': {'name': 'Bat in a Hat', 'description': 'A bat in a hat and that is that.'},
    '💉🌻': {'name': 'The Experiment',
           'description': 'An experiment gone-wrong. He insists he has a name, but you care not for his feelings, for he has none.'},
    ':adhesive_bandage::head_bandage:': {'name': 'DIY Mummy', 'description': 'Available in all good hardware stores.'},
    '⚱️🚬': {'name': 'Pot Smoker', 'description': 'We\'re not sure what happens when you smoke ceramics either.'},
    ':nut_and_bolt::man_zombie::nut_and_bolt:': {'name': 'It\'s Alive!',
                                                 'description': 'This isn\'t the monster. Frankenstein was the real monster. But it\'s still going to attack you anyway, so keep up your guard!'},
    ':peach:': {'name': 'Suspicious Fruit', 'description': 'Presently resides in another castle.'},
    ':gun::monkey_face:': {'name': 'Monkioso', 'description': 'The lobster is their cousin.'},
    ':skull::skull::adhesive_bandage::skull::skull:': {'name': 'Skeleton Band',
                                                       'description': 'They all seem to be held together by a large band-aid, moving as a group to attack you as one!'},
    '<:crow1:903391005246619658><:crow2:903391005108215868><:crow3:903391005053698088><:crow4:903391005045309480><:crow5:903391004953042945><:crow6:903391004776882210>': {
        'name': 'A Murder of Crows', 'description': 'Having an identity crisis.'},
    '🥜 🛒': {'name': 'Nutdealer', 'description': 'Also a bit of a lute nerd.'},
    '<:spamdude:903964210533388369>': {'name': '{{NUMBER 2 RATED SALESMAN 1997}}',
                                       'description': 'The flavour text keeps getting caught in your spam filter.'},
    '🐀🐀🐀🐀': {'name': 'Rat King',
             'description': 'In another world, perhaps one of them would be a chef. Target the big one - he\'s making the rules!'},
    '💀''🌀': {'name': 'funny skeleton', 'description': 'Thinks you\'re in for a bad time.'},
    '🦊🚁': {'name': 'Tails the Fox', 'description': 'Child Genius who didn\'t think to bring a weapon to this duel.'},
    '🔶': {'name': 'Orange Star', 'description': 'We haven\'t told him what stars look like.'},
    '👨🐱👩🚀': {'name': 'Team Rocket', 'description': 'Surrender now, or prepare for a fight.'},
    '🪩🕺': {'name': 'Saturday Fright Fever',
           'description': 'You both agree Friday is the worst day of the week, but they\'re still feeling up for a fight!'},
    '🫲🪬🫱': {'name': 'The Handy Man', 'description': 'Wouldn\'t mind another if you\'re interested.'},
    '🧌 🧙‍♂️⚔': {'name': '\"You Encounter Some Undertale Fans In The Brush...\"',
                'description': 'They seem to think that this is some sort of game. Show them your might!'},
    '🫙': {'name': 'Forbidden Container',
          'description': 'You really don\'t want to know. Destroy it to keep the knowledge from future generations!'},
    '🫳 🏀': {'name': 'The Bron Jame', 'description': 'It\'s not playing ball.'},
    '🛵🐋': {'name': 'Moby-lity scooter', 'description': 'Seems like you\'re in for a whale of a time.'},
    '🧌📔': {'name': 'Lore Goblins', 'description': 'About to throw the book at you.'},
    '<:sansBadTime:278804488889040896> :door: <:sansWink:278804488897429504>': {'name': 'hall o\' ween',
                                                                                'description': 'Offers a spooky time'},
    '🤓📖': {'name': 'Pedantic Peddler',
           'description': '\"uhm akshually didn\'t you guysh do this event LAST year??\"\nHe may be right, but show him what-for anyway!'},
    '🙈🙉🙊': {'name': 'Mystic Monkeys',
            'description': 'When one of these monkeys changes the position of their hands, the others cycle around to match...'},
    '🏒♞🥍': {'name': 'The Sunday Knight Sports Game',
            'description': 'This knight is armed to the teeth with various sports equipment. Watch out for flying spheres!'},
    '💽📼🎞️': {'name': 'Attack of the 30-Year-Old Media Formats!',
             'description': 'They swear they\'re not outdated, but they can\'t seem to find something to play themselves in.'},
    '🍞👻': {'name': 'Toast Ghost', 'description': 'Haunting is his bread and butter.'},
    '👖👻': {'name': 'Pants\'em Phantom',
           'description': 'Keep an eye on your pants, or he\'ll pull \'em down for bants!'},
    '<:sink:1033110747871465512>🚽🛀': {'name': 'Drain Gang', 'description': 'This fight is sure to be draining.'},
    '📦🦊': {'name': 'Box Fox',
           'description': 'This anthropomorph intermittently transmogrifies into an immobile cube. Surely, some designer thought it was a good idea.'},
    '🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️🕵️': {'name': 'The Convocation',
                                     'description': 'Appearing from beyond the shadows, you\'re sure this is a reference to something. Perhaps it\'s time for them to ride home.'},
    '🤘🤖🤘': {'name': 'Death Metal', 'description': 'It\'s edgy! Literally! Don\'t get cut!'},
    '🥳🎉': {'name': 'Premature Victory',
           'description': 'It\'s already cutting a cake labelled \"Congrats on winning the fight!\"'},
    '🫥👅': {'name': 'Cut and Taste',
           'description': 'Left in its wake is a trail of bland apples, and one overripe one in its hand...'},
    '🍟🍟': {'name': 'Small Potatoes',
           'description': 'They keep asking "do you think you\'re better than me?" No matter your answer, they get more angry!'},
    '<:sansta:1022652448730529913>🎄': {'name': 'Hey, wait a minute...', 'description': 'IT\'S F%&#ING OCTOBER'},
    '<:tinyGoat:746489342700290108><:tinySheep:746488928432816209>': {'name': 'Comically Small Ruminants',
                                                                      'description': 'One is ramming lightly into your leg. The other is trying to get a vantage point with a nearby stepladder.'},
    '<:tobyDog:278804489383706624>': {'name': 'Tony Fox', 'description': 'Claims to be a professional scater.'},
    '💪🐉': {'name': 'Beefy-Armed Dragon', 'description': 'Legend calls him "The Burninator."'},
    '🏊‍♂️♨️🏊‍♂️  ': {'name': 'Two Bros, Chilling In A Hot Tub',
                     'description': 'Five feet apart, because they\'re Not Gay™️.'},
    '<:smol:906983749495959573>': {'name': 'Smol Bot',
                                   'description': 'Still recovering from her wounds, but she\'s still putting up a fight!'},
    ':knife::cook:': {'name': 'Chefioso', 'description': 'The secret ingredient is crime.'}
}


def getCandies(user: disnake.Member):
    db.get_tickets(user)


def addCandies(user, n_candy):
    db.award_tickets(n_candy, user, "Battle")


def getEnemy():
    global enemy_list
    sel = random.choice(list(enemy_list.items()))
    return sel


def getFlavour(monster):
    flavour_list = [
        f'{monster} attacks!',
        f'{monster} wanders by!',
        f'{monster} crossed your path!',
        f'{monster} stakes their claim!',
        f'{monster} fights back!',
        f'{monster} has decided your fate!',
        f'{monster} takes a stab!',
        f'{monster} remembers where they are!',
        f'{monster} took a wrong turn!',
        f'{monster} committed piracy!',
        f'{monster} pinged everyone!',
        f'{monster} repeated 4 times!',
        f'{monster} draws near!',
        f'You are confronted by {monster} and its cohorts.',
        f'{monster} hasn\'t paid their taxes!',
        f'{monster} emerges from the earth!',
        f'{monster} wakes up from a nightmare!',
        f'{monster} forgets what day it is!',
        f'{monster} thinks this is a prank..?',
        f'{monster} jumpscares you!',
        f'{monster} readjusts their Halloween mask.',
        f'{monster} befriends your mom!',
        f'{monster} wavedashes towards you!',
        f'{monster} shuffles towards you!',
        f'{monster} comes out to play!',
        f'{monster} confronts you!',
        f'{monster} draws near!',
        f'Oops! All {monster}!',
        f'Wild {monster} appeared!',
        f'You were accosted by {monster}!',
        f'{monster} has come to make an announcement.',
        f'{monster} has some Kromer!',
        f'{monster}, on the scene!',
        f'There\'s a {monster} among us!',
        f'{monster} broke TOS!',
        f'{monster} explodes gently.',
        f'{monster} exists in your general direction.',
        f'{monster} RPs in your general chat!',
        f'{monster} drinks all your iced coffee!',
        f'{monster} floats and gloats!',
        f'{monster} trips and faceplants!',
        f'{monster} thinks you\'re just playing!',
        f'{monster} chose trick!',
        f'{monster} hurls garbage at you!',
        f'{monster} comes back again!'
        f'{monster} is out of ideas!'
    ]

    valid = False

    while not valid:
        temp = random.choice(flavour_list)
        if len(temp) < 256:
            valid = True
    return temp


async def newEmbed(flavour, monster, time, health, maxhealth, actions='ATTACKS...', color=0xff0000):
    global hitpoints, old_deadlist, deadlist, enemy_list

    monster_info = enemy_list[monster]
    description = monster_info["description"]

    if min(500, 0.1 * maxhealth) > health > 1:
        health = 'LOW HP'

    alive_fighters = []
    dead_fighters = []
    t_dead_text = ''
    t_alive_text = ''
    alive_text = "Nobody is fighting!"
    dead_text = "Nobody is broke!"
    player_dead = False
    player_alive = False
    if len(hitpoints) < 1:
        alive_text = "Nobody has entered this battle!"
        dead_text = "Nobody is broke!"
    else:
        for i in hitpoints:
            temp_hp = hitpoints[i]
            if temp_hp <= 0:
                player_dead = True
                if i not in deadlist:
                    deadlist.append(i)
                if len(t_dead_text) >= 900:
                    t_dead_text = f'{t_dead_text}(+ more...)'
                    break
                the_user = await bot.get_or_fetch_user(i)
                t_dead_text = f'{t_dead_text}{the_user.name} (0/100 HP)\n'
            else:
                player_alive = True
                if len(t_alive_text) >= 900:
                    t_alive_text = f'{t_alive_text}(+ more...)'
                    break
                user = await bot.get_or_fetch_user(i)
                if i in userList:
                    t_alive_text = f'{t_alive_text}🛑 | {user.name} ({temp_hp}/100 HP)\n'
                else:
                    t_alive_text = f'{t_alive_text}🟢 | {user.name} ({temp_hp}/100 HP)\n'

    if player_dead:
        dead_text = t_dead_text
    if player_alive:
        alive_text = t_alive_text

    embed = disnake.Embed(title=f"{flavour}",
                          description=f"{monster}", color=color)
    embed.add_field(name="Monster Information", value=description, inline=False)
    embed.add_field(name="MONSTER HP", value=f"{health} / {maxhealth}", inline=True)
    if actions: embed.add_field(name=actions, value=time, inline=True)
    embed.add_field(name="EMPLOYEES:", value="_ _", inline=False)
    embed.add_field(name="THE FIGHTERS", value=alive_text, inline=True)
    embed.add_field(name="THE BROKE", value=dead_text, inline=True)

    return embed


difficulty = 0
old_userList = []
old_deadlist = []
deadlist = []
battleOngoing = False
monster_HP = 0
hitpoints = {}
dmgDone = {}
lastAttacker = 0
userList = []
turn = False
loss = False
fight_average = [0]


async def attackHandler(interaction):
    global monster_HP, hitpoints, lastAttacker
    if monster_HP > 0:
        m_dam, p_hp = await attack(interaction, hitpoints[interaction.author.id])
        hitpoints[interaction.author.id] = p_hp
        monster_HP = monster_HP - m_dam
    else:
        sadEmbed = disnake.Embed(title='Too Late!',
                                 description='The monster has already been killed so you cannot attack it!')
        interaction.send(embed=sadEmbed, ephemeral=True)


async def candyHandler(interaction):
    global hitpoints
    cur_can = getCandies(interaction.author)
    candyToLose = 0

    if cur_can < candyToLose:
        candyToLose = cur_can

    reward = 0
    dead_players = []

    for i in hitpoints:
        if hitpoints[i] == 0:
            dead_players.append(i)

    if len(dead_players) == 0:
        cEmbed = disnake.Embed(title=f'You try to pick up the fallen..',
                                description=f'Unfortunately, there was nobody to revive!',
                                color=0x388500)
        userList.remove(interaction.author.id)
    else:
        player = random.choice(dead_players)
        guild = interaction.guild
        user = guild.get_member(player)
        cEmbed = disnake.Embed(title=f'You spend a turn healing {user.name}.',
                               description=f'{user.name} (<@{player}>) was healed by 20 health!',
                               color=0x65EA00)
        hitpoints[player] = 20
        deadlist.remove(player)
        if player not in userList:
            userList.append(player)

    await interaction.send(embed=cEmbed, ephemeral=True)


async def healHandler(interaction):
    return await heal(interaction, hitpoints[interaction.author.id])


async def play_game(channel, bot, optional_argument=None):
    global old_userList, deadlist, old_deadlist, battleOngoing, hitpoints, monster_HP, lastAttacker, userList, turn, loss, dmgDone, fight_average, action_to_process

    old_deadlist = deadlist
    deadlist = []

    if battleOngoing:
        return

    hitpoints = {}
    dmgDone = {}
    monster, info = getEnemy()
    mname = info['name']
    flavour = getFlavour(mname)

    monster_HP_MAX = round(((len(old_userList)) * 400))

    if loss:
        monster_HP_MAX = int(monster_HP_MAX * 0.90)
    if monster_HP_MAX < 3400:
        monster_HP_MAX = 3400

    if len(fight_average) > 0:
        avg = sum(fight_average) / len(fight_average)
        print(f"Current Player Winrate: {avg}")
        if avg < 0.7:
            monster_HP_MAX = int(monster_HP_MAX - ((0.5 * monster_HP_MAX) * (1 - (avg / 2))))
        else:
            monster_HP_MAX = int(monster_HP_MAX * (1 + (avg - 0.7)))
        if len(fight_average) > 6:
            fight_average.pop(0)

    monster_HP_MAX = int(monster_HP_MAX * random.uniform(0.85, 1.35))

    if mname == 'Sans':
        monster_HP_MAX = 1

    monster_HP = monster_HP_MAX
    turnTime = 60
    battleTime = int(time.time())
    embed = await newEmbed(flavour, monster, f'...<t:{battleTime + 62}:R>', monster_HP, monster_HP_MAX)

    battleOngoing = True
    turn = True
    print(battleTime)
    turnCount = 0
    lastAttacker = None

    message = await channel.send(embed=embed, components=[
        disnake.ui.ActionRow(
            disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4),
                              disabled=False),
            disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3),
                              disabled=False))])

    @bot.listen("on_button_click")
    async def on_button_click(interaction):
        global userList, hitpoints, action_to_process

        if interaction.component.custom_id != 'attack_enemy' and interaction.component.custom_id != 'heal_player' and interaction.component.custom_id != 'throw_candy':
            return

        if turn is False and battleOngoing is True:
            await interaction.send(content="The monster is currently taking their turn so you cannot act!",
                                   ephemeral=True)
            return

        if not battleOngoing:
            await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
            userList = []
            return

        if interaction.author.id not in hitpoints:
            if interaction.author.id in old_deadlist:
                hitpoints[interaction.author.id] = 50
            else:
                hitpoints[interaction.author.id] = 100

        if hitpoints[interaction.author.id] <= 0:
            await interaction.response.send_message(
                content="GAME OVER!\nYou were defeated and have been disengaged from the battle!", ephemeral=True)
            return
        if interaction.author.id in userList:
            await interaction.response.send_message(content="You have already acted this turn!", ephemeral=True)
            return
        else:
            userList.append(interaction.author.id)

        if interaction.component.custom_id == 'attack_enemy' and battleOngoing is True:
            await attackHandler(interaction)
        elif interaction.component.custom_id == 'heal_player' and battleOngoing is True:
            hitpoints[interaction.author.id] = await healHandler(interaction)
        elif interaction.component.custom_id == 'throw_candy' and battleOngoing is True:
            await candyHandler(interaction)
        else:
            await interaction.response.send_message("There's not an ongoing battle!", ephemeral=True)
            userList = []

        action_to_process = True

    while battleOngoing:
        userList = []
        if monster_HP <= 0:
            turn = False
            battleOngoing = False
            victory = True
        elif turnCount >= 10:
            turn = False
            battleOngoing = False
            victory = False
        while turn:
            await asyncio.sleep(1)
            if monster_HP <= 0:
                break
            if action_to_process:
                try:
                    await message.edit(
                        embed=await newEmbed(flavour, monster, f'<t:{battleTime + 62}:R>', monster_HP,
                                       monster_HP_MAX), components=[
                            disnake.ui.ActionRow(disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy",
                                                                   style=disnake.Color(4), disabled=False),
                                                 disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player",
                                                                   style=disnake.Color(3), disabled=False))])
                except Exception as e:
                    print("Threw Exception! ", e)
                action_to_process = False
            if battleTime + turnTime < int(time.time()):
                userList = []
                battleTime = int(time.time())
                turnCount += 1
                turn = False

        if monster_HP > 0 and turnCount < 10:
            await message.edit(components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4),
                                      disabled=True),
                    disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3),
                                      disabled=True))])
            attacking = True
            attacked = {}
            attackstring = ''

            validTargets = []
            targetList = []

            for i in hitpoints:
                if hitpoints[i] > 0:
                    validTargets.append(i)

            atkcount = round((len(validTargets)) / 4)
            if atkcount > 15:
                atkcount = 15
            elif atkcount == 0:
                attacking = False
        else:
            attacking = False
        atk_time = int(time.time())
        if attacking:
            attackstring = ''
            while atkcount > 0 and attacking:
                if len(validTargets) == 0:
                    embed = await newEmbed(f"{mname} is taking their turn!", monster,
                                     f"...<t:{int(atk_time + 7 + atkcount)}:R>", monster_HP,
                                     monster_HP_MAX, actions=f"Monster Turn ends...", color=0xFFD800)
                    embed.add_field(name=f'{mname} Tried Attacking...', value="But they weren't able to attack anyone!",
                                    inline=False)
                    attacking = False
                    break
                t_dmg = random.randrange(10, 25)
                t_crit = random.randrange(1, 100)

                targetValid = False
                while not targetValid:
                    t_attacked = random.choice(validTargets)
                    if t_attacked not in targetList:
                        targetValid = True
                        targetList.append(t_attacked)

                attacked[t_attacked] = t_dmg
                hitpoints[t_attacked] = hitpoints[t_attacked] - t_dmg
                if hitpoints[t_attacked] < 0:
                    t_dmg = t_dmg + hitpoints[t_attacked]
                    hitpoints[t_attacked] = 0
                user = await bot.get_or_fetch_user(t_attacked)
                attackstring = f'{attackstring}{await user.name} for {t_dmg} Damage!\n'
                embed = await newEmbed(f"{mname} is taking their turn!", monster, f"...<t:{int(atk_time + 16 + atkcount)}:R>",
                                 monster_HP,
                                 monster_HP_MAX, actions=f"Turn ends...:", color=0xFFD800)
                embed.add_field(name=f'{mname} attacked:', value=attackstring, inline=False)
                await message.edit(embed=embed)
                await asyncio.sleep(1)
                atkcount -= 1
            await asyncio.sleep(15)
        elif monster_HP > 0:
            embed = await newEmbed(f"{mname} is taking their turn!", monster, f"...<t:{int(atk_time + 7 + atkcount)}:R>",
                             monster_HP,
                             monster_HP_MAX, actions=f"Turn Ends...", color=0xFFD800)
            embed.add_field(name=f'{mname} tried attacking!', value="But they weren't able to attack anyone!",
                            inline=False)
            # noinspection PyTypeChecker
            await message.edit(embed=embed, components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(label="🗡️ Attack Enemy", custom_id=f"attack_enemy", style=disnake.Color(4),
                                      disabled=True),
                    disnake.ui.Button(label="💊 Heal Yourself", custom_id=f"heal_player", style=disnake.Color(3),
                                      disabled=True))])
            await asyncio.sleep(5)
        action_to_process = True

        battleTime = int(time.time())
        if turnCount < 10:
            turn = True
    await message.edit(components=None)
    if victory:
        fight_average.append(1)
        msg = f"{mname} was defeated!"
        vEmbed = await newEmbed(msg, monster, 0, 0, monster_HP_MAX, actions=False)
        reg_c = random.randrange(20, 45)

        dmg_c = random.randrange(25, 55)
        dmg_r = random.randrange(2, 4)

        bestAttacker = None
        tmpDMG = 0
        tmpUSR = 0
        for i in dmgDone:
            if dmgDone[i] > tmpDMG and lastAttacker is not i:
                tmpDMG = dmgDone[i]
                tmpUSR = i

        if tmpUSR != 0:
            user = await bot.get_or_fetch_user(lastAttacker)
            vEmbed.add_field(name='Monster Defeated',
                             value=f'{user.name} got the final hit! They have been awarded {reg_c} Tickets!\n{await bot.get_or_fetch_user(tmpUSR).name} did the most damage, with {tmpDMG} damage! They have been awarded {dmg_c} Tickets', inline=False)
        else:
            user = await bot.get_or_fetch_user(lastAttacker)
            vEmbed.add_field(name='Monster Defeated',
                             value=f'{await user.name} got the final hit! They have been awarded {reg_c} Tickets!',
                             inline=False)
        loss = False
        addCandies(user, reg_c)
        if tmpUSR != 0:
            addCandies(user, dmg_c, dmg_r)
    else:
        fight_average.append(0)
        msg = f"{mname} got away!"
        vEmbed = await newEmbed(msg, monster, -1, monster_HP, monster_HP_MAX, actions=False)
        vEmbed.add_field(name=f'{mname} Escaped', value=f'{mname} escaped, so nobody was paid! :(', inline=False)
        loss = True

    await message.edit(embed=vEmbed)

    old_userList = hitpoints.items()


async def attack(action, player_hp):
    global dmgDone, lastAttacker
    lastAttacker = action.author.id
    avg = sum(fight_average) / len(fight_average)
    attackLow = 95
    attackHigh = 175
    attackDmg = random.randrange(attackLow, attackHigh)

    if player_hp < 50:
        attackDmg = int(attackDmg * 1.25)
    elif player_hp < 25:
        attackDmg = int(attackDmg * 1.35)

    n_C = random.randrange(2, 7)

    if avg < 0.3:
        rareChance = 80
    else:
        rareChance = 98


    c_C = getCandies(action.author)

    HPLoss = random.randrange(0, 35)
    player_hp = player_hp - HPLoss

    if HPLoss > 30:
        attackDmg = int(attackDmg * 1.10)

    crit = random.randrange(1, 100)

    if avg < 0.3:
        crit = crit * 1.25

    if crit >= 95:
        attackDmg = attackDmg * 3
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xFFD800)
        pmEmbed.description = f"**CRITICAL HIT!** You deal {attackDmg} damage!\nYou won {n_C} Tickets for your mighty blow!"
        player_hp = player_hp + HPLoss
        pmEmbed.set_image(
            url='https://media.discordapp.net/attachments/669077343482019870/902003156924379156/tumblr_m0biocwpJC1rnm2iko1_500.png')
    else:
        pmEmbed = disnake.Embed(title="You attack the enemy!", color=0xD95249)

        if player_hp < 0:
            HPLoss = HPLoss + player_hp
            player_hp = 0

        if HPLoss == 0:
            dmgText = ' and take no'
        else:
            dmgText = f', but take {HPLoss}'

        pmEmbed.description = f'You deal {attackDmg} damage{dmgText} damage in return.\nYou currently have **{player_hp}/100** health remaining.\nYou were awarded {n_C} Tickets for your attack.'
    await action.send(embed=pmEmbed, ephemeral=True)

    addCandies(action.author, n_C)

    if action.author.id not in dmgDone:
        dmgDone[action.author.id] = attackDmg
    else:
        dmgDone[action.author.id] = dmgDone[action.author.id] + attackDmg

    return attackDmg, player_hp


async def heal(action, hitpoints):
    avg = sum(fight_average) / len(fight_average)

    if avg > 0.85:
        healLow = 10
        healHigh = 45
    else:
        healLow = 20
        healHigh = 60

    heal = random.randrange(healLow, healHigh)

    if hitpoints > 75:
        heal = int(heal * 0.75)

    hlEmbed = disnake.Embed(title="You take a moment to heal your wounds.", color=0x59A361)
    hitpoints = min(100, (hitpoints + heal))
    if hitpoints == 69:
        hitpoints = 70
        heal = heal + 1
    if hitpoints == 100:
        hitpoints = 100
        hlEmbed.description = "You were fully healed!\nYou have **100/100** health remaining."
    else:
        hlEmbed.description = f"You were healed by {heal} hitpoints.\nYou now have **{hitpoints}/100** health remaining."

    await action.send(embed=hlEmbed, ephemeral=True)

    return hitpoints

