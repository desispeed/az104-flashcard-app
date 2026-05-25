# AZ-104 Flashcards MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io) server that exposes
the AZ-104 question bank from this repo as tools and resources, so any MCP
client (Claude Desktop, Claude Code, custom clients, etc.) can quiz, search,
and grade answers against the deck.

## Install

```bash
cd mcp-server
npm install
```

## Run

The server speaks the MCP protocol over stdio:

```bash
node mcp-server/server.js
```

You normally don't run it directly — your MCP client launches it.

## Tools

| Tool | Description |
| --- | --- |
| `list_categories` | List all categories with question counts. |
| `get_question` | Fetch a question by id. Pass `reveal_answer: true` for the answer + explanation. |
| `get_random_question` | A random question, optionally filtered by `category`. |
| `search_questions` | Substring search across question text and options. |
| `check_answer` | Grade a choice (0-based index or `A`/`B`/`C`/`D`) against a question id. |
| `start_quiz` | Build a quiz of N random questions, optionally filtered by category. |

## Resources

- `az104://questions` — full question bank as JSON.
- `az104://questions/{id}` — a single question as JSON.

## Wiring it into a client

### Claude Desktop / Claude Code (`mcpServers` config)

Add an entry pointing at this directory:

```json
{
  "mcpServers": {
    "az104-flashcards": {
      "command": "node",
      "args": ["/absolute/path/to/az104-flashcard-app/mcp-server/server.js"]
    }
  }
}
```

For Claude Code specifically, this can live in `.mcp.json` at the project
root, or in your user `~/.claude.json`.

### Quick smoke test

```bash
printf '%s\n' \
  '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"0"}}}' \
  '{"jsonrpc":"2.0","method":"notifications/initialized"}' \
  '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' \
  | node server.js
```

## Data source

`mcp-server/data/questions.json` is the question bank — kept in sync with the
React app's inline `AZ104_QUESTIONS` array in `src/App.jsx`. If you edit one,
update the other.
