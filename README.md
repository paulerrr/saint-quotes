# Saint Quotes

1866 quotes from 224 Catholic saints across 302 topics in a portable SQLite database.

## Usage

Copy `saint_quotes.py` and `saint_quotes.db` into your project.

```python
from saint_quotes import SaintQuotes

sq = SaintQuotes("saint_quotes.db")

sq.random()                     # one random quote
sq.random(topic="PRAYER")       # random quote on a topic
sq.random(author="Augustine")   # random quote by author (substring match)

sq.search("love")              # search quote text
sq.by_author("Thomas Aquinas") # all quotes by an author
sq.by_topic("HUMILITY")       # all quotes under a topic
sq.topics()                    # list all topics
sq.authors()                   # list all authors

# Quote objects have: .id, .topic, .quote, .author, .page
# str(quote) gives a formatted string:
#   "Quote text here."
#     — Author Name (on TOPIC)
# quote.to_dict() returns a plain dict
```

### Discord bot example

```python
import discord
from saint_quotes import SaintQuotes

bot = discord.Bot()
sq = SaintQuotes("saint_quotes.db")

@bot.slash_command()
async def quote(ctx, topic: str = None):
    q = sq.random(topic=topic)
    if q:
        await ctx.respond(str(q))
    else:
        await ctx.respond("No quotes found.")
```
