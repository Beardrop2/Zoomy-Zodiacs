# 🤖 Zoomy Zodiacs' Community Bot

For the [Python Discord](https://pythondiscord.com)'s 11th code jam with the
theme "Information Overload", we built a community bot. As a new community
member, this bot aims to help you get around the server.

## ➕ Features

### 🏷️ User tags

- `/tag add` - Add tags to yourself with a dropdown
- `/tag remove` - Remove a tag from yourself
- `/tag suggest_friends` - Suggest friends based on your tags

### ✨ AI help

AI help uses an LLM to help users navigate around channels.

## ⚙️ Setting up

This bot is built with [PDM](https://pdm-project.org). To start the bot, you
clone the repository, set up environment variables, install dependencies, and
run the `start` command:

```sh
# Clone the repository and go to it
git clone https://github.com/Beardrop2/Zoomy-Zodiacs
cd Zoomy-Zodiacs

# Copy the .env template
cp template.env .env

# After copying the template, configure the `.env` file with a text editor.
# If you don't want to change the Ollama settings (for AI help), all you need to
# fill in is the bot token.

# Install PDM if it hasn't been installed (run ONLY ONE of these commands)
pip install pdm      # Globally
pipx install pdm     # With pipx
rye install pdm      # With Rye
uv tool install pdm  # With uv

# Install project dependencies
pdm install

# Start
pdm start
```

### ✨⚙️ Setting up AI help

AI help requires [Ollama](https://ollama.com) to be running on your system. The
model used (`phi3` by default) also needs to be pulled by running:

```sh
# The model should match the one in the environment variable (see ZZ_OLLAMA_MODEL in .env)
ollama pull <model>
```

## 🧑‍💻 Development

See the [development setup](./DEV_SETUP.md) guide.

## 🔑 License

This project (along with all other code jam entries) is licensed under the
[MIT license](./LICENSE.txt).
