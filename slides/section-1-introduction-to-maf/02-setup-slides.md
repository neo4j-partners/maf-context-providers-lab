---
marp: true
theme: default
paginate: true
---

<style>
section {
  --marp-auto-scaling-code: false;
}

li {
  opacity: 1 !important;
  animation: none !important;
  visibility: visible !important;
}

/* Disable all fragment animations */
.marp-fragment {
  opacity: 1 !important;
  visibility: visible !important;
}

ul > li,
ol > li {
  opacity: 1 !important;
}
</style>


# Setup Your Development Environment

---

## What You Need

Two things to set up:

1. **Neo4j Sandbox** -- a hosted Neo4j instance with the recommendations movie dataset
2. **GitHub Codespace** -- a cloud development environment with all dependencies pre-installed

No local installation required.

---

## Step 1: Create a Neo4j Sandbox

1. Go to [sandbox.neo4j.com](https://sandbox.neo4j.com)
2. Sign up for a free account (or sign in)
3. Select the **Recommendations** dataset
4. Click **Create** to launch your sandbox
5. Download your credentials and save them

You will need the **Bolt URL**, **username**, and **password**.

> **Important:** Save your credentials now. You cannot retrieve the password later.

---

## The Recommendations Dataset

The sandbox includes a movie database with:

- **Movies** with titles, plots, years, and genres
- **Actors** and **directors** linked to movies
- **User ratings** and reviews
- **Pre-computed vector indexes** on movie plot embeddings

You will use this data throughout the workshop for semantic search and graph traversal.

---

## Step 2: Launch GitHub Codespaces

Open the workshop repository in GitHub Codespaces:

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/neo4j-partners/genai-maf-context-providers)

You will be prompted to enter four **secrets**:

| Secret | Value |
|--------|-------|
| `OPENAI_API_KEY` | Your OpenAI API key (or provided by instructor) |
| `NEO4J_URI` | Bolt URI from your sandbox (e.g. `neo4j+s://xxxxx.databases.neo4j.io`) |
| `NEO4J_USERNAME` | Your Neo4j username (usually `neo4j`) |
| `NEO4J_PASSWORD` | Password from your sandbox |

---

## What the Codespace Does

Once launched, the Codespace automatically:

- Installs **Python 3.12** and all required packages
- Installs `agent-framework`, `openai`, `neo4j-graphrag`, and Jupyter
- Generates your **`.env`** file from the secrets you provided

> **Note:** The Codespace takes **3 to 5 minutes** to fully launch. Wait until the `.env` file appears before running labs.

---

## Running the Notebooks

Each lab is a **Jupyter notebook**. To run one:

1. Open the notebook file in the Codespace
2. Click **Select Kernel** (top right)
3. Choose **Python Environments**
4. Select **Python 3.12.11**

You are now ready to run cells.

---

## Step 3: Verify Your Setup

Run the test environment script:

```bash
python genai-maf-context-providers/test_environment.py
```

You should see confirmation that your **OpenAI** and **Neo4j** connections are working.

---

## Step 4: Load Embeddings and Create Indexes

> **You must run this before starting the labs.** Without it, vector and fulltext searches will fail.

```bash
python genai-maf-context-providers/setup.py
```

The script will:

- Load **500 movie plot embeddings** into your Neo4j database
- Create the `moviePlots` **vector index** (1536 dimensions, cosine similarity)
- Create the `moviePlotsFulltext` **fulltext index**
- Wait for indexes to come online and verify the setup

You should see `Setup complete!` when it finishes.

---

## Environment Checklist

Before moving on, confirm:

- [ ] Neo4j Sandbox is running with the Recommendations dataset
- [ ] GitHub Codespace is launched and `.env` file is populated
- [ ] `test_environment.py` passes (OpenAI + Neo4j connections working)
- [ ] `setup.py` completes successfully (embeddings loaded, indexes created)

---

## Summary

You have:

- Created a **Neo4j Sandbox** with the recommendations movie dataset
- Launched a **GitHub Codespace** with credentials and dependencies
- Verified your **environment** is working
- Loaded **embeddings and indexes** for later labs

**Next:** Create your first agent with a tool that queries movie data.
