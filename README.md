# Athens Properties

## MCP servers

This project configures the following MCP server for local development in `.mcp.json`:

- **nanobanana-mcp** — Google Gemini image generation/editing (https://github.com/charlesdove977/nanobanana-mcp).
  Requires a `GEMINI_API_KEY` environment variable (get one at https://aistudio.google.com/apikey).
  **Never commit your API key.** Export it in your shell or put it in a local, git-ignored `.env` file before starting Claude Code:

  ```sh
  export GEMINI_API_KEY="your-key-here"
  ```
