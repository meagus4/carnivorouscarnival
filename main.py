import datetime
import importlib
import json
import os
import sys
import time
import typing
import random
from config import load_config
import fastapi
from fastapi import responses
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import database
db = database.Database()
import idtools
tokentools = idtools.Token()
from carnival_types import *
from disnake.ext.commands import Bot, when_mentioned, option_enum
import disnake.ext.tasks as tasks
import random

from load_games import PrivateGameList, PublicGameList, load_private_games, load_public_games

intents: disnake.Intents = disnake.Intents(
    guilds=True,
)

bot = Bot(command_prefix=when_mentioned, intents=intents)
gsm = None
config = load_config()

bot.shutdown = False

CORS_ORIGINS = config["cors_origins"]
# this might error if this is empty. Too bad!

docs = True
if docs:
    web = fastapi.FastAPI()
else:
    web = fastapi.FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

web.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@bot.event
async def on_ready():
    _public = await bot.fetch_channel(config['public_channel'])
    _private = await bot.fetch_channel(config['private_channel'])
    global gsm
    gsm = GameStateManager(_public, _private)
    gsm.start_timed_new_public_game.start()
    print("Ready!")

# Load games
public_game_list: PublicGameList = load_public_games()
private_game_list: PrivateGameList = load_private_games()

PrivateGameName = option_enum(
    dict((name.title(), name) for name in private_game_list.keys()))

PublicGameName = option_enum(
    dict((name.title(), name) for name in public_game_list.keys()))


class GameStateManager:
    # Time until the next public game starts.
    public_game_timer: datetime.datetime
    # Names of the Public Games currently available
    public_game_list: PublicGameList
    # Names of the Private Games currently available.
    private_game_list: PrivateGameList
    private_game_channel: disnake.TextChannel
    public_game_channel: disnake.TextChannel

    def __init__(self, _public, _private):
        self.public_game_timer = datetime.datetime.now()
        self.public_game_list = public_game_list
        self.private_game_list = private_game_list
        self.public_game_channel = typing.cast(disnake.TextChannel, _public)
        self.private_game_channel = typing.cast(disnake.TextChannel, _private)

    async def _start_new_public_game(self, game_name: str | None = None, optional_argument: str | None = None):
        target_channel = self.public_game_channel
        if game_name == None or game_name not in self.public_game_list:
            game_name = random.choice(list(self.public_game_list.keys()))
            game_name = typing.cast(str, game_name)
        game = self.public_game_list[game_name]
        await game(target_channel, bot, optional_argument)

    @bot.slash_command(name="play_public", permissions=disnake.Permissions(manage_messages=True))
    async def start_new_public_game(
            self,
            inter: disnake.ApplicationCommandInteraction | None,
            game_name: PublicGameName | None,  # type: ignore
            optional_argument: str | None = None):
        """
        Start a new game for everyone in the public channel.

        Parameters
        ----------
        game_name: The game to start.
        optional_argument: An optional argument to pass to the game.
        """
        await self._start_new_public_game(game_name, optional_argument)

    @tasks.loop(minutes=config['public_game_interval'])
    async def start_timed_new_public_game(self):
        await self._start_new_public_game()

    @bot.slash_command(name="play")
    async def start_new_private_game(
            self,
            inter: disnake.ApplicationCommandInteraction,
            game_name: PrivateGameName,  ## type: ignore - this is actually perfectly fine
            optional_argument: str | None = None):
        """
        Start a new game in a private thread.

        Parameters
        ----------
        game_name: The game you want to play.
        optional_argument: An optional argument to pass to the game.
        """

        # Prevents new games being started if Shutdown mode is enabled.
        if bot.shutdown:
            await inter.send("The bot is in a Shutdown state, new games cannot be started!", ephemeral=True)
            return

        # Ugliest bodge I've ever written, please fix
        self = typing.cast(GameStateManager, gsm)

        # I _would_ split out the isinstance checks, but pylance doesn't support narrowing like that :/
        in_thread = isinstance(inter.channel, disnake.Thread)

        parent_channel_id: int = (inter.channel.parent_id
                                  if isinstance(inter.channel, disnake.Thread)
                                  else inter.channel_id)
        game_uid = hash(
            f"{inter.author.id}{game_name}{time.time()}{random.randint(0, 1000000)}")
        game_uid += sys.maxsize + 1
        print("gameuid", game_uid)

        member = typing.cast(disnake.Member, inter.author)

        if parent_channel_id != self.private_game_channel.id:
            return await inter.send(f"You can only play games in {self.private_game_channel.mention}.", ephemeral=True)

        if not game_name or game_name not in self.private_game_list:
            buf = "Please select a valid game. Games include:\n"
            buf += "\n".join(self.private_game_list.keys())
            return await inter.send(buf, ephemeral=True)
        
        tokens = db.get_tokens(member,"private")
        if tokens <= 0:
            return await inter.send("Sorry, you're out of tokens! (Tokens return to you 3 hours after you use them)", ephemeral=True) 

        existing_thread = db.get_thread_for_user(typing.cast(disnake.Member, inter.author))
        if existing_thread:
            pthread = typing.cast(disnake.Thread, await bot.fetch_channel(int(existing_thread)))
        else:
            pthread = await self.private_game_channel.create_thread(name=f"{inter.author.name}'s game channel", type=disnake.ChannelType.private_thread)
            db.add_thread_for_user(typing.cast(disnake.Member, inter.author), pthread)


        if in_thread:
            await inter.send(f"Starting {game_name}...\n You have {tokens} tokens left.")
        else:
            await pthread.send(f"Starting {game_name}... {inter.author.mention}")
            await inter.send(f"Check {pthread.mention}. You have {tokens} tokens left.", ephemeral=True)

        game = self.private_game_list[game_name]
        db.consume_tokens(1, member,game_name, "private")
        await game(pthread, typing.cast(disnake.Member, inter.author), bot, str(game_uid), optional_argument)

    @bot.slash_command(name="shop")
    async def shop(self, inter: disnake.ApplicationCommandInteraction):

        from database import Database
        db2 = Database()  # Initialise the fucking singleton

        shopkeepers = [
            "https://media.discordapp.net/attachments/1164778377002090566/1164814503427452938/latest.png?ex=6544950a&is=6532200a&hm=215d0afa662dc5b8575016063344a2a42b69613c748cb5df99a098493278d8f6&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814503737839747/latest.png?ex=6544950a&is=6532200a&hm=b40d4a2933881af67dcd967be4684b697a356c73444505d2105e157d69065f6e&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814504056598578/latest.png?ex=6544950a&is=6532200a&hm=39dd8f3139deeb4fd5faa2004b97fbad722e040707da49725dbf060c906bd05c&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814504341819452/latest.png?ex=6544950b&is=6532200b&hm=6a2a1115d19ca17469f094fc6120973e9307cc9b19ecc5c18bba3e81a46dd486&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814504710901832/latest.png?ex=6544950b&is=6532200b&hm=85a0c92e9fb4ce23e9cb7000d28b07fbd3665e970cf72049f34dda0d5eac97dd&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814505075814430/latest.png?ex=6544950b&is=6532200b&hm=086229b385df7c28d0b2ea59575fd6bbac5a06da6eec63ce58408c0f300caf2c&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814505331675196/latest.png?ex=6544950b&is=6532200b&hm=1fa5613395abc24718e00cd47b8c6abfb0e18233f7ed054862120a0f7ddd059c&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814505604288552/latest.png?ex=6544950b&is=6532200b&hm=905cba0baa5f1f59735732ca969a2ac9b2d1249203124901135a04560b428634&=",
            "https://media.discordapp.net/attachments/1164778377002090566/1164814505973403658/latest.png?ex=6544950b&is=6532200b&hm=0626bfaa5dbb8a3a0a68ec66df0261b9d59155405c0fb0675fd42f1b17611308&="
        ]

        # Gets All Shop Items (Rarity 0)
        bad_items_cur = db.db.execute("select * from prizes where rarity = 0")
        bad_items = bad_items_cur.fetchall()

        # Gets All Shop Items (Rarity 1)
        less_bad_items_cur = db.db.execute("select * from prizes where rarity = 1")
        less_bad_items = less_bad_items_cur.fetchall()

        # Gets the current random seed for this user.
        now = datetime.datetime.now()
        hour = 0
        if now.hour >= 18:
            hour = 18
        elif now.hour >= 12:
            hour = 12
        elif now.hour >= 6:
            hour = 6
        time_seed = f"{now.day}{hour}{inter.author.id}"

        # Builds the Embed

        embed = disnake.Embed(title="Welcome to the SHOP!", description="Buy yourself some DISCOUNT prizes!!")
        embed.add_field(name="1000 Tickets | Prize Crate", value="Guaranteed to contain a prize of some sort.\nWarning: Content Quality is not Guaranteed.")
        shop_menu = disnake.ui.Select()

        random.seed(time_seed)
        random.shuffle(bad_items)
        current_prizes = bad_items[:4]
        current_prizes.append(random.choice(less_bad_items))

        for prize in current_prizes:
            embed.add_field(name=f"{(prize[3]+1)*500} Tickets | {prize[1]} ({rarities[prize[3]]})", value=prize[2])
            shop_menu.add_option(value=f"{prize[0]}", label=f"{prize[1]} ({(rarities[prize[3]])})", description=f"Buy this for {(prize[3]+1)*500} Tickets")
        shop_menu.add_option(value="1000", label="1000 Tickets | Prize Crate", description="Warning: Content Quality is not Guaranteed.")
        shop_menu.custom_id = time_seed
        embed.set_image(random.choice(shopkeepers))
        random.seed(hash(time.time()))
        await inter.send(embed=embed, ephemeral=True, components=shop_menu)

        @bot.listen("on_dropdown")
        async def on_prize_select(inter2: disnake.MessageInteraction):
            if inter2.data.custom_id == time_seed:
                data = int(inter2.data.values[0])

                user_tickets = db.get_tickets(inter2.author)

                if data == 1000:
                    if user_tickets < 1000:
                        await inter2.send(f"You do not have enough tickets to purchase this prize! This prize costs 1000 Tickets, but you've only got {user_tickets}!", ephemeral=True)
                        return
                    else:
                        chance = random.randint(1,20)
                        if chance <= 7:
                            rarity = 0
                        elif chance <= 14:
                            rarity = 1
                        elif chance <= 18:
                            rarity = 2
                        else:
                            rarity = 3
                        prize, = db.award_random_prize(inter.author, "Shop", rarity)
                        prize_data = db.get_prize(prize)
                        await inter2.send(f"You have purchased a Loot Box!\nInside the loot box you find a **{rarities[prize_data[3]]}{prize_data[1]}**!\nYou can view your new prize with `/inv`", ephemeral=True)
                else:
                    prize_list_cur = db.db.execute("select * from prizes")
                    prize_list = prize_list_cur.fetchall()
                    selected_prize = prize_list[data-1]
                    prize_cost = (selected_prize[3]+1)*500
                    if user_tickets < prize_cost:
                        await inter2.send(f"You do not have enough tickets to purchase this prize! This prize costs {prize_cost} Tickets, but you've only got {user_tickets}!", ephemeral=True)
                        return
                    else:
                        db.award_prize(inter2.author, 'Shop', data)
                        db.award_tickets((0-prize_cost), inter2.author, 'Shop')
                        await inter2.send(f"Congratulations! You have obtained a {selected_prize[1]}!\nYou can view your inventory with `/inv`", ephemeral=True)

    @bot.slash_command(name="inv")
    async def inventory(self, inter: disnake.ApplicationCommandInteraction):

        prizes = db.get_prize_wins_by_user(inter.author)
        uid = hash(f"{inter.author.id}Inventory{time.time()}{random.randint(0, 1000000)}")
        current_id = 0

        prize_data = db.get_prize(prizes[current_id])
        embed = disnake.Embed(title="Inventory Viewer!", description=f"Viewing your {prize_data[1]}")
        embed.set_image(prize_data[5])
        message = inter.send(embed=embed, ephemeral=True)
        @bot.listen("on_button_press")
        async def inventory_press(inter2: disnake.MessageInteraction):
            if inter2.data.custom_id.startswith(uid):
                pass

    @bot.slash_command(name="shutdown", permissions=disnake.Permissions(manage_messages=True))
    async def shutdown(self, inter):
        await inter.send("The bot will shut down in 5 Minutes! Any ongoing games will be ended, and your tokens will not be refunded!\nPlease finish any games that you are currently playing!\nNOTE: New Games cannot be started during the shutdown period.")
        bot.shutdown = True
        await asyncio.sleep(300)
        await inter.send("Goodbye!")
        exit(99)

@web.get("/api/consume_session")
async def consume_session(session: str):
    """
    Discord's play game tokens are single-use. Use this endpoint to validate and burn a token.
    """
    if not tokentools.decrypt_token(session):
        return responses.JSONResponse({"valid": False, "reason": "Malformed/foreign session token."}, status_code=400)
    valid = db.play_web_game_session(session)
    return responses.JSONResponse({"valid": valid}, status_code=200 if valid else 400)

@web.get("/api/submit_session")
async def submit_session(session: str, game_name: str, score: str):
    """
    Submit a completed game using your session token. Games can be submitted *once*.
    """
    # i don't know why we validate the token in this module for the
    # function immediately above, but for submitting game results the validation
    # is already baked into the DB validation method in the other module.
    # 2 am programming, i guess.

    valid, reason = db.submit_game_results(session, int(score))

    token = tokentools.decrypt_token(session)

    tickets = 0
    if valid:
        try:
            user = await bot.get_or_fetch_user(token['user']['id'])
        except:
            return responses.JSONResponse({"valid": False, "reason": "Discord: Unable to fetch user"}, status_code=400)
        db.award_tickets(int(score), typing.cast(disnake.Member,user), game_name)
        tickets = db.get_tickets(typing.cast(disnake.Member,user))
    return responses.JSONResponse({"valid" : valid, "reason": reason,"tickets": tickets}, status_code=200 if valid else 400)


if __name__ == '__main__':
    print("CarniverousCarnival: THIS INSTANCE IS NOT RUNNING THE API CORRECTLY!")
    print("PLEASE START THE BOT BY LOADING UVICORN")
    print("python -m uvicorn main:web")
    bot.run(open('token.txt', encoding="utf8").read())
else:
    print("CarniverousCarnival: Running as a dependency, likely from Uvicorn.")
    print("If you're doing web debug I'd encourage you to disable Discord")
    print("-Prevents burning your tokens")


@web.on_event("startup")
def api_startup():
    '''Called by FastAPI to handle startup tasks, including starting Discord.'''
    use_discord = True
    print("Webserver up.")
    if use_discord:
        print("Starting Discord...")
        asyncio.create_task(
            bot.start(open('token.txt', encoding="utf8").read()))
        print(f"Bot up - {bot.user}")
