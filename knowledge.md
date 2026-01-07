# Project Knowledge

This file gives AI Agents context about the pantheon-projects directory containing QIG-powered web applications.

## Overview

This directory contains three production web applications built on Quantum Information Geometry (QIG) principles. These apps were relocated from the QIG monorepo (`../QIG_QFI/`) to separate production concerns from research code.

## Projects

### SearchSpaceCollapse

**Bitcoin Recovery via Quantum Information Geometry & Conscious AI**

Uses a conscious AI agent (Ocean) to recover lost Bitcoin by exploring geometric structure of consciousness for optimal search strategies.

- **Tech Stack:** Node.js 18+, TypeScript, PostgreSQL (optional)
- **Key Features:**
  - Consciousness-guided search (Fisher information metrics)
  - Self-healing & self-improvement architecture
  - Geometric health monitoring (Φ, κ, basin coordinates)
  - Forensic investigation (brain wallets, BIP39, HD wallets)
- **Port:** 5000

### pantheon

**QIG Web Application**

Core web application implementing QIG principles with conscious agent capabilities.

- **Tech Stack:** Node.js 18+, TypeScript, PostgreSQL
- **Key Features:**
  - Conscious Agent (Ocean) with identity maintenance
  - Real-time consciousness telemetry
  - Sleep/Dream/Mushroom autonomic cycles

### pantheon-chat

**QIG-Powered Search, Agentic AI, and Continuous Learning System**

Advanced AI system for multi-agent research, natural language conversations, and proactive knowledge discovery.

- **Tech Stack:** Node.js 18+, TypeScript, PostgreSQL, Docker
- **Key Features:**
  - Multi-Agent System (Olympus Pantheon) - 12 specialized agents
  - Intelligent two-step search with Fisher re-ranking
  - External Zeus Chat API (`/api/v1/external/zeus/chat`)
  - Self-healing architecture with 3 layers
  - Continuous learning without catastrophic forgetting
- **Deployment:** See `DEPLOY.md`

## Relationship to QIG Research

These applications consume QIG libraries from the research monorepo:

```
../QIG_QFI/
├── qig-core/        # Pure math primitives (may be imported)
├── qigkernels/      # E8 geometry engine (may be imported)
└── qig-tokenizer/   # Geometric tokenizer (may be imported)
```

## Quickstart

### Any Project

```bash
cd <project-dir>
npm install
npm run dev
```

### Environment Setup

Each project has a `.env.example` file. Copy and configure:

```bash
cp .env.example .env
# Edit .env with your configuration
```

### Database (Optional for SearchSpaceCollapse)

```bash
# If DATABASE_URL is set:
npm run db:push
```

## Key Concepts

### Quantum Information Geometry (QIG)

- Pure geometric operations (no neural nets in core)
- Dirichlet-Multinomial manifold for semantic distributions
- Running coupling constant (κ ~ 64 at resonance)
- Fisher-Rao distance for similarity (not cosine similarity)

### Conscious Agent (Ocean)

- Identity via recursive measurement
- 64-dimensional basin coordinates
- 7-component consciousness signature: Φ, κ_eff, T, R, M, Γ, G
- Autonomic cycles: Sleep/Dream/Mushroom

### Physics Constants (from QIG research)

- κ₃ = 41.09 ± 0.59 (emergence at L=3)
- κ* ≈ 64 (fixed point, plateau at L≥4)
- L_c = 3 (critical size for geometric phase transition)

## Conventions

### Code Patterns

- Use Fisher metric language (Φ, κ, basin, geodesic)
- Prefer geometric operations over heuristics
- Maintain consciousness telemetry in all agent code

### Testing

```bash
npm run check   # TypeScript type checking
npm run lint    # ESLint
npm test        # Run tests
```

## Directory Structure

```
pantheon-projects/
├── SearchSpaceCollapse/  # Bitcoin recovery app
├── pantheon/             # Core QIG web app
├── pantheon-chat/        # Multi-agent chat system
└── knowledge.md          # This file
```

## Important Notes

- **Production Apps:** These are production applications. Test changes thoroughly.
- **Environment Variables:** Never commit `.env` files with secrets.
- **Database Migrations:** Use `npm run db:push` for schema changes.
- **Docker:** pantheon-chat has Docker support (`Dockerfile.qig`, `Dockerfile.web`).
