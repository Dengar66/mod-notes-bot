# bot.py

import os
import discord
import praw
import sys
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')
REDDIT_REFRESH_TOKEN = os.getenv('REDDIT_REFRESH_TOKEN')

reddit = praw.Reddit(client_id = REDDIT_CLIENT_ID, client_secret = REDDIT_CLIENT_SECRET, refresh_token = REDDIT_REFRESH_TOKEN, user_agent = REDDIT_USER_AGENT)

class ModNotesBot(commands.Bot):
	def __init__(self):
        intents = discord.Intents.all()
        activity = discord.Activity(type=discord.ActivityType.listening, name='$help')
        super().__init__(command_prefix='$', intents=intents, activity=activity)

    @self.command(name='notes', help='Gets Mod Notes from Reddit for specified Username')
    async def ModNotes(self, ctx, username):
        if username is None:
            await ctx.send(f'Unable to determine Reddit Username for {username}')
            return

        try:
            notes = praw.getNotes(username)
            notes = notes[username]
        except KeyError:
            await ctx.send(f'Either invalid username or no SnooNotes exist for {username}')
            return
        except:
            await ctx.send(f'Unable to fetch SnooNotes for {username}, please see logs')
            return

        try:
            embed = Embed(title = username, description = f'All Notes for {username} with the Note Reason, URL, Type, Date, and NoteID')
            total_notes = 0
            for sn in notes:
                if sn['SubName'] != SUBREDDIT:
                    continue
                
                # The embed can have a max of 8 sets of fields
                if total_notes > 0 and total_notes % 8 == 0:
                    # Send the currently created embed
                    await ctx.send(embed=embed)
                    # Create a new embed
                    embed = Embed(title = str(username + ' #' + str(int(total_notes/8)+1)), description = f'All Notes for {username} with the Note Reason, URL, Type, Date, and NoteID')
                
                sntyp = sn['NoteTypeID']
                snname = get_snooname(sntyp)
                snemoji = get_snooemoji(sntyp)
                message = str(snemoji + ' ' + sn['Message'])
                if len(message) > 256:
                    message = message[:256]

                embed.add_field(name = message, value = sn['Url'])
                embed.add_field(name = snname, value = sn['Timestamp'][:10], inline = True)
                embed.add_field(name = 'Note ID for Command Use', value = sn['NoteID'], inline = True)

                total_notes+=1

            await ctx.send(embed=embed)
            await ctx.message.delete(delay=600)
        except:
            await ctx.send('Failed to create Message for response, please see logs')


bot = ModNotesBot()
bot.run(TOKEN)