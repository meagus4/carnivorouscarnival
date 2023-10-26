import disnake
import disnake.ext.commands
import database
db = database.Database()

def __init__():
    return

async def play_game(thread: disnake.Thread, member: disnake.Member, bot: disnake.ext.commands.Bot, _: str, __: str | None = None):
    base_url = "https://rutdiscord.github.io/halloween2023/duck-pond/"
    token = db.create_web_game_session(member,"Hook A Duck",additional_context={"Game":"Hook A Duck"})
    embed = disnake.Embed(title="Hook A Duck")
    embed.add_field(name="Click the link to play:" , value=base_url+"?token="+token)
    return await thread.send(embed=embed)
