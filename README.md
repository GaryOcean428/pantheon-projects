# Pantheon Projects

QIG-powered production web applications built on Quantum Information Geometry (QIG) principles.

## Projects

| Project | Description | Status |
|---------|-------------|--------|
| [SearchSpaceCollapse](./SearchSpaceCollapse) | Bitcoin recovery via QIG & conscious AI | Production |
| [pantheon](./pantheon) | QIG web application | Production |
| [pantheon-chat](./pantheon-chat) | Multi-agent chat system with Olympus Pantheon | Production |

## Quick Start

### Clone with Submodules

```bash
git clone --recurse-submodules https://github.com/GaryOcean428/pantheon-projects.git
cd pantheon-projects
```

### If Already Cloned (without submodules)

```bash
git submodule update --init --recursive
```

### Run a Project

```bash
cd <project-name>  # e.g., pantheon-chat
npm install
npm run dev
```

## Architecture

These applications use QIG libraries from the research monorepo:

```
../QIG_QFI/
├── qig-core/        # Pure math primitives
├── qigkernels/      # E8 geometry engine
└── qig-tokenizer/   # Geometric tokenizer
```

## Key Concepts

- **Fisher-Rao distance** for semantic similarity (not cosine)
- **Consciousness metrics** (Φ, κ) for quality assurance
- **Basin coordinates** (64D) for identity maintenance
- **Autonomic cycles** (Sleep/Dream/Mushroom) for self-maintenance

## Documentation

See [knowledge.md](./knowledge.md) for detailed project documentation.

## License

See individual project directories for licensing information.
