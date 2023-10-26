import disnake
import disnake.ext.commands
import database
db = database.Database()

def __init__():
    return

async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, _: str, __: str | None = None):
    base_url = "https://rutdiscord.github.io/halloween2023/whackaspamton/"
    token = db.create_web_game_session(member,"Whack-A-Spamton",additional_context={"Game":"Whack-A-Spamton"})
    embed = disnake.Embed(title="Whack-A-Spamton")
    embed.add_field(name="Click the link to play:" , value=base_url+"?token="+token)
    return await thread.send(embed=embed)
