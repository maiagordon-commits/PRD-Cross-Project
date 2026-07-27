# Cursor Cloud Agents: Step-by-Step Creation Guide

This guide walks you through everything you need to know to create and configure Cursor Cloud Agents for your team.

---

## Table of Contents

1. [What Are Cloud Agents?](#what-are-cloud-agents)
2. [Prerequisites](#prerequisites)
3. [Step 1: Connect Source Control](#step-1-connect-source-control)
4. [Step 2: Create a Development Environment](#step-2-create-a-development-environment)
5. [Step 3: Configure Secrets and Environment Variables](#step-3-configure-secrets-and-environment-variables)
6. [Step 4: Launch Your First Cloud Agent](#step-4-launch-your-first-cloud-agent)
7. [Step 5: Using Cloud Agents from Different Surfaces](#step-5-using-cloud-agents-from-different-surfaces)
8. [Advanced Configuration](#advanced-configuration)
9. [Multi-Repo Environments](#multi-repo-environments)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## What Are Cloud Agents?

Cloud Agents are AI-powered development assistants that run in isolated virtual machines (VMs) in the cloud. Unlike local agents that run on your machine, Cloud Agents:

- Run in their own Ubuntu-based development environment
- Can build, test, and verify code changes autonomously
- Work in parallel without consuming local machine resources
- Can access MCP servers, databases, APIs, and third-party services
- Produce artifacts like screenshots, videos, and logs to demonstrate their work
- Create merge-ready pull requests when they complete tasks

**Key Benefits:**
- Run multiple agents simultaneously
- No need for your local machine to be connected
- Full development environment access (not just code editing)
- Can test and verify work before creating PRs

---

## Prerequisites

Before you can create and use Cloud Agents, ensure you have:

| Requirement | Details |
|-------------|---------|
| **Cursor Plan** | Pro plan ($20/month) or higher |
| **Usage-Based Billing** | Enabled with at least a $10 spending limit |
| **Privacy Mode** | Must be disabled (Cloud VMs need to receive your code) |
| **Source Control** | GitHub, GitLab, Azure DevOps, or Bitbucket Cloud connected with read-write permissions |

---

## Step 1: Connect Source Control

A Cursor account admin must connect source control before anyone can start cloud agents.

### For GitHub:

1. Go to [Cursor Integrations](https://www.cursor.com/dashboard/integrations)
2. Click **Connect** next to GitHub
3. Authorize Cursor to access your repositories
4. Select the repositories you want to use with Cloud Agents
5. Ensure you have read-write permissions to the repos

### For Other Providers:

- **GitLab (Cloud and Self-Hosted)**: Same process through Integrations dashboard
- **Bitbucket Cloud**: Connect via Integrations dashboard
- **Azure DevOps**: Connect via Integrations dashboard

**Important:** You need read-write privileges to your repo and any dependent repos or submodules.

---

## Step 2: Create a Development Environment

Environment setup is the **most important step** for effective Cloud Agents. An agent without a proper environment is like an engineer without a computer.

### Navigate to Cloud Agents Dashboard

Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents#environments)

### Choose Your Setup Method

#### Option A: Agent-Driven Setup (Recommended)

This is the easiest approach and takes about 10 minutes:

1. Click **Create New Environment** in the dashboard
2. Connect your GitHub/GitLab/Azure DevOps/Bitbucket account
3. Select one or more repositories
4. Provide environment variables and secrets needed to install dependencies
5. Watch the agent set up the environment in a shared terminal session
6. Once Cursor verifies the code is working, **save a snapshot** of the VM
7. Commit the configuration to `.cursor/environment.json` so your team benefits

#### Option B: Manual Dockerfile Setup (Advanced)

For more control, configure with a Dockerfile:

1. Create a `.cursor/` directory in your repository root
2. Create a `Dockerfile` inside `.cursor/`
3. Create `.cursor/environment.json` with your configuration:

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "install": "npm install"
}
```

**Dockerfile Guidelines:**
- Install system-level dependencies, compilers, debuggers
- Do NOT `COPY` the full project (Cursor manages the workspace)
- Use build secrets for private package registries

### Environment Resolution Order

Cursor resolves environment configuration using the first match:

1. `.cursor/environment.json` in the repository
2. A personal saved environment
3. A team saved environment

---

## Step 3: Configure Secrets and Environment Variables

Cloud Agents need environment variables and secrets (API keys, database credentials) to run and test code.

### Add Secrets via Dashboard

1. Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents)
2. Navigate to the **Secrets** tab
3. Add your secrets as key-value pairs

**Types of Secrets:**

| Type | Scope |
|------|-------|
| **User Secrets** | Available only to your agents |
| **Team Secrets** | Shared across team members |
| **Environment-Scoped** | Only available to agents using specific environments |

### Common Secrets to Add:

- `DATABASE_URL` - Database connection string
- `API_KEY` - External API keys
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `GITHUB_TOKEN` - For private package access
- Login credentials (username, email, password)
- TOTP secrets for 2FA (use `oathtool --totp -b "$TOTP_SECRET"` to generate codes)

### For Monorepos with Multiple .env Files:

- Add values from all `.env.local` files to the Secrets tab
- Use unique variable names when keys overlap (e.g., `NEXTJS_*`, `CONVEX_*`)

---

## Step 4: Launch Your First Cloud Agent

Once your environment is configured, you can launch a Cloud Agent.

### From Cursor Desktop:

1. Open Cursor IDE
2. Look at the agent input dropdown
3. Select **Cloud** instead of the default local mode
4. Type your task description
5. Press Enter to start the agent

### From Cursor Web:

1. Go to [cursor.com/agents](https://cursor.com/agents)
2. Select your repository
3. Type your task
4. Click to start the agent

### What Happens When an Agent Runs:

1. Cursor spins up an isolated Ubuntu VM
2. Clones your repository
3. Checks out a dedicated `agent/` branch from main
4. Runs your `install` command (e.g., `npm install`)
5. Starts any configured `start` commands
6. Works on your task autonomously
7. Tests and verifies changes
8. Opens a pull request when complete
9. Sends you a notification (email, desktop, or Slack)

---

## Step 5: Using Cloud Agents from Different Surfaces

Cloud Agents can be triggered from multiple interfaces:

### From Slack

1. Install the Cursor Slack app: [Installation Page](https://cursor.com/api/install-slack-app)
2. Mention `@cursor` with your prompt

**Commands:**
```
@Cursor [prompt]              # Start an agent or add follow-up
@Cursor settings              # Configure defaults
@Cursor agent [prompt]        # Force create a new agent in a thread
@Cursor list my agents        # Show running agents
@Cursor help                  # Get command list
```

**Options:**
```
@Cursor in acme/backend fix the login bug       # Specify repo
@Cursor with opus fix the bug                    # Specify model
@Cursor use the Platform environment update API  # Use named environment
@Cursor branch=dev fix the tests                 # Specify branch
```

### From GitHub/Bitbucket

Comment `@cursor` on any:
- GitHub Pull Request
- GitHub Issue
- Bitbucket Pull Request

### From Linear

Mention `@Cursor` on any Linear issue

### From iOS App

Download the [Cursor iOS app](https://cursor.com/docs/cloud-agent/mobile.md) to start and manage agents on the go

### Via API

Use the [Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints.md) for programmatic access

---

## Advanced Configuration

### The environment.json File

Create `.cursor/environment.json` for code-defined configuration:

**Using a snapshot:**
```json
{
  "snapshot": "snapshot-20260212-00000000-0000-0000-0000-000000000000",
  "install": "npm install"
}
```

**Using a Dockerfile:**
```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "context": ".."
  },
  "install": "pnpm install && ./custom_script.sh"
}
```

### Update Commands

The `install` command runs when a new machine boots:

- Should be idempotent (safe to run multiple times)
- Common examples: `npm install`, `pip install -r requirements.txt`, `bazel build`
- Results are cached for faster subsequent starts

### Startup Commands

Configure processes that should stay alive while the agent runs:

```json
{
  "start": "sudo service docker start",
  "terminals": ["npm run dev", "npm run api"]
}
```

### AGENTS.md Instructions

Add cloud-specific instructions to your `AGENTS.md` file:

```markdown
## Cursor Cloud Specific Instructions

### Development Environment Setup
- Run `npm install` before starting any work
- Start the dev server with `npm run dev`

### Testing
- Run `npm test` to execute unit tests
- Run `npm run e2e` for end-to-end tests

### Deployment
- Use `npm run deploy:staging` for staging deployments
```

---

## Multi-Repo Environments

Use multi-repo environments when your agent needs to work across multiple repositories.

### When to Use:

- Frontend, backend, infrastructure in separate repos
- Shared libraries in their own repos
- Microservices architecture

### Setup:

1. Go to [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents#environments)
2. Create a new environment
3. Select **multiple repositories**
4. Configure which repos should be cloned and into which directories

### Benefits:

- Agent can inspect the full workspace
- Make coordinated changes across repos
- Run tests that span multiple repos
- Open pull requests in all affected repos

---

## Best Practices

### Environment Setup

- **Take snapshots** after successful setup - future agents start faster
- **Commit environment.json** to share with your team
- **Keep update scripts fast** - complex setup slows agent startup
- **Use AGENTS.md** for task-specific instructions agents can discover

### Secrets Management

- Store secrets in the dashboard, not in code
- Use environment-scoped secrets for staging vs. production
- Rotate credentials regularly
- Never commit `.env` files with real secrets

### Task Design

- Give clear, specific task descriptions
- Include success criteria when possible
- Break large tasks into smaller, focused requests
- Reference relevant files or documentation

### Team Collaboration

- Share agent URLs with teammates for visibility
- Enable [team follow-ups](https://cursor.com/docs/cloud-agent/settings.md#team-follow-ups) if needed
- Use channel settings in Slack for consistent defaults
- Set up routing rules for automatic repo/environment selection

---

## Troubleshooting

### Agent runs are not starting

- Ensure you're logged in to Cursor
- Verify your GitHub/GitLab/Azure DevOps/Bitbucket account is connected
- Check that you have necessary repository permissions
- Confirm you're on a paid Cursor plan with usage-based billing enabled

### Secrets aren't available to the agent

- Verify secrets are added in [Cloud Agents Dashboard](https://cursor.com/dashboard/cloud-agents)
- Secrets are workspace/team-scoped - ensure you're using the correct account
- Try restarting the cloud agent after adding new secrets

### Slack integration not working

- Verify workspace admin has installed the Cursor Slack app
- Check that you have proper permissions
- Run `@Cursor settings` to verify configuration

### Teammate can't open my agent

- Teammate must belong to the same Cursor team
- They need to connect their own source control account
- They need access to the repository the agent worked in

### Environment configuration issues

- Check for error messages in the agent view
- Verify your Dockerfile builds successfully locally
- Ensure all required secrets are configured
- Check that your update script is idempotent

---

## Quick Reference Card

| Action | How to Do It |
|--------|--------------|
| Create environment | [Dashboard](https://cursor.com/dashboard/cloud-agents#environments) → Create New |
| Add secrets | Dashboard → Secrets tab → Add secret |
| Start agent (Desktop) | Agent input → Select "Cloud" → Type task |
| Start agent (Web) | [cursor.com/agents](https://cursor.com/agents) |
| Start agent (Slack) | `@Cursor [your task]` |
| Start agent (GitHub) | Comment `@cursor` on PR/issue |
| View running agents | [cursor.com/agents](https://cursor.com/agents) or `@Cursor list my agents` |
| Configure Slack channel | `@Cursor settings` |

---

## Additional Resources

- [Cloud Agent Overview](https://cursor.com/docs/cloud-agent)
- [Cloud Agent Setup](https://cursor.com/docs/cloud-agent/setup.md)
- [Cloud Agent Capabilities](https://cursor.com/docs/cloud-agent/capabilities.md)
- [Cloud Agent Security](https://cursor.com/docs/cloud-agent/security-network.md)
- [Slack Integration](https://cursor.com/docs/integrations/slack)
- [Cloud Agent API](https://cursor.com/docs/cloud-agent/api/endpoints.md)

---

*Last updated: July 2026*
