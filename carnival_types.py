import typing
import disnake
import disnake.ext.commands

PrivateGame = typing.Callable[
    [
        disnake.Thread,  # thread - Private thread
        disnake.Member,  # member - Target member
        disnake.ext.commands.Bot,  # bot - Bot instance
        str,  # uid - uid
        typing.Optional[str],  # optional - Optional arguments
    ], typing.Coroutine]
PublicGame = typing.Callable[[disnake.TextChannel,
                              typing.Optional[str]], typing.Coroutine]
