OWNERS = {
    919401140523761735,
    260173296081829889,
    914457549116411924,
}


def only_owners(ctx):
    if ctx.author.id in OWNERS:
        return True
