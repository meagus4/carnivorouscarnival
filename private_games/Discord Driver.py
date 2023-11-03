import asyncio
import math
import random
import database
import disnake
import disnake.ext.commands

db = database.Database()

def __init__():
    return
async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, uid: str, optional: str | None = None):

    class RoadManager():
        # Manages the road & the road state.
        def __init__(self, difficulty):
            self.difficulty = difficulty
            self.road_sections = []
            for x in range(10):
                self.road_sections.append(RoadPiece(10 - x))
            self.player_pos = (0, 0)
            self.hits = 0
            self.score = 0

        def generate_traffic(self):

            # Determines whether it will spawn traffic. Spawns traffic at a rate of (10*difficulty)%
            if random.randint(0, 100) > (10 * self.difficulty):
                return
            # Determines which lane it will spawn traffic in
            lane = random.randint(0, 1)

            # Makes sure the previous road did not have traffic in a different lane
            if self.road_sections[1].obstacles:
                if self.road_sections[1].obstacles[0] != lane:
                    return

            # Chooses the vehicle type
            vehicle = random.choice(['🚘', '🚍', '🚔', '🚖'])

            # Spawns the traffic
            self.road_sections[0].update_road((lane, vehicle))

        def progress_game(self):

            # Difficulty Adjustment
            if self.difficulty < 6 and self.score > 500:
                self.difficulty += 1
            elif self.difficulty < 7 and self.score > 800:
                self.difficulty += 1
            elif self.difficulty < 8 and self.score > 950:
                self.difficulty += 1

            reverse_list = self.road_sections.copy()
            was_hit = 0
            # Updates Player Position
            road_lane, player_index = self.player_pos

            reverse_list.reverse()
            for index, road in enumerate(reverse_list):

                to_update = {
                    'obstacle': None,
                    'shrub': None,
                    'player': None
                }

                # Updates Obstacles
                if index < len(reverse_list) - 1:

                    print(index, player_index)

                    next_road = reverse_list[index + 1]
                    if next_road.obstacles:
                        to_update['obstacle'] = next_road.obstacles
                        next_road.update_road(obstacle=None)
                    if index == player_index:
                        to_update['player'] = road_lane

                was_hit += road.update_road(**to_update)

            if was_hit >= 1:
                self.score = int(0.8*self.score)
                self.hits += 1
            else:
                self.score += 10

        def generate_shrubs(self):
            pass

        def get_current_road(self):
            current_road = ''
            for road in self.road_sections:
                current_road += road.road_str
                current_road += '\n'
            return current_road
    class RoadPiece():
        # Each individual road piece.
        def __init__(self, index):
            self.index = index
            outside = index
            inside = 12-index

            self.obstacles = None
            self.shrubs = []
            self.updated = False
            self.lane_1 = f"{' '*outside}/{' '*inside}"
            self.lane_2 = f"{' '*inside}\\{' '*outside}"
            self.road_str = f"{self.lane_1}|{self.lane_2}"

        def update_road(self, obstacle:tuple | None = None, shrub:tuple | None = None, player:int | None = None):

            hits = 0 # Will return 1 if the player got hit this turn.

            # Sets up inside & outside of road.
            self.updated = True
            outside = self.index
            inside = 12-self.index

            self.obstacles = obstacle
            self.shrubs = shrub

            # Sets up the Lanes

            self.lane_1 = f"{' '*outside}/{' '*inside}"
            self.lane_2 = f"{' '*inside}\\{' '*outside}"

            # Adds Obstacles
            if self.obstacles:
                obstacle_position = inside / 2
                if self.obstacles[0] == 0:
                    if player == 0:
                        player = None
                        hits = 1
                        self.obstacles = (self.obstacles[0], '💥')


                    # Obstacle in the LEFT lane

                    obstacle_position += outside

                    # Rounds up to make it even with the right lane.
                    obstacle_position = math.ceil(obstacle_position)
                    temp_slice = list(self.lane_1)
                    temp_slice[obstacle_position+1] = '' # Accounts for 2-width of Emoji
                    temp_slice[obstacle_position] = self.obstacles[1]
                    self.lane_1 = ''.join(temp_slice)
                else:
                    if player == 1:
                        player = None
                        hits = 1
                        self.obstacles = (self.obstacles[0], '💥')

                    # Obstacle in the RIGHT lane

                    # Rounds down to make it even with left lane
                    obstacle_position = math.floor(obstacle_position)
                    temp_slice = list(self.lane_2)
                    temp_slice[obstacle_position-1] = '' # Accounts for 2-width of Emoji
                    temp_slice[obstacle_position] = self.obstacles[1]
                    self.lane_2 = ''.join(temp_slice)

            # Adds Player
            if player == 0:
                player_position = inside / 2
                player_position += outside
                player_position = math.ceil(player_position)
                temp_slice = list(self.lane_1)
                temp_slice[player_position + 1] = ''  # Accounts for 2-width of Emoji
                temp_slice[player_position] = '❤️'
                self.lane_1 = ''.join(temp_slice)
            elif player == 1:
                player_position = inside / 2
                player_position = math.floor(player_position)
                temp_slice = list(self.lane_2)
                temp_slice[player_position - 1] = ''  # Accounts for 2-width of Emoji
                temp_slice[player_position] = '❤️'
                self.lane_2 = ''.join(temp_slice)
            # Draws the Road
            self.road_str = f"{self.lane_1}|{self.lane_2}"
            return hits

    road_manager = RoadManager(5)

    game_active = True
    message = await thread.send(f"```Initializing 80's RACER...```")
    up = disnake.ui.ActionRow()

    # Builds the arrow keys
    middle = disnake.ui.ActionRow()

    # Top Row
    up.add_button(label=f'⠀', disabled=True, style=disnake.ButtonStyle.grey)
    up.add_button(label='↑', custom_id=f"{uid}-up", style=disnake.ButtonStyle.blurple)
    up.add_button(label=f'⠀', disabled=True, style=disnake.ButtonStyle.grey)

    # Middle Row
    middle.add_button(label='←',  custom_id=f"{uid}-left", style=disnake.ButtonStyle.blurple)
    middle.add_button(label='↓', custom_id=f"{uid}-down", style=disnake.ButtonStyle.blurple)
    middle.add_button(label='→', custom_id=f"{uid}-right", style=disnake.ButtonStyle.blurple)

    components = [up, middle]

    # Listens for button inputs
    @bot.listen("on_button_click")
    async def on_race_press(inter):
        if not inter.data.custom_id.startswith(uid):
            return
        if inter.data.custom_id.endswith("up"):
            x, y = road_manager.player_pos

            if y < 3:
                y += 1
            road_manager.player_pos = (x, y)
        elif inter.data.custom_id.endswith("down"):
            x, y = road_manager.player_pos
            if y > 0:
                y -= 1
            road_manager.player_pos = (x, y)
        elif inter.data.custom_id.endswith("left"):
            x, y = road_manager.player_pos
            if x > 0:
                x -= 1
            road_manager.player_pos = (x, y)
        elif inter.data.custom_id.endswith("right"):
            x, y = road_manager.player_pos
            if x < 1:
                x += 1
            road_manager.player_pos = (x, y)
        final_road_str = road_manager.get_current_road()
        await inter.response.edit_message(f"```80's RACER\n{final_road_str}```", components=components)
    final_road_str = ''
    # Main Game Loop
    while game_active:

        road_manager.progress_game()
        road_manager.generate_traffic()
        final_road_str = road_manager.get_current_road()
        await message.edit(f"```Dodge the cars to accumulate score! Get hit 3 times and you lose!\nSCORE: {road_manager.score} | HITS: {road_manager.hits}\n{final_road_str}```", components=components)
        await asyncio.sleep(1)

        if road_manager.score >= 1000 or road_manager.hits >= 3:
            game_active = False
            break

    bot.remove_listener(on_race_press)
    if road_manager.score >= 1000:
        end_game_message = f"```Congratulations! You managed to survive the Race! You won {road_manager.score} Tickets."
        if random.randint(1, 3) == 1:

            draw = random.randint(1, 25)
            if draw <= 6:
                prize, = db.award_random_prize(member, "Race", 0)
            elif draw <= 16:
                prize, = db.award_random_prize(member, "Race", 1)
            elif draw <= 24:
                prize, = db.award_random_prize(member, "Race", 2)
            else:
                prize, = db.award_random_prize(member, "Race", 3)
            prize_data = db.get_prize(prize)
            end_game_message += f"\nWow! You won a {prize_data[1]}! You can view your prizes with /inv\n{final_road_str}```"
        else:
            end_game_message += f"\n{final_road_str}```"
    else:
        end_game_message = f"```Game Over! You were hit too many times! You earned {road_manager.score} Tickets this run.\n{final_road_str}```"
    db.award_tickets(road_manager.score, member, "Race")
    end_game_message += f"You now have {db.get_tickets(member)} Tickets!"
    await message.edit(end_game_message, components=[])