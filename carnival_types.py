import typing
import disnake
import disnake.ext.commands

PrivateGame = typing.Callable[[disnake.Thread, disnake.Member, typing.Optional[str], disnake.ext.commands.Bot, str], typing.Coroutine]