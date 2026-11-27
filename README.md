# IEC Agentic AI Developer Course: Cohort 37

This repository contains all the assignments for the **Agentic AI Developer** course, Cohort 37, organized by **IEC**.

## Course Team

| Role | Name |
|---|---|
| Trainer | Sir Talha Khan |
| Collaborator | Tanzeel Ahmad |

## Assignments

| # | Assignment | Folder | Status |
|---|---|---|---|
| 1 | Two-provider LLM cost tracker (Gemini + Groq) | [`A1-cost-tracker`](./A1-cost-tracker) | Done |
| 2 | Messy text to JSON (Gemini structured output + Pydantic) | [`Messy-Text`](./Messy-Text) | Done |
| 3 | Coming soon | | |

Each assignment lives in its own folder with its own README that explains the setup and how to run it.

## Repository Structure

```text
IEC-proje/
├── A1-cost-tracker/    # Assignment 1
├── Messy-Text/         # Assignment 2
└── README.md           # This file
```

## General Setup

Most assignments use Python with `uv`:

```bash
cd <assignment-folder>
uv sync
cp .env.example .env   # add your own API keys in .env
```

API keys are never committed to this repository. Each folder has a `.env.example` showing which keys are needed.

## Author

Laraib ([@Laraib-code23](https://github.com/Laraib-code23))
