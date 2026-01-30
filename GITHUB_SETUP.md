# GitHub Setup Guide

This guide provides step-by-step instructions for pushing the IoT Fleet Monitor project to GitHub.

## Prerequisites

- Git installed on your system
- GitHub account created
- SSH key configured (optional but recommended)

## Initial Setup

### 1. Initialize Git Repository

```bash
cd c:\Users\olade\iot-fleet-monitor
git init
```

### 2. Configure Git (First Time Only)

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Create GitHub Repository

1. Go to https://github.com
2. Click "New repository"
3. Repository name: `iot-fleet-monitor`
4. Description: "High-performance IoT device monitoring system with FastAPI"
5. Choose Public or Private
6. Do NOT initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 4. Add Files to Git

```bash
# Add all files
git add .

# Check what will be committed
git status

# Commit
git commit -m "Initial commit: IoT Fleet Monitor application"
```

### 5. Connect to GitHub

Replace `<your-username>` with your GitHub username:

```bash
git remote add origin https://github.com/<your-username>/iot-fleet-monitor.git
```

Or if using SSH:

```bash
git remote add origin git@github.com:<your-username>/iot-fleet-monitor.git
```

### 6. Push to GitHub

```bash
# Push to main branch
git branch -M main
git push -u origin main
```

## Project Structure (Ready for GitHub)

```
iot-fleet-monitor/
├── .github/workflows/        # CI/CD configuration
├── app/                      # Application source code
├── scripts/                  # Utility scripts
├── tests/                    # Test suite
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── DEPLOYMENT.md             # Deployment documentation
├── docker-compose.yml        # Docker configuration
├── Dockerfile                # Container definition
├── LICENSE                   # MIT License
├── Makefile                  # Build commands
├── pytest.ini                # Test configuration
├── README.md                 # Main documentation
├── requirements.txt          # Python dependencies
└── start.ps1                 # Windows startup script
```

## What Was Cleaned Up

### Removed Files
- QUICKSTART.md (redundant)
- PROJECT_SUMMARY.md (redundant)
- ARCHITECTURE.md (consolidated into README)

### Code Improvements
- Removed all emojis from Python code
- Standardized logging messages
- Professional console output formatting

### Documentation
- Created concise, professional README.md
- Structured deployment guide
- Standard project documentation

## Repository Features

### Included
- Comprehensive README with examples
- Deployment guide for Ubuntu/Linux
- Docker containerization
- CI/CD pipeline (GitHub Actions)
- Unit and integration tests
- Database seeding scripts
- Load testing utilities
- MIT License

### GitHub Actions Workflow
The repository includes automated CI/CD that:
- Runs on every push and pull request
- Executes pytest test suite
- Builds Docker image
- Performs linting checks

## Repository Settings

### Recommended Settings

1. **Branch Protection**:
   - Go to Settings > Branches
   - Add rule for `main` branch
   - Enable "Require pull request reviews"
   - Enable "Require status checks to pass"

2. **Topics** (for discoverability):
   - fastapi
   - iot
   - postgresql
   - docker
   - python
   - monitoring
   - sensor-data

3. **About Section**:
   - Description: "High-performance IoT device monitoring system"
   - Website: (your deployment URL if available)
   - Topics: Add relevant tags

## Common Git Commands

### Update Repository

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push
```

### Create Feature Branch

```bash
# Create and switch to new branch
git checkout -b feature/new-feature

# Make changes, commit
git add .
git commit -m "Add new feature"

# Push branch
git push -u origin feature/new-feature
```

### Pull Latest Changes

```bash
git pull origin main
```

## Troubleshooting

### Authentication Failed

If using HTTPS and authentication fails:
1. Generate Personal Access Token on GitHub
2. Use token as password when prompted

### Permission Denied (SSH)

If SSH fails:
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub: Settings > SSH Keys
```

### Large Files

If you encounter large file errors:
```bash
# Check file sizes
git ls-files -z | xargs -0 du -h | sort -h

# Consider Git LFS for large files
```

## Next Steps

After pushing to GitHub:

1. Add repository description and topics
2. Enable GitHub Actions (should work automatically)
3. Configure branch protection rules
4. Add collaborators if needed
5. Create issues for planned features
6. Add badges to README (optional)

## Badges (Optional)

Add these to the top of README.md:

```markdown
![Build Status](https://github.com/<username>/iot-fleet-monitor/workflows/CI/badge.svg)
![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

## Support

For Git-related issues:
- Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com

For project-specific questions:
- Open an issue on GitHub
- Check README.md and DEPLOYMENT.md
