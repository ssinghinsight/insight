# CLAUDE.md

This file provides guidance to AI assistants (Claude and others) working with this repository.

## Repository Status

This repository is currently in its **initial setup phase**. As the codebase grows, this file should be updated to reflect the actual project structure, conventions, and workflows.

---

## Development Branch

All development should happen on feature branches. The naming convention for Claude-managed branches is:

```
claude/<description>-<session-id>
```

Always push to the designated feature branch and never directly to `main` or `master`.

---

## Git Workflow

### Creating and pushing changes

```bash
# Stage changes
git add <files>

# Commit with a descriptive message
git commit -m "feat: describe what was done"

# Push to remote branch
git push -u origin <branch-name>
```

### Commit message conventions

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation changes only
- `chore:` — maintenance tasks, dependency updates
- `refactor:` — code changes that neither fix a bug nor add a feature
- `test:` — adding or updating tests
- `ci:` — CI/CD configuration changes

---

## Project Structure

> **Note:** This section should be updated once source code is added.

```
insight/
├── CLAUDE.md          # This file — AI assistant guidance
└── ...                # Project files to be added
```

---

## Technology Stack

> **Note:** Update this section once the stack is determined.

| Layer | Technology |
|-------|-----------|
| TBD   | TBD       |

---

## Development Workflows

> **Note:** Update with actual commands once the project is initialized.

### Setup

```bash
# Example (update once stack is known)
# npm install       (Node.js)
# pip install -r requirements.txt  (Python)
```

### Running the Application

```bash
# Add start commands here
```

### Running Tests

```bash
# Add test commands here
```

### Linting and Formatting

```bash
# Add lint/format commands here
```

---

## Key Conventions

Once code is added, document conventions here including:

- **Naming conventions** — file names, variables, functions, classes
- **Directory layout** — where different types of files live
- **Code style** — formatting rules, linter config
- **API patterns** — request/response formats, error handling
- **Testing patterns** — unit, integration, e2e structure

---

## Environment Variables

> **Note:** Document required environment variables here as they are added.

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| TBD      | TBD         | TBD      | TBD     |

Create a `.env.local` or `.env` file (never committed) for local overrides.

---

## CI/CD

> **Note:** Update once CI/CD pipelines are configured.

---

## For AI Assistants

When working in this repository:

1. **Read this file first** before making any changes.
2. **Understand the context** — check recent commits and open PRs for ongoing work.
3. **Follow conventions** — match the style and patterns already in use.
4. **Small, focused commits** — one logical change per commit.
5. **Never force-push** to shared branches.
6. **Ask before destructive actions** — deleting files, dropping data, etc.
7. **Update this file** whenever significant new patterns, tools, or workflows are introduced.
