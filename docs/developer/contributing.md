# Contributing to Dev Sentinel

Thank you for your interest in contributing to Dev Sentinel! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct:

- Be respectful and inclusive
- Focus on constructive feedback
- Assume good intentions
- Follow the technical guidelines

## Getting Started

1. **Fork the repository**
2. **Clone your fork**

   ```bash
   git clone https://github.com/YOUR-USERNAME/yj-dev_sentinel.git
   cd yj-dev_sentinel
   ```
3. **Set up your development environment** (see [Development Setup](development-setup.md))
4. **Create a branch for your changes**

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow [PEP 8](https://pep8.org/) guidelines for Python code
- Use [Black](https://github.com/psf/black) for code formatting
- Use type annotations for all function parameters and return values
- Include docstrings for all classes, methods, and functions

### Documentation

- Update documentation when adding or modifying functionality
- Use markdown for documentation files
- Follow the documentation structure defined in the project
- Include examples where appropriate

### Testing

- Write tests for all new functionality
- Ensure all tests pass before submitting a pull request
- Maintain or improve code coverage

## Submitting Changes

1. **Commit your changes**

   ```bash
   git add .
   git commit -m "feat: add new feature"
   ```
   Use [Conventional Commits](https://www.conventionalcommits.org/) format for commit messages:
   - `feat:` for new features
   - `fix:` for bug fixes
   - `docs:` for documentation changes
   - `test:` for tests
   - `refactor:` for refactoring
   - `chore:` for maintenance tasks

2. **Push your changes to your fork**

   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a pull request** from your branch to the main repository

4. **Address any feedback** from the code review

## Review Process

1. All pull requests will be reviewed by at least one maintainer
2. Automated checks must pass (tests, linting, type checking)
3. Changes may be requested before merging
4. Once approved, a maintainer will merge your pull request

## Project Structure

```bash
dev_sentinel/
├── agents/           # Agent implementations
├── core/             # Core system components
├── force/            # FORCE framework
├── integration/      # External integrations
├── tests/            # Test suite
└── docs/             # Documentation
```

## Contact

If you have questions or need help, you can:

- Open an issue in the GitHub repository
- Contact the maintainers directly
- Join our community chat

Thank you for contributing to Dev Sentinel!
