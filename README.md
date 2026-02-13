# Saint Quotes Ingestion

This project extracts quote records from:
`A Dictionary of Quotes From th - Thigpen, Paul_6247.pdf`

## 1) Extract structured records

```powershell
python scripts\extract_saint_quotes.py --pdf "A Dictionary of Quotes From th - Thigpen, Paul_6247.pdf" --outdir output
```

Outputs:
- `output/saint_quotes.csv`
- `output/saint_quotes.json`

## 2) Build the SQLite database

```powershell
python scripts\build_db.py
```

Creates `output/saint_quotes.db` (~740 KB, 1866 quotes, 302 topics, 224 authors).

## 3) Use in other projects

Copy `saint_quotes.py` and `output/saint_quotes.db` into your project.

```python
from saint_quotes import SaintQuotes

sq = SaintQuotes("path/to/saint_quotes.db")

sq.random()                     # one random quote
sq.random(topic="PRAYER")       # random quote on a topic
sq.random(author="Augustine")   # random quote by author (substring match)

sq.search("love")              # search quote text
sq.by_author("Thomas Aquinas") # all quotes by an author
sq.by_topic("HUMILITY")       # all quotes under a topic
sq.topics()                    # list all topics
sq.authors()                   # list all authors

# Quote objects have: .id, .topic, .quote, .author, .page
# str(quote) gives a formatted string like:
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

## Notes

- The parser assigns `topic`, `quote`, `author`, and `page` from PDF text extraction.
- Always keep provenance columns (source title/file/page) in your production DB.
- Verify rights/licensing before publishing or redistributing quote content.
