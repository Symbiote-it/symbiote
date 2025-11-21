# Contributing to Symbiote

<div align="center">
  <img src="media/symbiote.svg" alt="Symbiote Logo" width="100"/>
  
  **Thank you for considering contributing to Symbiote!**
  
  This document provides guidelines and instructions for contributing to the project.
</div>

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of background, experience level, gender identity, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or offensive comments
- Trolling or insulting remarks
- Public or private harassment
- Publishing others' private information

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/symbiote.git
   cd symbiote
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/your-org/symbiote.git
   ```
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

## Development Setup

### Prerequisites

- Node.js 18+ or Python 3.9+
- Docker and Docker Compose
- Git
- Your preferred IDE (VS Code recommended)

### Initial Setup

```bash
# Install dependencies
npm install
# or
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development services
docker-compose up -d

# Run database migrations
npm run migrate
# or
python manage.py migrate

# Start development server
npm run dev
# or
python manage.py runserver
```

### Development Tools

- **Linting**: ESLint (JavaScript) or Black/Flake8 (Python)
- **Formatting**: Prettier (JavaScript) or Black (Python)
- **Testing**: Jest (JavaScript) or pytest (Python)
- **Type Checking**: TypeScript or mypy

## Contribution Workflow

### 1. Choose What to Work On

- Check [open issues](https://github.com/your-org/symbiote/issues) for tasks
- Look for issues labeled `good first issue` if you're new
- Comment on issues you want to work on to avoid duplicate work
- For large features, discuss in an issue first

### 2. Make Your Changes

- Write clean, maintainable code
- Follow the coding standards (see below)
- Add tests for new features
- Update documentation as needed
- Keep commits focused and atomic

### 3. Test Your Changes

```bash
# Run all tests
npm test
# or
pytest

# Run linters
npm run lint
# or
flake8 .

# Run type checking
npm run type-check
# or
mypy .
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples**:
```
feat(ai): add test generation model
fix(api): resolve authentication timeout issue
docs(readme): update installation instructions
```

### 5. Keep Your Branch Updated

```bash
# Fetch latest changes
git fetch upstream

# Rebase your branch on main
git checkout main
git pull upstream main
git checkout your-branch
git rebase main
```

## Feature Requests

When requesting features:

1. **Check Existing Issues**: Avoid duplicates
2. **Describe Use Case**: Why is this needed?
3. **Propose Solution**: How should it work?
4. **Consider Alternatives**: Other approaches?
5. **Be Patient**: Features take time to implement

## Getting Help

- **Documentation**: Check docs first
- **Discussions**: Use GitHub Discussions
- **Discord/Slack**: Join our community
- **Email**: support@symbiote.dev

## Recognition

Contributors will be:

- Listed in CONTRIBUTORS.md
- Credited in release notes
- Invited to contributor events
- Given early access to new features

## Questions?

If you have questions about contributing:

1. Check this document first
2. Search existing issues/discussions
3. Ask in GitHub Discussions
4. Contact maintainers

---

**Thank you for contributing to Symbiote!** 🎉

Every contribution, no matter how small, makes Symbiote better.

