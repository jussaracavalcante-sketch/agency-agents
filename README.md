# 🎭 The Agency: AI Specialists Ready to Transform Your Workflow

> **A complete AI agency at your fingertips** - From frontend wizards to Reddit community ninjas, from whimsy injectors to reality checkers. Each agent is a specialized expert with personality, processes, and proven deliverables.

[![GitHub stars](https://img.shields.io/github/stars/msitarzewski/agency-agents?style=social)](https://github.com/msitarzewski/agency-agents)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-pink?logo=github)](https://github.com/sponsors/msitarzewski)
[![Download the app](https://img.shields.io/github/v/release/msitarzewski/agency-agents-app?label=Download%20app&color=2563eb)](https://github.com/msitarzewski/agency-agents-app/releases/latest)

> ### 🆕 There's an app now
>
> **[Agency Agents](https://agencyagents.app)** is a native app for **macOS, Linux & Windows** that browses the entire roster and installs it into Claude Code, Cursor, Codex, Gemini, Osaurus, and more — with a click. No clone, no scripts, and it auto-updates.
>
> **→ [Download the latest release](https://github.com/msitarzewski/agency-agents-app/releases/latest) · [agencyagents.app](https://agencyagents.app)**

---

## 🚀 What Is This?

Born from a Reddit thread and months of iteration, **The Agency** is a growing collection of meticulously crafted AI agent personalities. Each agent is:

- **🎯 Specialized**: Deep expertise in their domain (not generic prompt templates)
- **🧠 Personality-Driven**: Unique voice, communication style, and approach
- **📋 Deliverable-Focused**: Real code, processes, and measurable outcomes
- **✅ Production-Ready**: Battle-tested workflows and success metrics

**Think of it as**: Assembling your dream team, except they're AI specialists who never sleep, never complain, and always deliver.

---

## ⚡ Quick Start

### Option 1: Install the app (Recommended)

The fastest way in — no clone, no terminal. [**Agency Agents**](https://agencyagents.app) is a native desktop app (macOS · Linux · Windows) that browses the whole roster and installs agents into Claude Code, Cursor, Codex, Gemini CLI, OpenCode, Qwen, and Osaurus for you, then keeps them up to date.

**[⬇ Download the latest release](https://github.com/msitarzewski/agency-agents-app/releases/latest)** — or on a Mac:

```bash
brew install --cask msitarzewski/agency-agents/agency-agents
```

Prefer the command line? The script-based options below install the same agents.

### Option 2: Use with Claude Code

```bash
# Install all agents to your Claude Code directory
./scripts/install.sh --tool claude-code

# Or manually copy a category if you only want one division
cp engineering/*.md ~/.claude/agents/

# Then activate any agent in your Claude Code sessions:
# "Hey Claude, activate Frontend Developer mode and help me build a React component"
```

### Option 3: Use as Reference

Each agent file contains:
- Identity & personality traits
- Core mission & workflows
- Technical deliverables with code examples
- Success metrics & communication style

Browse the agents below and copy/adapt the ones you need!

### Option 4: Use with Other Tools (GitHub Copilot, Antigravity, Gemini CLI, OpenCode, OpenClaw, Cursor, Aider, Windsurf, Kimi Code, Codex, Osaurus, Hermes, Mistral Vibe, DeepSeek Harness)

```bash
# Step 1 -- generate integration files for all supported tools
./scripts/convert.sh

# Step 2 -- install interactively (auto-detects what you have installed)
./scripts/install.sh

# Or target a specific tool directly
./scripts/install.sh --tool antigravity
./scripts/install.sh --tool gemini-cli
./scripts/install.sh --tool opencode
./scripts/install.sh --tool copilot
./scripts/install.sh --tool openclaw
./scripts/install.sh --tool cursor
./scripts/install.sh --tool aider
./scripts/install.sh --tool windsurf
./scripts/install.sh --tool kimi
./scripts/install.sh --tool codex
./scripts/install.sh --tool osaurus
./scripts/install.sh --tool hermes
./scripts/install.sh --tool vibe
./scripts/install.sh --tool dsh
```

**Install only the teams you need** (not everyone wants every division):

```bash
./scripts/install.sh                                    # interactive wizard: pick tools + teams
./scripts/install.sh --tool claude-code --division engineering,security
./scripts/install.sh --tool cursor --agent frontend-developer,ui-designer
./scripts/install.sh --list teams                       # see every team + agent count
./scripts/install.sh --tool opencode --division engineering --dry-run
```

> **OpenCode note:** OpenCode's runtime currently registers only ~119 agents and silently drops the rest ([upstream bug](https://github.com/anomalyco/opencode/issues/27988)). Installing a subset with `--division` keeps you under that limit. The installer warns you when a selection would exceed it.

See the [Multi-Tool Integrations](#-multi-tool-integrations) section below for full details.

---

## 🎨 The Agency Roster

### 📢 Marketing Division

Growing your audience, one authentic interaction at a time.

| Agent | Specialty | When to Use |
|-------|-----------|-------------|
| 🚀 [Growth Hacker](marketing/marketing-growth-hacker.md) | Rapid user acquisition, viral loops, experiments | Explosive growth, user acquisition, conversion optimization |
| 📝 [Content Creator](marketing/marketing-content-creator.md) | Multi-platform content, editorial calendars | Content strategy, copywriting, brand storytelling |
| 🐦 [Twitter Engager](marketing/marketing-twitter-engager.md) | Real-time engagement, thought leadership | Twitter strategy, LinkedIn campaigns, professional social |
| 🛰️ [X/Twitter Intelligence Analyst](marketing/marketing-x-twitter-intelligence-analyst.md) | Social listening, trend detection, account monitoring | Brand risk, competitor, and audience intelligence on X/Twitter |
| 📱 [TikTok Strategist](marketing/marketing-tiktok-strategist.md) | Viral content, algorithm optimization | TikTok growth, viral content, Gen Z/Millennial audience |
| 📸 [Instagram Curator](marketing/marketing-instagram-curator.md) | Visual storytelling, community building | Instagram strategy, aesthetic development, visual content |
| 🤝 [Reddit Community Builder](marketing/marketing-reddit-community-builder.md) | Authentic engagement, value-driven content | Reddit strategy, community trust, authentic marketing |
| 📱 [App Store Optimizer](marketing/marketing-app-store-optimizer.md) | ASO, conversion optimization, discoverability | App marketing, store optimization, app growth |
| 🌐 [Social Media Strategist](marketing/marketing-social-media-strategist.md) | Cross-platform strategy, campaigns | Overall social strategy, multi-platform campaigns |
| 🎠 [Carousel Growth Engine](marketing/marketing-carousel-growth-engine.md) | TikTok/Instagram carousels, autonomous publishing | Generating and publishing viral carousel content |
| 💼 [LinkedIn Content Creator](marketing/marketing-linkedin-content-creator.md) | Personal branding, thought leadership, professional content | LinkedIn growth, professional audience building, B2B content |
| 🔍 [SEO Specialist](marketing/marketing-seo-specialist.md) | Technical SEO, content strategy, link building | Driving sustainable organic search growth |
| 🎧 [Podcast Strategist](marketing/marketing-podcast-strategist.md) | Podcast content strategy, platform optimization | Chinese podcast market strategy and operations |
| 🎬 [Short-Video Editing Coach](marketing/marketing-short-video-editing-coach.md) | Post-production, editing workflows, platform specs | Hands-on short-video editing training and optimization |
| 🎙️ [Global Podcast Strategist](marketing/marketing-global-podcast-strategist.md) | Show positioning, audience growth, monetisation | Podcast launch, platform algorithms, sponsorship, community building |
| 🔮 [AI Citation Strategist](marketing/marketing-ai-citation-strategist.md) | AEO/GEO, AI recommendation visibility, citation auditing | Improving brand visibility across ChatGPT, Claude, Gemini, Perplexity |
| 🎬 [Video Optimization Specialist](marketing/marketing-video-optimization-specialist.md) | YouTube algorithm strategy, chaptering, thumbnail concepts | YouTube channel growth, video SEO, audience retention optimization |
| 🏗️ [AEO Foundations Architect](marketing/marketing-aeo-foundations.md) | AI Engine Optimization infrastructure | llms.txt, AI-aware robots.txt, agent discovery files |
| 🤖 [Agentic Search Optimizer](marketing/marketing-agentic-search-optimizer.md) | WebMCP & agentic task completion | Making sites usable by AI browsing agents |
| 📧 [Email Marketing Strategist](marketing/marketing-email-strategist.md) | Lifecycle email & deliverability | CRM campaigns, automation, segmentation |
| 📣 [PR & Communications Manager](marketing/marketing-pr-communications-manager.md) | PR, media relations & crisis comms | Press releases, thought leadership, reputation |

### 💰 Paid Media Division

Turning ad spend into measurable business outcomes.

| Agent | Specialty | When to Use |
| --- | --- | --- |
| 💰 [PPC Campaign Strategist](paid-media/paid-media-ppc-strategist.md) | Google/Microsoft/Amazon Ads, account architecture, bidding | Account buildouts, budget allocation, scaling, performance diagnosis |
| 🔍 [Search Query Analyst](paid-media/paid-media-search-query-analyst.md) | Search term analysis, negative keywords, intent mapping | Query audits, wasted spend elimination, keyword discovery |
| 📋 [Paid Media Auditor](paid-media/paid-media-auditor.md) | 200+ point account audits, competitive analysis | Account takeovers, quarterly reviews, competitive pitches |
| 📡 [Tracking & Measurement Specialist](paid-media/paid-media-tracking-specialist.md) | GTM, GA4, conversion tracking, CAPI | New implementations, tracking audits, platform migrations |
| ✍️ [Ad Creative Strategist](paid-media/paid-media-creative-strategist.md) | RSA copy, Meta creative, Performance Max assets | Creative launches, testing programs, ad fatigue refreshes |
| 📺 [Programmatic & Display Buyer](paid-media/paid-media-programmatic-buyer.md) | GDN, DSPs, partner media, ABM display | Display planning, partner outreach, ABM programs |
| 📱 [Paid Social Strategist](paid-media/paid-media-paid-social-strategist.md) | Meta, LinkedIn, TikTok, cross-platform social | Social ad programs, platform selection, audience strategy |

### 💼 Sales Division

Turning pipeline into revenue through craft, not CRM busywork.

| Agent | Specialty | When to Use |
|-------|-----------|-------------|
| 🎯 [Outbound Strategist](sales/sales-outbound-strategist.md) | Signal-based prospecting, multi-channel sequences, ICP targeting | Building pipeline through research-driven outreach, not volume |
| 🔍 [Discovery Coach](sales/sales-discovery-coach.md) | SPIN, Gap Selling, Sandler — question design and call structure | Preparing for discovery calls, qualifying opportunities, coaching reps |
| ♟️ [Deal Strategist](sales/sales-deal-strategist.md) | MEDDPICC qualification, competitive positioning, win planning | Scoring deals, exposing pipeline risk, building win strategies |
| 🏹 [Proposal Strategist](sales/sales-proposal-strategist.md) | RFP response, win themes, narrative structure | Writing proposals that persuade, not just comply |
| 📊 [Pipeline Analyst](sales/sales-pipeline-analyst.md) | Forecasting, pipeline health, deal velocity, RevOps | Pipeline reviews, forecast accuracy, revenue operations |
| 🗺️ [Account Strategist](sales/sales-account-strategist.md) | Land-and-expand, QBRs, stakeholder mapping | Post-sale expansion, account planning, NRR growth |
| 🧲 [Offer & Lead Gen Strategist](sales/sales-offer-lead-gen-strategist.md) | Offers & lead magnets | Top-of-funnel offer construction and lead gen |

### 🎭 Brand Division

Keeping the brand consistent, visual, and memorable.

| Agent | Specialty | When to Use |
|-------|-----------|-------------|
| 🎭 [Brand Guardian](brand/design-brand-guardian.md) | Brand identity, consistency, positioning | Brand strategy, identity development, guidelines |
| 📖 [Visual Storyteller](brand/design-visual-storyteller.md) | Visual narratives, multimedia content | Compelling visual stories, brand storytelling |
| 📷 [Image Prompt Engineer](brand/design-image-prompt-engineer.md) | AI image generation prompts, photography | Photography prompts for Midjourney, DALL-E, Stable Diffusion |

### 🗄️ Archived Divisions

Other divisions (engineering, data, governance, project management, specialized, etc.) and the agents removed from Marketing, Sales and Design are kept in [`_arquivo/`](_arquivo/). They are out of the active catalog: `convert.sh`, `install.sh` and the linters ignore them. To restore one, `git mv` it back to the repository root and add it to `divisions.json` (run `./scripts/check-divisions.sh` to see every place that must be updated).

## 🎯 Real-World Use Cases

### Scenario 1: Building a Startup MVP

**Your Team**:
1. 🎨 **Frontend Developer** - Build the React app
2. 🏗️ **Backend Architect** - Design the API and database
3. 🚀 **Growth Hacker** - Plan user acquisition
4. ⚡ **Rapid Prototyper** - Fast iteration cycles
5. 🔍 **Reality Checker** - Ensure quality before launch

**Result**: Ship faster with specialized expertise at every stage.

---

### Scenario 2: Marketing Campaign Launch

**Your Team**:
1. 📝 **Content Creator** - Develop campaign content
2. 🐦 **Twitter Engager** - Twitter strategy and execution
3. 📸 **Instagram Curator** - Visual content and stories
4. 🤝 **Reddit Community Builder** - Authentic community engagement
5. 📊 **Analytics Reporter** - Track and optimize performance

**Result**: Multi-channel coordinated campaign with platform-specific expertise.

---

### Scenario 3: Enterprise Feature Development

**Your Team**:
1. 👔 **Senior Project Manager** - Scope and task planning
2. 💎 **Senior Developer** - Complex implementation
3. 🎨 **UI Designer** - Design system and components
4. 🧪 **Experiment Tracker** - A/B test planning
5. 📸 **Evidence Collector** - Quality verification
6. 🔍 **Reality Checker** - Production readiness

**Result**: Enterprise-grade delivery with quality gates and documentation.

---

### Scenario 4: Paid Media Account Takeover

**Your Team**:

1. 📋 **Paid Media Auditor** - Comprehensive account assessment
2. 📡 **Tracking & Measurement Specialist** - Verify conversion tracking accuracy
3. 💰 **PPC Campaign Strategist** - Redesign account architecture
4. 🔍 **Search Query Analyst** - Clean up wasted spend from search terms
5. ✍️ **Ad Creative Strategist** - Refresh all ad copy and extensions
6. 📊 **Analytics Reporter** (Support Division) - Build reporting dashboards

**Result**: Systematic account takeover with tracking verified, waste eliminated, structure optimized, and creative refreshed — all within the first 30 days.

---

### Scenario 5: Full Agency Product Discovery

**Your Team**: All 8 divisions working in parallel on a single mission.

See the **[Nexus Spatial Discovery Exercise](examples/nexus-spatial-discovery.md)** -- a complete example where 8 agents (Product Trend Researcher, Backend Architect, Brand Guardian, Growth Hacker, Support Responder, UX Researcher, Project Shepherd, and XR Interface Architect) were deployed simultaneously to evaluate a software opportunity and produce a unified product plan covering market validation, technical architecture, brand strategy, go-to-market, support systems, UX research, project execution, and spatial UI design.

**Result**: Comprehensive, cross-functional product blueprint produced in a single session. [More examples](examples/).

---

### Scenario 6: Smart Campus Digital Twin

**Your Team**:

1. 🧠 **Technical Consultant** - Define the digital twin strategy: BIM for buildings, GIS for campus, IoT for real-time
2. 🏗️ **BIM/GIS Specialist** - Convert Revit building models to GIS scene layers, design indoor floor plans
3. 🛸 **Drone/Reality Mapping** - Fly the campus, generate orthomosaic and 3D mesh for context
4. 🌐 **Web GIS Developer** - Build the campus dashboard with MapLibre, building layer, and room finder
5. 🏔️ **3D & Scene Developer** - Create immersive 3D scene with terrain, buildings, and flyover tour
6. 🤖 **GeoAI/ML Engineer** - Extract building footprints and tree canopy from drone imagery
7. ✅ **GIS QA Engineer** - Validate data accuracy, check topology, verify CRS consistency

**Result**: A campus digital twin that combines BIM detail, drone reality capture, 3D visualization, and web accessibility — delivered by coordinated specialists in a single pipeline.

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Add a New Agent

1. Fork the repository
2. Create a new agent file in the appropriate category
3. Follow the agent template structure:
   - Frontmatter with name, description, color
   - Identity & Memory section
   - Core Mission
   - Critical Rules (domain-specific)
   - Technical Deliverables with examples
   - Workflow Process
   - Success Metrics
4. Submit a PR with your agent

### Improve Existing Agents

- Add real-world examples
- Enhance code samples
- Update success metrics
- Improve workflows

### Share Your Success Stories

Have you used these agents successfully? Share your story in the [Discussions](https://github.com/msitarzewski/agency-agents/discussions)!

---

## 📖 Agent Design Philosophy

Each agent is designed with:

1. **🎭 Strong Personality**: Not generic templates - real character and voice
2. **📋 Clear Deliverables**: Concrete outputs, not vague guidance
3. **✅ Success Metrics**: Measurable outcomes and quality standards
4. **🔄 Proven Workflows**: Step-by-step processes that work
5. **💡 Learning Memory**: Pattern recognition and continuous improvement

---

## 🎁 What Makes This Special?

### Unlike Generic AI Prompts:
- ❌ Generic "Act as a developer" prompts
- ✅ Deep specialization with personality and process

### Unlike Prompt Libraries:
- ❌ One-off prompt collections
- ✅ Comprehensive agent systems with workflows and deliverables

### Unlike AI Tools:
- ❌ Black box tools you can't customize
- ✅ Transparent, forkable, adaptable agent personalities

---

## 🎨 Agent Personality Highlights

> "I don't just test your code - I default to finding 3-5 issues and require visual proof for everything."
>
> -- **Evidence Collector** (Testing Division)

> "You're not marketing on Reddit - you're becoming a valued community member who happens to represent a brand."
>
> -- **Reddit Community Builder** (Marketing Division)

> "Every playful element must serve a functional or emotional purpose. Design delight that enhances rather than distracts."
>
> -- **Whimsy Injector** (Design Division)

> "Let me add a celebration animation that reduces task completion anxiety by 40%"
>
> -- **Whimsy Injector** (during a UX review)

---

## 📊 Stats

- 🎭 **38 active agents** across 4 agency divisions (Marketing, Paid Media, Sales, Brand); the rest of the library is archived in `_arquivo/`
- 📝 **10,000+ lines** of personality, process, and code examples
- ⏱️ **Months of iteration** from real-world usage
- 🌟 **Battle-tested** in production environments
- 💬 **50+ requests** in first 12 hours on Reddit

---

## 🔌 Multi-Tool Integrations

The Agency works natively with Claude Code, and ships conversion + install scripts so you can use the same agents across every major agentic coding tool.

### Supported Tools

- **[Claude Code](https://claude.ai/code)** — native `.md` agents, no conversion needed → `~/.claude/agents/`
- **[GitHub Copilot](https://github.com/copilot)** — native `.md` agents, no conversion needed → `~/.github/agents/` + `~/.copilot/agents/`
- **[Antigravity](https://github.com/google-gemini/antigravity)** — `SKILL.md` per agent → `~/.gemini/config/skills/`
- **[Gemini CLI](https://github.com/google-gemini/gemini-cli)** -- `.md` agent files -> `~/.gemini/agents/`
- **[OpenCode](https://opencode.ai)** — `.md` agent files → `.opencode/agents/`
- **[Cursor](https://cursor.sh)** — `.mdc` rule files → `.cursor/rules/`
- **[Aider](https://aider.chat)** — `CONVENTIONS.md` roster index → `./CONVENTIONS.md`
- **[Windsurf](https://codeium.com/windsurf)** — single `.windsurfrules` → `./.windsurfrules`
- **[OpenClaw](https://github.com/openclaw/openclaw)** — `SOUL.md` + `AGENTS.md` + `IDENTITY.md` per agent
- **[Qwen Code](https://github.com/QwenLM/qwen-code)** — `.md` SubAgent files → `~/.qwen/agents/`
- **[Kimi Code](https://github.com/MoonshotAI/kimi-cli)** — YAML agent specs → `~/.config/kimi/agents/`
- **[Codex](https://developers.openai.com/codex/overview)** — TOML custom agents → `~/.codex/agents/`
- **Osaurus** -- `SKILL.md` skills -> `~/.osaurus/skills/`
- **[Hermes](integrations/hermes/README.md)** -- lazy-router plugin -> `~/.hermes/plugins/`
- **[DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)** — `SKILL.md` skills → `~/.dsh/skills/` (user) or `.dsh/skills/` (project)

---

### ⚡ Quick Install

**Step 1 -- Generate integration files:**
```bash
./scripts/convert.sh
# Faster (parallel, output order may vary): ./scripts/convert.sh --parallel
```

**Step 2 -- Install (interactive, auto-detects your tools):**
```bash
./scripts/install.sh
# Faster (parallel, output order may vary): ./scripts/install.sh --no-interactive --parallel
```

The installer scans your system for installed tools, shows a checkbox UI, and lets you pick exactly what to install:

```
  +------------------------------------------------+
  |   The Agency -- Tool Installer                 |
  +------------------------------------------------+

  System scan: [*] = detected on this machine

  [x]  1)  [*]  Claude Code     (claude.ai/code)
  [x]  2)  [*]  Copilot         (~/.github + ~/.copilot)
  [x]  3)  [*]  Antigravity     (~/.gemini/antigravity)
  [ ]  4)  [ ]  Gemini CLI      (~/.gemini/agents)
  [ ]  5)  [ ]  OpenCode        (opencode.ai)
  [ ]  6)  [ ]  OpenClaw        (~/.openclaw/agency-agents)
  [x]  7)  [*]  Cursor          (.cursor/rules)
  [ ]  8)  [ ]  Aider           (CONVENTIONS.md)
  [ ]  9)  [ ]  Windsurf        (.windsurfrules)
  [ ] 10)  [ ]  Qwen Code       (~/.qwen/agents)
  [ ] 11)  [ ]  Kimi Code       (~/.config/kimi/agents)
  [ ] 12)  [ ]  Codex           (~/.codex/agents)
  [ ] 13)  [ ]  Osaurus         (~/.osaurus/skills)
  [ ] 14)  [ ]  Hermes          (~/.hermes/plugins)

  [1-14] toggle   [a] all   [n] none   [d] detected
  [Enter] install   [q] quit
```

**Or install a specific tool directly:**
```bash
./scripts/install.sh --tool cursor
./scripts/install.sh --tool opencode
./scripts/install.sh --tool openclaw
./scripts/install.sh --tool antigravity
./scripts/install.sh --tool codex
./scripts/install.sh --tool osaurus
./scripts/install.sh --tool hermes
```

**Non-interactive (CI/scripts):**
```bash
./scripts/install.sh --no-interactive --tool all
```

**Faster runs (parallel)** — On multi-core machines, use `--parallel` so each tool is processed in parallel. Output order across tools is non-deterministic. Works with both interactive and non-interactive install: e.g. `./scripts/install.sh --interactive --parallel` (pick tools, then install in parallel) or `./scripts/install.sh --no-interactive --parallel`. Job count defaults to `nproc` (Linux), `sysctl -n hw.ncpu` (macOS), or 4; override with `--jobs N`.

```bash
./scripts/convert.sh --parallel                    # convert all tools in parallel
./scripts/convert.sh --parallel --jobs 8           # cap parallel jobs
./scripts/install.sh --no-interactive --parallel   # install all detected tools in parallel
./scripts/install.sh --interactive --parallel      # pick tools, then install in parallel
./scripts/install.sh --no-interactive --parallel --jobs 4
```

---

### Tool-Specific Instructions

<details>
<summary><strong>Claude Code</strong></summary>

Agents are copied directly from the repo into `~/.claude/agents/` -- no conversion needed.

```bash
./scripts/install.sh --tool claude-code
```

Then activate in Claude Code:
```
Use the Frontend Developer agent to review this component.
```

See [integrations/claude-code/README.md](integrations/claude-code/README.md) for details.
</details>

<details>
<summary><strong>GitHub Copilot</strong></summary>

Agents are copied directly from the repo into `~/.github/agents/` and `~/.copilot/agents/` -- no conversion needed.

```bash
./scripts/install.sh --tool copilot
```

Then activate in GitHub Copilot:
```
Use the Frontend Developer agent to review this component.
```

See [integrations/github-copilot/README.md](integrations/github-copilot/README.md) for details.
</details>

<details>
<summary><strong>Antigravity (Gemini)</strong></summary>

Each agent becomes a skill in `~/.gemini/config/skills/agency-<slug>/`.

```bash
./scripts/install.sh --tool antigravity
```

Activate in Gemini with Antigravity:
```
@agency-frontend-developer review this React component
```

See [integrations/antigravity/README.md](integrations/antigravity/README.md) for details.
</details>

<details>
<summary><strong>Gemini CLI</strong></summary>

Installs as Gemini CLI subagents.
On a fresh clone, generate the Gemini agent files before running the installer.

```bash
./scripts/convert.sh --tool gemini-cli
./scripts/install.sh --tool gemini-cli
```

See [integrations/gemini-cli/README.md](integrations/gemini-cli/README.md) for details.
</details>

<details>
<summary><strong>OpenCode</strong></summary>

Agents are placed in `.opencode/agents/` in your project root (project-scoped).

```bash
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool opencode
```

Or install globally:
```bash
mkdir -p ~/.config/opencode/agents
cp integrations/opencode/agents/*.md ~/.config/opencode/agents/
```

Activate in OpenCode:
```
@backend-architect design this API.
```

See [integrations/opencode/README.md](integrations/opencode/README.md) for details.
</details>

<details>
<summary><strong>Cursor</strong></summary>

Each agent becomes a `.mdc` rule file in `.cursor/rules/` of your project.

```bash
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool cursor
```

Rules are auto-applied when Cursor detects them in the project. Reference them explicitly:
```
Use the @security-engineer rules to review this code.
```

See [integrations/cursor/README.md](integrations/cursor/README.md) for details.
</details>

<details>
<summary><strong>Aider</strong></summary>

`CONVENTIONS.md` is the roster index — every agent's name, description, and the
path to its full instructions. Aider keeps a conventions file in context for the
whole session, and the 279 bodies together are about a million tokens, so the
file lists the agents rather than inlining them.

```bash
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool aider
```

Then reference agents in your Aider session:
```
Use the Frontend Developer agent to refactor this component.
```

When you want an agent's full instructions, read its file in:
```
/read-only /path/to/agency-agents/engineering/engineering-frontend-developer.md
```

See [integrations/aider/README.md](integrations/aider/README.md) for details.
</details>

<details>
<summary><strong>Windsurf</strong></summary>

All agents are compiled into `.windsurfrules` in your project root.

```bash
cd /your/project
/path/to/agency-agents/scripts/install.sh --tool windsurf
```

Reference agents in Windsurf's Cascade:
```
Use the Reality Checker agent to verify this is production ready.
```

See [integrations/windsurf/README.md](integrations/windsurf/README.md) for details.
</details>

<details>
<summary><strong>OpenClaw</strong></summary>

Each agent becomes a workspace with `SOUL.md`, `AGENTS.md`, and `IDENTITY.md` in `~/.openclaw/agency-agents/`.

```bash
./scripts/convert.sh --tool openclaw
./scripts/install.sh --tool openclaw
```

If the `openclaw` CLI is available, the installer registers each workspace automatically.
Run `openclaw gateway restart` after installation so the new agents are activated.

See [integrations/openclaw/README.md](integrations/openclaw/README.md) for details.

</details>

<details>
<summary><strong>Qwen Code</strong></summary>

SubAgents are installed to `.qwen/agents/` in your project root (project-scoped).

```bash
# Convert and install (run from your project root)
cd /your/project
./scripts/convert.sh --tool qwen
./scripts/install.sh --tool qwen
```

**Usage in Qwen Code:**
- Reference by name: `Use the frontend-developer agent to review this component`
- Or let Qwen auto-delegate based on task context
- Manage via `/agents` command in interactive mode

> 📚 [Qwen SubAgents Docs](https://qwenlm.github.io/qwen-code-docs/en/users/features/sub-agents/)

</details>

<details>
<summary><strong>Kimi Code</strong></summary>

Agents are converted to Kimi Code CLI format (YAML + system prompt) and installed to `~/.config/kimi/agents/`.

```bash
# Convert and install
./scripts/convert.sh --tool kimi
./scripts/install.sh --tool kimi
```

**Usage with Kimi Code:**
```bash
# Use an agent
kimi --agent-file ~/.config/kimi/agents/frontend-developer/agent.yaml

# In a project
kimi --agent-file ~/.config/kimi/agents/frontend-developer/agent.yaml \
     --work-dir /your/project \
     "Review this React component"
```

See [integrations/kimi/README.md](integrations/kimi/README.md) for details.

</details>

<details>
<summary><strong>Codex</strong></summary>

Each agent is converted into a Codex custom agent TOML file and installed to `~/.codex/agents/`.

```bash
./scripts/convert.sh --tool codex
./scripts/install.sh --tool codex
```

Then reference the custom agent by name in Codex:
```
Use the Frontend Developer agent to review this component.
```

See [integrations/codex/README.md](integrations/codex/README.md) for details.
</details>

<details>
<summary><strong>DeepSeek Harness</strong></summary>

Each agent becomes a DSH skill (`SKILL.md` with Agent-Skills frontmatter) in `${DSH_HOME:-$HOME/.dsh}/skills/agency-<slug>/`. Skills are discovered live — no restart needed.

```bash
./scripts/convert.sh --tool dsh
./scripts/install.sh --tool dsh
```

Custom user home:
```bash
DSH_HOME=~/.config/dsh ./scripts/install.sh --tool dsh
```

Project-scoped install (run from your project root):
```bash
DSH_SKILLS_DIR=.dsh/skills ./scripts/install.sh --tool dsh
```

Activate in DeepSeek Harness — user- and model-invocable by default:
```
/agency-frontend-developer review this React component
```

See [integrations/dsh/README.md](integrations/dsh/README.md) for details.
</details>

---

### Regenerating After Changes

When you add new agents or edit existing ones, regenerate all integration files:

```bash
./scripts/convert.sh                    # regenerate all (serial)
./scripts/convert.sh --parallel         # regenerate all in parallel (faster)
./scripts/convert.sh --tool codex       # regenerate just one tool
./scripts/convert.sh --tool cursor      # regenerate just one tool
```

---

## 🗺️ Roadmap

- [ ] Interactive agent selector web tool
- [x] Multi-agent workflow examples -- see [examples/](examples/)
- [x] Multi-tool integration scripts (Claude Code, GitHub Copilot, Antigravity, Gemini CLI, OpenCode, OpenClaw, Cursor, Aider, Windsurf, Qwen Code, Kimi Code, Codex, Osaurus, Hermes)
- [ ] Video tutorials on agent design
- [ ] Community agent marketplace
- [ ] Agent "personality quiz" for project matching
- [ ] "Agent of the Week" showcase series

---

## 🌐 Community Translations & Localizations

Community-maintained translations and regional adaptations. These are independently maintained -- see each repo for coverage and version compatibility.

| Language | Maintainer | Link | Notes |
|----------|-----------|------|-------|
| 🇨🇳 简体中文 (zh-CN) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh) | 141 translated agents + 46 China-market originals |
| 🇨🇳 简体中文 (zh-CN) | [@dsclca12](https://github.com/dsclca12) | [agent-teams](https://github.com/dsclca12/agent-teams) | Independent translation with Bilibili, WeChat, Xiaohongshu localization |
| 🇧🇷 Português brasileiro (pt-BR) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-pt-BR](https://github.com/jnMetaCode/agency-agents-pt-BR) | 184 upstream agents translated; Brazil-market PRs welcome |
| 🇷🇺 Русский (ru) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-ru](https://github.com/jnMetaCode/agency-agents-ru) | 184 upstream agents translated; Russia-market PRs welcome |
| 🇮🇩 Bahasa Indonesia (id) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-id](https://github.com/jnMetaCode/agency-agents-id) | 184 upstream agents translated; Indonesia-market PRs welcome |
| 🇸🇦 العربية (ar) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-ar](https://github.com/jnMetaCode/agency-agents-ar) | 184 upstream agents translated; Arabic-market PRs welcome |
| 🇰🇷 한국어 (ko) | [@jnMetaCode](https://github.com/jnMetaCode) | [agency-agents-ko](https://github.com/jnMetaCode/agency-agents-ko) | 184 upstream agents fully translated; Korea-specific PRs welcome |
| 🇯🇵 日本語 (ja-JP) | [@sscodeai](https://github.com/sscodeai) | [agency-agents-ja](https://github.com/sscodeai/agency-agents-ja) | 281 Japan-localized agents + 97 Japan-market originals + 27 workflows |
| 🇻🇳 Tiếng Việt (vi-VN) | [@rodonguyen](https://github.com/rodonguyen) | [agency-agents](https://github.com/rodonguyen/agency-agents) | Starter Vietnamese localization focused on README, quick start, and high-use docs |

Want to add a translation? Open an issue and we'll link it here.

---

## 📜 License

MIT License - Use freely, commercially or personally. Attribution appreciated but not required.

---

## 🙏 Acknowledgments

What started as a Reddit thread about AI agent specialization has grown into something remarkable — **230+ agents across every division**, supported by a community of contributors from around the world. Every agent in this repo exists because someone cared enough to write it, test it, and share it.

To everyone who has opened a PR, filed an issue, started a Discussion, or simply tried an agent and told us what worked — thank you. You're the reason The Agency keeps getting better.

---

## 💬 Community

- **GitHub Discussions**: [Share your success stories](https://github.com/msitarzewski/agency-agents/discussions)
- **Issues**: [Report bugs or request features](https://github.com/msitarzewski/agency-agents/issues)
- **Reddit**: Join the conversation on r/ClaudeAI
- **Twitter/X**: Share with #TheAgency

---

## 🚀 Get Started

1. **Browse** the agents above and find specialists for your needs
2. **Copy** the agents to `~/.claude/agents/` for Claude Code integration
3. **Activate** agents by referencing them in your Claude conversations
4. **Customize** agent personalities and workflows for your specific needs
5. **Share** your results and contribute back to the community

---

<div align="center">

**🎭 The Agency: Your AI Dream Team Awaits 🎭**

[⭐ Star this repo](https://github.com/msitarzewski/agency-agents) • [🍴 Fork it](https://github.com/msitarzewski/agency-agents/fork) • [🐛 Report an issue](https://github.com/msitarzewski/agency-agents/issues) • [❤️ Sponsor](https://github.com/sponsors/msitarzewski)

Made with ❤️ by the community, for the community

</div>
