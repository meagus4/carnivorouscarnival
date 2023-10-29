import random
import statistics
from typing import List

import disnake
import disnake.ext.commands

import database


def __init__():
    return


db = database.Database()
MIN_BET = 100
BASE_BET = 300
MAX_BET = 500
BET_STEP = 100
STARTING_PLAYS = 5
GAME_NAME = 'slots'

def ci(uid: str, str: str) -> str:
    return f"{GAME_NAME}:{uid}:{str}"


async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):
    player_tickets = db.get_tickets(member)

    if player_tickets < MIN_BET:
        return await thread.send(f'You need at least {MIN_BET} tickets to play slots!')

    plays_left = STARTING_PLAYS
    bet = min(BASE_BET, player_tickets)
    ticket_change = 0

    embed = disnake.Embed(
        title=f"🎰 SLOTS 🎰",
        description=display_slots_roll(generate_slots_roll())
    )

    embed.add_field('Win!!!', 'Get x0.25-6 times your bet!', inline=False)
    embed.add_field('Points:', points_1, inline=True)
    embed.add_field('\u200b', points_2, inline=True)

    embed.set_footer(
        text=f'{plays_left} play{"s" if plays_left != 1 else ""} left!')

    decrease_bet = disnake.ui.Button(
        custom_id=ci(uid, 'increase_bet'), label=f"-{BET_STEP}", style=disnake.ButtonStyle.blurple)
    current_bet = disnake.ui.Button(
        custom_id=ci(uid, 'play_bet'), label=f"Play Bet: {bet} Tickets", style=disnake.ButtonStyle.green)
    increase_bet = disnake.ui.Button(
        custom_id=ci(uid, 'decrease_bet'), label=f"+{BET_STEP}", style=disnake.ButtonStyle.blurple)
    bet_row = disnake.ui.ActionRow(decrease_bet, current_bet, increase_bet)
    components = [bet_row]

    @bot.listen('on_button_click')
    async def on_button_click(interaction: disnake.MessageInteraction):
        if interaction.component.custom_id is None:
            return

        if not interaction.component.custom_id.startswith(ci(uid, '')):
            # Not our game
            return

        nonlocal player_tickets
        nonlocal bet
        nonlocal plays_left
        nonlocal ticket_change

        if interaction.user != member:
            return await interaction.send("You didn't start this game!", ephemeral=True)

        player_tickets = db.get_tickets(member)

        if interaction.component.custom_id == current_bet.custom_id:
            if plays_left <= 0:
                return await interaction.send("You're out of plays!", ephemeral=True)

            if bet > player_tickets:
                return await interaction.send("You don't have enough tickets!", ephemeral=True)

            roll = generate_slots_roll()
            embed.description = display_slots_roll(roll)
            points = calculate_points(roll)
            multiplier = calculate_tickets_multiplier(points)
            won_tickets = round(bet * multiplier)

            tickets_won_name = 'Tickets Won:'

            #  Get the index of the previous "Ticket Won" field, if any:
            ticket_won_field_idx = next((i for i, field in enumerate(
                embed.fields) if field.name == tickets_won_name), None)

            change = won_tickets - bet
            ticket_change += change
            tickets_won_line = f'You got {points} points (x{round(multiplier, 2)})!\nYou won {won_tickets} tickets!\n(You got {ticket_change} so far!)'

            db.award_tickets(change, member, GAME_NAME)
            player_tickets = db.get_tickets(member)

            if ticket_won_field_idx is not None:
                embed.set_field_at(
                    ticket_won_field_idx, name=tickets_won_name, value=tickets_won_line, inline=False)
            else:
                embed.add_field(
                    tickets_won_name, tickets_won_line, inline=False)

            plays_left -= 1
            embed.set_footer(
                text=f'{plays_left} play{"s" if plays_left != 1 else ""} left!')

        if interaction.component.custom_id == decrease_bet.custom_id:
            bet -= BET_STEP
            if bet < MIN_BET:
                bet = MIN_BET

        if interaction.component.custom_id == increase_bet.custom_id:
            bet += BET_STEP
            if bet > MAX_BET:
                bet = MAX_BET

        if bet <= MIN_BET or plays_left <= 0:
            decrease_bet.style = disnake.ButtonStyle.grey
            decrease_bet.disabled = True
        else:
            decrease_bet.style = disnake.ButtonStyle.blurple
            decrease_bet.disabled = False

        if bet >= MAX_BET or plays_left <= 0:
            increase_bet.style = disnake.ButtonStyle.grey
            increase_bet.disabled = True
        else:
            increase_bet.style = disnake.ButtonStyle.blurple
            increase_bet.disabled = False

        if bet > player_tickets or plays_left <= 0:
            current_bet.style = disnake.ButtonStyle.grey
            current_bet.disabled = True
        else:
            current_bet.style = disnake.ButtonStyle.green
            current_bet.disabled = False

        current_bet.label = f"Play Bet: {bet} Tickets"

        return await interaction.response.edit_message(embed=embed, components=components if plays_left > 0 else None)

    return await thread.send(embed=embed, components=components)

# Slot logic

SlotsRoll = tuple[int, int, int]
PointsDict = dict[str, int]

symbols = ['🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '⚫']
symbols_len = len(symbols)
symbols_end_idx = symbols_len - 1

symbols_points: PointsDict = {
    '🔴': 1,
    '🟠': 2,
    '🟡': 3,
    '🟢': 4,
    '🔵': 5,
    '🟣': 6,
    '🟤': 7,
    '⚫': 8,
}

points_1 = '\n'.join([f'{symbols[i]} = {symbols_points[symbols[i]]} Pts' for i in range(
    0, symbols_len // 2)])

points_2 = '\n'.join([f'{symbols[i]} = {symbols_points[symbols[i]]} Pts' for i in range(
    symbols_len // 2, symbols_len)])


def generate_slots_roll() -> SlotsRoll:
    return (
        random.randint(0, symbols_end_idx),
        random.randint(0, symbols_end_idx),
        random.randint(0, symbols_end_idx)
    )


blank = '<:empty:753399747578036246>'

offset_symbols = [
    '↘️ ',  # 0
    ' ↙️',  # 1
    f'{blank} ',  # 2
    f' {blank}',  # 3
    '➡️ ',  # 4
    ' ⬅️',  # 5
    f'{blank} ',  # 6
    f' {blank}',  # 7
    '↗️ ',  # 8
    ' ↖️',  # 9
]


def display_slots_roll(roll: SlotsRoll) -> str:
    leading = f"{offset_symbols[0]}{' | '.join([blank for _ in range(0, len(roll))])}{offset_symbols[1]}"
    trailing = f"{offset_symbols[-2]}{' | '.join([blank for _ in range(0, len(roll))])}{offset_symbols[-1]}"

    slots = "\n".join([
        offset_symbols[(offset + 2) * 2] + " | ".join([
            f"{symbols[(roll[i] + offset) % symbols_len]}"
            for i in range(0, len(roll))
        ]) + offset_symbols[(offset + 2) * 2 + 1]
        for offset in range(-1, 2)  # Show previous + next "row" of the roll
    ])

    return f"{leading}\n{slots}\n{trailing}"


def calculate_points(roll: SlotsRoll) -> int:
    # Generate a 3x3 matrix with the symbols in it
    # (the roll is the middle row)
    # Then, calculate the points for the middle row and the 2 diagonals
    # Duplicate symbols doubles/triples the points that symbols gives
    matrix: List[List[int]] = [
        [roll[0] - 1, roll[1] - 1, roll[2] - 1],
        list(roll),
        [roll[0] + 1, roll[1] + 1, roll[2] + 1]
    ]

    points = 0

    symbols_seen: dict[str, int] = {}
    # Calculate points for the middle row
    for i in range(0, len(matrix[1])):
        if map_symbol(matrix[1][i]) in symbols_seen:
            symbols_seen[map_symbol(matrix[1][i])] += 1
        else:
            symbols_seen[map_symbol(matrix[1][i])] = 1

    points += add_points(symbols_seen)

    symbols_seen = {}
    # Calculate points for the / diagonal
    for i in range(0, len(matrix)):
        if map_symbol(matrix[i][i]) in symbols_seen:
            symbols_seen[map_symbol(matrix[i][i])] += 1
        else:
            symbols_seen[map_symbol(matrix[i][i])] = 1

    points += add_points(symbols_seen)

    symbols_seen = {}
    # Calculate points for the \ diagonal
    for i in range(0, len(matrix)):
        if map_symbol(matrix[i][len(matrix) - 1 - i]) in symbols_seen:
            symbols_seen[map_symbol(matrix[i][len(matrix) - 1 - i])] += 1
        else:
            symbols_seen[map_symbol(matrix[i][len(matrix) - 1 - i])] = 1

    points += add_points(symbols_seen)

    return points


def map_symbol(idx: int) -> str:
    return symbols[idx % symbols_len]


def add_points(symbols_seen: dict[str, int]) -> int:
    points = 0
    for symbol in symbols_seen:
        points += (symbols_points[symbol] *
                   symbols_seen[symbol]) * symbols_seen[symbol]

    return points


def calculate_tickets_multiplier(x: int) -> float:
    return 4.13209876543212 - 0.419032186948856*x + 0.0146016865079366*x**2 - 0.000183446318342152*x**3 + 7.84005731922401*10**(-7)*x**4


if __name__ == "__main__":
    bet = BASE_BET

    roll = generate_slots_roll()
    print(display_slots_roll(roll))
    points = calculate_points(roll)
    print('points', points)
    multiplier = calculate_tickets_multiplier(points)
    won_tickets = round(bet * multiplier)

    print('Tickets Won:', won_tickets, 'Tickets')
