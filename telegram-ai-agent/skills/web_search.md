# Web Search

Search the web using curl and return results.

## When to use
When the user asks about current events, latest news, or needs up-to-date information.

## How to use
Use the `run_shell` tool with curl to fetch search results:

```
{"tool": "run_shell", "command": "curl -s 'https://api.duckduckgo.com/?q=QUERY&format=json' | python3 -c \"import sys,json; d=json.load(sys.stdin); [print(r['Text']) for r in d.get('RelatedTopics',[])[:5] if 'Text' in r]\""}
```

Replace QUERY with the URL-encoded search query.
