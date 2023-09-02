import typing
import disnake

PrivateGame = typing.Callable[[disnake.Thread, disnake.Member, typing.Optional[str]], typing.Coroutine]
PublicGame = typing.Callable[[disnake.TextChannel, typing.Optional[str]], typing.Coroutine]