import disnake
import disnake.ext.commands
import database
db = database.Database()

def __init__():
    return

async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, _: str, __: str | None = None):
    base_url = "https://rutdiscord.github.io/halloween2023/plinko/"
    token = db.create_web_game_session(member,"Drop A Ball",additional_context={"Game":"Drop A Ball"})
    embed = disnake.Embed(title="Drop A Ball")
    embed.add_field(name="Click the link to play:" , value=base_url+"?token="+token)
    return await thread.send(embed=embed)
