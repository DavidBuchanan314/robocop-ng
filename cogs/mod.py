import discord
from discord.ext import commands
import config
import json
import time


class ModCog:
    def __init__(self, bot):
        self.bot = bot

    def check_if_staff(ctx):
        return any(r.id in config.staff_role_ids for r in ctx.author.roles)

    def check_if_target_is_staff(self, target):
        return any(r.id in config.staff_role_ids for r in target.roles)

    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def mute(self, ctx, target: discord.Member, *, reason: str = ""):
        """Mutes a user, staff only."""
        # TODO: keep a restriction list
        # so that muted people can't just leave and rejoin
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't mute this user as "
                                  "they're a member of staff.")

        safe_name = self.bot.escape_message(str(target))

        dm_message = f"You were muted!"
        if reason:
            dm_message += f" The given reason is: \"{reason}\"."

        try:
            await target.send(dm_message)
        except discord.errors.Forbidden:
            # Prevents kick issues in cases where user blocked bot
            # or has DMs disabled
            pass

        mute_role = ctx.guild.get_role(config.mute_role)

        await target.add_roles(mute_role, reason=str(ctx.author))

        chan_message = f"🔇 **Muted**: {ctx.author.mention} muted "\
                       f"{target.mention} | {safe_name}\n"\
                       f"🏷 __User ID__: {target.id}\n"
        if reason:
            chan_message += f"✏️ __Reason__: \"{reason}\""
        else:
            chan_message += "Please add an explanation below. In the future, "\
                            "it is recommended to use `.mute <user> [reason]`"\
                            " as the reason is automatically sent to the user."

        log_channel = self.bot.get_channel(config.log_channel)
        await log_channel.send(chan_message)
        await ctx.send(f"{target.mention} can no longer speak.")

    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def unmute(self, ctx, target: discord.Member):
        """Unmutes a user, staff only."""
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't unmute this user as "
                                  "they're a member of staff.")

        safe_name = self.bot.escape_message(str(target))

        mute_role = ctx.guild.get_role(config.mute_role)
        await target.remove_roles(mute_role, reason=str(ctx.author))

        chan_message = f"🔈 **Unmuted**: {ctx.author.mention} unmuted "\
                       f"{target.mention} | {safe_name}\n"\
                       f"🏷 __User ID__: {target.id}\n"

        log_channel = self.bot.get_channel(config.log_channel)
        await log_channel.send(chan_message)
        await ctx.send(f"{target.mention} can now speak again.")

    @commands.guild_only()
    @commands.bot_has_permissions(kick_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def kick(self, ctx, target: discord.Member, *, reason: str = ""):
        """Kicks a user, staff only."""
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't kick this user as "
                                  "they're a member of staff.")

        safe_name = self.bot.escape_message(str(target))

        dm_message = f"You were kicked from {ctx.guild.name}."
        if reason:
            dm_message += f" The given reason is: \"{reason}\"."
        dm_message += "\n\nYou are able to rejoin the server,"\
                      " but please be sure to behave when participating again."

        try:
            await target.send(dm_message)
        except discord.errors.Forbidden:
            # Prevents kick issues in cases where user blocked bot
            # or has DMs disabled
            pass

        await target.kick(reason=f"{ctx.author}, reason: {reason}")
        chan_message = f"👢 **Kick**: {ctx.author.mention} kicked "\
                       f"{target.mention} | {safe_name}\n"\
                       f"🏷 __User ID__: {target.id}\n"
        if reason:
            chan_message += f"✏️ __Reason__: \"{reason}\""
        else:
            chan_message += "Please add an explanation below. In the future"\
                            ", it is recommended to use `.ban <user> [reason]`"\
                            " as the reason is automatically sent to the user."

        log_channel = self.bot.get_channel(config.log_channel)
        await log_channel.send(chan_message)

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def ban(self, ctx, target: discord.Member, *, reason: str = ""):
        """Bans a user, staff only."""
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't ban this user as "
                                  "they're a member of staff.")

        safe_name = self.bot.escape_message(str(target))

        dm_message = f"You were banned from {ctx.guild.name}."
        if reason:
            dm_message += f" The given reason is: \"{reason}\"."
        dm_message += "\n\nThis ban does not expire."

        try:
            await target.send(dm_message)
        except discord.errors.Forbidden:
            # Prevents ban issues in cases where user blocked bot
            # or has DMs disabled
            pass

        await target.ban(reason=f"{ctx.author}, reason: {reason}",
                         delete_message_days=0)
        chan_message = f"⛔ **Ban**: {ctx.author.mention} banned "\
                       f"{target.mention} | {safe_name}\n"\
                       f"🏷 __User ID__: {target.id}\n"
        if reason:
            chan_message += f"✏️ __Reason__: \"{reason}\""
        else:
            chan_message += "Please add an explanation below. In the future"\
                            ", it is recommended to use `.ban <user> [reason]`"\
                            " as the reason is automatically sent to the user."

        log_channel = self.bot.get_channel(config.log_channel)
        await log_channel.send(chan_message)
        await ctx.send(f"{safe_name} is now b&. 👍")

    @commands.guild_only()
    @commands.bot_has_permissions(ban_members=True)
    @commands.check(check_if_staff)
    @commands.command()
    async def silentban(self, ctx, target: discord.Member, *, reason: str = ""):
        """Bans a user, staff only."""
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't ban this user as "
                                  "they're a member of staff.")

        safe_name = self.bot.escape_message(str(target))

        await target.ban(reason=f"{ctx.author}, reason: {reason}",
                         delete_message_days=0)
        chan_message = f"⛔ **Silent ban**: {ctx.author.mention} banned "\
                       f"{target.mention} | {safe_name}\n"\
                       f"🏷 __User ID__: {target.id}\n"
        if reason:
            chan_message += f"✏️ __Reason__: \"{reason}\""
        else:
            chan_message += "Please add an explanation below. In the future"\
                            ", it is recommended to use `.ban <user> [reason]`"\
                            " as the reason is automatically sent to the user."

        log_channel = self.bot.get_channel(config.log_channel)
        await log_channel.send(chan_message)

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def userinfo(self, ctx, *, user: discord.Member):
        """Gets user info, staff only."""
        role = user.top_role.name
        if role == "@everyone":
            role = "@ everyone"
        await ctx.send(f"user = {user}\n"
                       f"id = {user.id}\n"
                       f"avatar = {user.avatar_url}\n"
                       f"bot = {user.bot}\n"
                       f"created_at = {user.created_at}\n"
                       f"display_name = {user.display_name}\n"
                       f"joined_at = {user.joined_at}\n"
                       f"activities = `{user.activities}`\n"
                       f"color = {user.colour}\n"
                       f"top_role = {role}\n")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def approve(self, ctx, target: discord.Member,
                      role: str = "community"):
        if role not in config.named_roles:
            return await ctx.send("No such role! Available roles: " +
                                  ','.join(config.named_roles))

        log_channel = self.bot.get_channel(config.log_channel)
        target_role = ctx.guild.get_role(config.named_roles[role])

        if target_role in target.roles:
            return await ctx.send("Target already has this role.")

        await target.add_roles(target_role, reason=str(ctx.author))

        await ctx.send(f"Approved {target.mention} to `{role}` role.")

        await log_channel.send(f"✅ Approved: {ctx.author.mention} added"
                               f" {role} to {target.mention}")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command(aliases=["unapprove"])
    async def revoke(self, ctx, target: discord.Member,
                     role: str = "community"):
        if role not in config.named_roles:
            return await ctx.send("No such role! Available roles: " +
                                  ','.join(config.named_roles))

        log_channel = self.bot.get_channel(config.log_channel)
        target_role = ctx.guild.get_role(config.named_roles[role])

        if target_role not in target.roles:
            return await ctx.send("Target doesn't have this role.")

        await target.remove_roles(target_role, reason=str(ctx.author))

        await ctx.send(f"Un-approved {target.mention} from `{role}` role.")

        await log_channel.send(f"❌ Un-approved: {ctx.author.mention} removed"
                               f" {role} from {target.mention}")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command(aliases=["setplaying", "setgame"])
    async def playing(self, ctx, *, game: str = ""):
        """Sets the bot's currently played game name, staff only.

        Just send .playing to wipe the playing state."""
        if game:
            await self.bot.change_presence(activity=discord.Game(name=game))
        else:
            await self.bot.change_presence(activity=None)

        await ctx.send("Successfully set game.")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command(aliases=["setbotnick", "botnick", "robotnick"])
    async def botnickname(self, ctx, *, nick: str = ""):
        """Sets the bot's nickname, staff only.

        Just send .botnickname to wipe the nickname."""

        if nick:
            await ctx.guild.me.edit(nick=nick, reason=str(ctx.author))
        else:
            await ctx.guild.me.edit(nick=None, reason=str(ctx.author))

        await ctx.send("Successfully set nickname.")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command(aliases=["setnick", "nick"])
    async def nickname(self, ctx, target: discord.Member, *, nick: str = ""):
        """Sets a user's nickname, staff only.

        Just send .nickname <user> to wipe the nickname."""

        if nick:
            await target.edit(nick=nick, reason=str(ctx.author))
        else:
            await target.edit(nick=None, reason=str(ctx.author))

        await ctx.send("Successfully set nickname.")

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command(aliases=["clear"])
    async def purge(self, ctx, limit: int, channel: discord.TextChannel = None):
        """Clears a given number of messages. Staff only."""
        log_channel = self.bot.get_channel(config.log_channel)
        if not channel:
            channel = ctx.channel
        await channel.purge(limit=limit)
        msg = f"🗑 **Purged**: {ctx.author.mention} purged {limit} "\
              f"messages in {channel.mention}."
        await log_channel.send(msg)

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def warn(self, ctx, target: discord.Member, *, reason: str = ""):
        """Warn a user. Staff only."""
        if self.check_if_target_is_staff(target):
            return await ctx.send("I can't warn this user as "
                                  "they're a member of staff.")

        log_channel = self.bot.get_channel(config.log_channel)
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        if str(target.id) not in warns:
            warns[str(target.id)] = {"warns": []}
        warns[str(target.id)]["name"] = str(target)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        warn_data = {"issuer_id": ctx.author.id,
                     "issuer_name": ctx.author.name,
                     "reason": reason,
                     "timestamp": timestamp}
        warns[str(target.id)]["warns"].append(warn_data)
        with open("data/warnsv2.json", "w") as f:
            json.dump(warns, f)

        warn_count = len(warns[str(target.id)]["warns"])

        msg = f"You were warned on {ctx.guild.name}."
        if reason:
            msg += " The given reason is: " + reason
        msg += f"\n\nPlease read the rules in {config.rules_url}. "\
               f"This is warn #{warn_count}."
        if warn_count == 2:
            msg += " __The next warn will automatically kick.__"
        if warn_count == 3:
            msg += "\n\nYou were kicked because of this warning. "\
                   "You can join again right away. "\
                   "Two more warnings will result in an automatic ban."
        if warn_count == 4:
            msg += "\n\nYou were kicked because of this warning. "\
                   "This is your final warning. "\
                   "You can join again, but "\
                   "**one more warn will result in a ban**."
        if warn_count == 5:
            msg += "\n\nYou were automatically banned due to five warnings."
        try:
            await target.send(msg)
        except discord.errors.Forbidden:
            # Prevents log issues in cases where user blocked bot
            # or has DMs disabled
            pass
        if warn_count == 3 or warn_count == 4:
            await target.kick()
        if warn_count >= 5:  # just in case
            await target.ban(reason="exceeded warn limit",
                             delete_message_days=0)
        await ctx.send(f"{target.mention} warned. "
                       f"User has {warn_count} warning(s).")
        msg = f"⚠️ **Warned**: {ctx.author.mention} warned {target.mention}"\
              f" (warn #{warn_count}) | {self.bot.escape_message(target)}"

        if reason:
            msg += f"✏️ __Reason__: \"{reason}\""
        else:
            msg += "Please add an explanation below. In the future"\
                   ", it is recommended to use `.ban <user> [reason]`"\
                   " as the reason is automatically sent to the user."
        await log_channel.send(msg)

    def get_warns_embed_for_id(self, uid: str, name: str):
        embed = discord.Embed(color=discord.Color.dark_red())
        embed.set_author(name=f"Warns for {name}")
        with open("data/warnsv2.json", "r") as f:
            warns = json.load(f)
        try:
            if len(warns[uid]["warns"]):
                for idx, warn in enumerate(warns[uid]["warns"]):
                    embed.add_field(name=f"{idx + 1}: {warn['timestamp']}",
                                    value=f"Issuer: {warn['issuer_name']}\n"
                                          f"Reason: {warn['reason']}")
            else:
                embed.description = "There are none!"
                embed.color = discord.Color.green()
        except KeyError:  # if the user is not in the file
            embed.description = "There are none!"
            embed.color = discord.Color.green()
        return embed

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def listwarns(self, ctx, target: discord.Member):
        """List warns for a user. Staff only."""
        embed = self.get_warns_embed_for_id(str(target.id), str(target))
        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.check(check_if_staff)
    @commands.command()
    async def listwarnsid(self, ctx, target: int):
        """List warns for a user by ID. Staff only."""
        embed = self.get_warns_embed_for_id(str(target), str(target))
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(ModCog(bot))