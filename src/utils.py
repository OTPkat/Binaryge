import discord


async def create_secret_thread(channel, thread_name):
    thread = await channel.create_thread(
        name=thread_name,
    )
    return thread


async def get_or_create_thread(
        channel: discord.TextChannel, thread_name: str
):
    thread_name = thread_name.replace("#", "")
    for thread in channel.threads:
        if thread.name == thread_name:
            return thread
    thread = await create_secret_thread(channel, thread_name)
    return thread