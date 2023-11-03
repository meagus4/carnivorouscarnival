import asyncio
import disnake
import disnake.ext.commands
import random
import typing
import string
import datetime
import database
db = database.Database()

emojimap = "🆓😀😄😁😆😅🤣😂🙂🙃😉😇🥰🤩😗🥲😋🤪🤑🤗🫢🤫🫡🤐🤨😑😏😒😬🤥🤤😴😷🤒🥴🤯🤠🥳🥸😎🧐😟😮😳🥺😨😭😱😖😤😡😈💀🤡👺👻👽👾🤖😺😹😼🙀🙈🙉🙊💢💫🎂🥚🧡💛💚💙💜"
game_delay = 300
seconds_per_turn = 20

def fmt_emoji(int) -> str:
    return emojimap[int]


def fmt_emojiboard(board: list[int]) -> str:
    if len(board) != 25:
        return f"INVALID BOARD! ({len(board)}/25) 😭😭😭😭😭\n This is a bug."
    buf = ""
    for start in range(0, 25, 5):
        buf += ''.join([fmt_emoji(x) for x in board[start:start+5]]) + "\n"
    return buf


class BingoSession:
    balls = 75
    played_balls: list[int]
    boards: dict[disnake.Member, list[int]]
    timeouts: dict[disnake.Member, datetime.datetime]
    won: bool
    buttonsalt: str
    game_message: disnake.Message
    game_embed: disnake.Embed

    def __init__(self):
        self.buttonsalt = ''.join(random.choices(string.ascii_letters, k=8))
        self.boards = {}
        self.timeouts = {}
        self.played_balls = [0]
        self.won = False

    def generate_board(self, player: disnake.Member) -> list:
        board = []
        for i in range(25):
            number = random.randrange(1, self.balls)
            while number in board:
                number = random.randrange(1, self.balls)
            board.append(number)
        self.boards[player] = board
        board[12] = 0
        return board

    def play_ball(self):
        number = random.randrange(0, self.balls)
        count = 0
        while number in self.played_balls:
            number = random.randrange(0, self.balls)
            count += 1
            if count > 500:
                raise Exception("Ran out of numbers")
        self.played_balls.append(number)
        return number

    async def generate_global_embed(self, channel: disnake.TextChannel) -> disnake.Message:
        start_time = datetime.datetime.now() + datetime.timedelta(seconds=game_delay)
        embed = disnake.Embed(title="Bingo", description="Welcome to Bingo!")
        embed.set_footer(text=f"Bingo")
        embed.set_author(name="Bingo", icon_url="")
        embed.add_field(name="Current emoji",
                        value="We haven't started yet, go get a board!\n"
                        "Take a screenshot and mark down emojis you have.\n"
                        "For phone users... grab a pencil and mark down a grid on paper to keep track.\n"
                        f"Game starts in {disnake.utils.format_dt(start_time,style='R')}", inline=False
                        )
        embed.add_field(name="Current player count:", value="0", inline=False)
        embed.add_field(name="Number of played emojis:",
                        value="0", inline=False)

        salt = self.buttonsalt
        message = await channel.send(
            embed=embed,
            components=[
                disnake.ui.ActionRow(
                    disnake.ui.Button(
                        label="Get a board!",
                        custom_id=f"bingo:{salt}:make_board",
                        style=disnake.ButtonStyle.primary,
                        disabled=False),
                    disnake.ui.Button(
                        label="BINGO!",
                        custom_id=f"bingo:{salt}:bingo",
                        style=disnake.ButtonStyle.success,
                        disabled=False)
                )
            ]
        )
        self.game_message = message
        self.game_embed = embed
        return message

    async def check_bingo(self, player: disnake.Member) -> tuple[bool, str]:
        cases = [
            [0, 1, 2, 3, 4, "Top Row"],  # HRZ:1
            [5, 6, 7, 8, 9, "Second Row"],  # HRZ:2
            [10, 11, 12, 13, 14, "Third Row"],  # HRZ:3
            [15, 16, 17, 18, 19, "Fourth Row"],  # HRZ:4
            [20, 21, 22, 23, 24, "Fifth Row"],  # HRZ:5
            [0, 5, 10, 15, 20, "First Column"],  # VER:1
            [1, 6, 11, 16, 21, "Second Column"],  # VER:2
            [2, 7, 12, 17, 22, "Third Column"],  # VER:3
            [3, 8, 13, 18, 23, "Fourth Column"],  # VER:4
            [4, 9, 14, 19, 24, "Fifth Column"],  # VER:5
            [0, 6, 12, 18, 24, "Diagonal (from Top Left)"],  # DIAG:1
            [4, 8, 12, 16, 20, "Diagonal (from Top Right)"]  # DIAG:2
        ]
        board = self.boards[player]
        bingo = False
        bingo_type: str
        for case in cases:
            for pos in case:
                if type(pos) == str:
                    bingo = True
                    bingo_type = pos
                    return bingo, bingo_type
                    break
                if board[pos] not in self.played_balls:
                    break
        return (False, "NO BINGO")

    def check_lockout(self, player: disnake.Member) -> bool:
        if player in self.timeouts:
            if datetime.datetime.now() < self.timeouts[player]:
                return True
            else:
                del self.timeouts[player]
        return False


class SessionManager:
    '''Needed something to store sessions that was accessible by interactions.'''
    sessions: dict[str, BingoSession] = {}

    def get_session(self, salt):
        return self.sessions[salt]


sesmgr = SessionManager()


def __init__():
    return


async def play_game(channel: disnake.TextChannel, bot: disnake.ext.commands.Bot, optional: str | None = None):
    session = BingoSession()
    game_message = await session.generate_global_embed(channel)
    sesmgr.sessions[session.buttonsalt] = session
    won = False

    @bot.listen("on_button_click")
    async def on_button_click(interaction: disnake.MessageInteraction):
        identifier = typing.cast(str, interaction.component.custom_id)
        if not identifier.startswith(f"bingo:"):
            return
        game, salt, button = identifier.split(":")
        player = typing.cast(disnake.Member, interaction.author)
        session = sesmgr.get_session(salt)
        # Check if Player locked out
        if session.check_lockout(player):
            await interaction.send("You are locked out for falsely claiming a bingo! Please wait until your lockout expires before before trying again.", ephemeral=True)
            return

        if button == "make_board":
            board = []
            if player in session.boards:
                board = session.boards[player]
            else:
                board = session.generate_board(
                    typing.cast(disnake.Member, interaction.author))

            await interaction.send(fmt_emojiboard(board), ephemeral=True)
            session.game_embed.set_field_at(
                1, name="Current player count:", value=f"{len(session.boards)}")
            await session.game_message.edit(embed=session.game_embed)
            return

        if button == "bingo":
            won, bingo_type = await session.check_bingo(typing.cast(disnake.Member, interaction.author))
            if won:
                await channel.send(f"{player.mention} won the game by completing: \"{bingo_type}\"!")
                session.game_embed.set_field_at(
                    0, name="Current emoji", value=f"The game has ended.{player.mention} won 1000 tickets.")
                session.won = True
                db.award_tickets(1000, player, "Bingo")
            else:
                await interaction.send("You didn't have a bingo! You've been prevented from calling \"Bingo\" for two minutes", ephemeral=True)
                session.timeouts[player] = datetime.datetime.now(
                ) + datetime.timedelta(minutes=2)

    await asyncio.sleep(game_delay)
    while not session.won:
        try:
            ball = session.play_ball()
        except:
            session.game_embed.set_field_at(
                0, name="Current emoji", value="The game has ended and nobody won!")
            await session.game_message.edit(components=[], embed=session.game_embed)
            sesmgr.sessions.pop(session.buttonsalt)
            return
        session.game_embed.set_field_at(
            0, name="Current emoji", value=f"{fmt_emoji(ball)}")
        session.game_embed.set_field_at(
            1, name="Current player count:", value=f"{len(session.boards)}")
        session.game_embed.set_field_at(
            2, name="Number of played emojis:", value=f"{len(session.played_balls)}")
        await session.game_message.edit(embed=session.game_embed)
        await asyncio.sleep(seconds_per_turn)
    sesmgr.sessions.pop(session.buttonsalt)
