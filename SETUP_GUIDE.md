# Claude Slack Bot — Setup Guide

A Slack bot powered by Anthropic's Claude that can chat with AI, write ads/landers/VSLs using proven direct-response frameworks, and manage campaigns and tasks — all from Slack.

## Features

**AI Chat** — @mention the bot or DM it. Thread-aware memory.

**Creative Tools** — Write ad scripts, landing pages, VSLs, and hooks using battle-tested frameworks (A.D.A.P.T., VSL arc, etc.). All commands auto-pull from your knowledge base.

**Project Management** — Track tasks with owners and due dates. Manage campaign pipelines through stages: brief → research → copy → review → revision → approved → live.

**Automations** — Welcome new members, auto-react to keywords, clipboard saving.

### All Slash Commands

| Command | What it does |
|---|---|
| `/ask <question>` | Ask Claude anything (private reply) |
| `/summary [N]` | Summarize last N messages in the channel |
| `/help-claude` | Show all bot capabilities |
| `/ad <brief>` | Write a UGC ad script (A.D.A.P.T. framework) |
| `/lander <brief>` | Write landing page copy |
| `/vsl <brief>` | Write a VSL script |
| `/hooks <brief>` | Generate 10 scroll-stopping hooks |
| `/kb-status` | Show what's in the knowledge base |
| `/task add/done/list/assign` | Manage tasks |
| `/campaign new/advance/stage/pipeline` | Manage campaign workflows |

---

## Step 1: Create a Slack App

1. Go to [api.slack.com/apps](https://api.slack.com/apps) and click **Create New App**
2. Choose **From scratch**
3. Name it (e.g. "ClaudeBot") and pick your workspace
4. Click **Create App**

## Step 2: Enable Socket Mode

Socket Mode lets your bot connect without a public URL — perfect for local development.

1. In the left sidebar, go to **Socket Mode**
2. Toggle it **ON**
3. Give your token a name (e.g. "socket-token") and click **Generate**
4. Copy the `xapp-...` token — this is your `SLACK_APP_TOKEN`

## Step 3: Set Bot Permissions (OAuth & Scopes)

1. Go to **OAuth & Permissions** in the sidebar
2. Under **Bot Token Scopes**, add these scopes:

| Scope | Why |
|---|---|
| `app_mentions:read` | Detect when someone @mentions the bot |
| `chat:write` | Send messages |
| `channels:history` | Read channel messages (for /summary) |
| `groups:history` | Read private channel messages |
| `im:history` | Read DMs to the bot |
| `im:write` | Send DMs |
| `mpim:history` | Read group DMs |
| `reactions:read` | Detect emoji reactions |
| `reactions:write` | Add emoji reactions |
| `users:read` | Look up user display names |
| `channels:read` | List channels |
| `commands` | Register slash commands |

3. Click **Install to Workspace** (or **Reinstall** if updating)
4. Copy the `xoxb-...` token — this is your `SLACK_BOT_TOKEN`

## Step 4: Enable Events

1. Go to **Event Subscriptions** in the sidebar
2. Toggle it **ON**
3. Under **Subscribe to bot events**, add:
   - `app_mention`
   - `message.channels`
   - `message.groups`
   - `message.im`
   - `message.mpim`
   - `member_joined_channel`
   - `reaction_added`
4. Click **Save Changes**

## Step 5: Create Slash Commands

1. Go to **Slash Commands** in the sidebar
2. Create ALL of these commands:

| Command | Description | Usage Hint |
|---|---|---|
| `/ask` | Ask Claude a question | `your question here` |
| `/summary` | Summarize recent channel messages | `[number of messages]` |
| `/help-claude` | Show bot capabilities | _(leave blank)_ |
| `/ad` | Write a UGC ad script | `brief describing product, audience, platform` |
| `/lander` | Write landing page copy | `brief describing product and goals` |
| `/vsl` | Write a VSL script | `brief with product, audience, angle` |
| `/hooks` | Generate 10 hooks | `product and angle description` |
| `/kb-status` | Show knowledge base status | _(leave blank)_ |
| `/task` | Manage tasks | `add/done/list/assign` |
| `/campaign` | Manage campaigns | `new/advance/stage/pipeline` |

## Step 6: Allow DMs

1. Go to **App Home** in the sidebar
2. Under **Show Tabs**, make sure **Messages Tab** is checked
3. Check **Allow users to send Slash commands and messages from the messages tab**

## Step 7: Get Your Signing Secret

1. Go to **Basic Information** in the sidebar
2. Under **App Credentials**, copy the **Signing Secret**
3. This is your `SLACK_SIGNING_SECRET`

## Step 8: Get an Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Create an API key
3. This is your `ANTHROPIC_API_KEY`

---

## Step 9: Set Up Your Knowledge Base

The bot has a `knowledge/` folder with four sections. The more you fill in, the better your creative output will be.

```
knowledge/
├── brand/          ← Brand guidelines, product info, tone of voice, USPs, pricing
├── customers/      ← Avatars, pain points, objections, review mining data, testimonials
├── ads/            ← Winning ad scripts, landers, VSLs — anything that's worked before
└── frameworks/     ← Auto-populated with creative frameworks
```

**How to add content:**
1. Create `.txt` or `.md` files in the appropriate folder
2. Restart the bot (it reads files on startup)
3. Run `/kb-status` in Slack to verify everything loaded

**Example files you might add:**

`knowledge/brand/brand-guide.txt`:
```
BRAND: Glow Skin Co.
TONE: Warm, conversational, backed by science. Never clinical or preachy.
PRODUCTS: Vitamin C Serum ($48), Retinol Night Cream ($52), Complete Bundle ($89)
USP: Dermatologist-formulated, clean ingredients, 90-day guarantee
TARGET MARKET: Women 30-55 who want professional results at home
```

`knowledge/customers/main-avatar.txt`:
```
AVATAR: "Frustrated Sarah"
DESIRE: Look in the mirror and feel confident without makeup
AGE: 38-52
PAIN: Tried expensive serums that did nothing. Feels like her skin aged overnight.
DEEPER PAIN: Avoids photos, feels less attractive than her peers.
OBJECTIONS: "I've tried everything", "Probably too expensive", "Results look fake"
TRIGGER: Saw a friend looking great, asked what changed.
```

`knowledge/ads/facebook-winner-q4.txt`:
```
[Paste your best-performing ad scripts here. The bot will study the tone,
structure, and angles to inform new creative.]
```

Every creative command (`/ad`, `/lander`, `/vsl`, `/hooks`) automatically reads from these files and uses them as context. The more detail you provide, the more on-brand the output will be.

---

## Step 10: Configure and Run

```bash
cd claude-slack-bot

# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy the example env file and fill in your tokens
cp .env.example .env
# Edit .env with your real values

# Run the bot
python app.py
```

You should see:
```
Knowledge base: 3 files loaded
Starting ClaudeBot...
⚡️ Bolt app is running!
```

### Quick test checklist:
- `@ClaudeBot what's the capital of France?` — AI chat
- `/ask explain quantum computing in one sentence` — private AI answer
- `/ad UGC script for our vitamin C serum targeting women 40+, Facebook` — write an ad
- `/hooks collagen powder for women who've tried everything` — generate hooks
- `/task add Write new Q2 hooks @harry due:friday` — create a task
- `/campaign new Q2 Facebook Push type:ad` — start a campaign
- `/campaign pipeline` — see all campaigns

---

## Deploying to the Cloud

Since this bot uses **Socket Mode**, it doesn't need an inbound URL. It works anywhere Python can run.

### Railway
1. Push your code to a GitHub repo (make sure `.env` is in `.gitignore`)
2. Go to [railway.app](https://railway.app), create a new project from that repo
3. Add your environment variables in the Railway dashboard
4. Railway will auto-deploy
5. **Important:** The `knowledge/` and `data/` folders need to persist. Use Railway volumes or store data externally.

### Render
1. Push to GitHub
2. Create a new **Background Worker** on [render.com](https://render.com)
3. Set the start command to `python app.py`
4. Add environment variables in the dashboard
5. Attach a persistent disk for `knowledge/` and `data/`

### Any VPS (DigitalOcean, etc.)
```bash
git clone <your-repo>
cd claude-slack-bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env

# Run with systemd or screen
nohup python app.py &
```

---

## Customization

### Change the bot's personality
Edit `SYSTEM_PROMPT` in `config.py`.

### Change the creative frameworks
Edit the system prompts in `handlers/creative.py`. Each creative type (`/ad`, `/lander`, `/vsl`, `/hooks`) has its own detailed system prompt you can tweak.

### Add new keyword reactions
Edit `KEYWORD_REACTIONS` in `handlers/automations.py`. Format: `regex_pattern: emoji_name`.

### Add campaign stages
Edit `CAMPAIGN_STAGES` and `STAGE_EMOJI` in `project_manager.py`.

### Switch Claude models
Change `CLAUDE_MODEL` in your `.env` file. Options:
- `claude-sonnet-4-20250514` (fast, smart — default)
- `claude-opus-4-20250514` (most capable, best for creative)
- `claude-haiku-3-5-20241022` (fastest, cheapest)

### Add new slash commands
Create a new handler file in `handlers/`, add your `@app.command` functions, and register it in `app.py`.
