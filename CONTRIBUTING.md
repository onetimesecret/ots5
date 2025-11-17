# Contributing to OneTimeSecret

Thank you for your interest in contributing to OneTimeSecret! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/onetimesecret/ots5/issues)
2. If not, create a new issue with:
   - Clear, descriptive title
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Features

1. Check existing issues and discussions
2. Create a new issue with the `enhancement` label
3. Clearly describe:
   - The problem you're trying to solve
   - Your proposed solution
   - Alternative approaches considered
   - Impact on existing functionality

### Pull Requests

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR-USERNAME/ots5.git
   cd ots5
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

3. **Set Up Development Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate
   make dev-install
   ```

4. **Make Your Changes**
   - Follow the code style (PEP 8, Black formatting)
   - Add type hints to all functions
   - Write docstrings for public APIs
   - Update tests as needed
   - Update documentation if needed

5. **Test Your Changes**
   ```bash
   # Run tests
   make test

   # Check code style
   make lint

   # Type checking
   make type-check

   # Security scanning
   make security
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "feat: add amazing feature"
   ```

   Use conventional commit messages:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `test:` - Test updates
   - `refactor:` - Code refactoring
   - `perf:` - Performance improvements
   - `chore:` - Build/tooling changes

7. **Push and Create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then create a Pull Request on GitHub.

## Development Guidelines

### Code Style

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Add type hints to all functions
- Write docstrings for public APIs

### Testing

- Write tests for all new features
- Maintain test coverage above 90%
- Use pytest for testing
- Follow AAA pattern (Arrange, Act, Assert)

Example:
```python
def test_encrypt_decrypt():
    # Arrange
    encryption = SecretEncryption("test-key-32-chars-minimum")
    plaintext = "secret message"

    # Act
    ciphertext, salt = encryption.encrypt(plaintext)
    decrypted = encryption.decrypt(ciphertext, salt)

    # Assert
    assert decrypted == plaintext
```

### Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Follow OWASP security best practices
- Run security scans before committing
- Report security issues privately

### Documentation

- Update README.md for user-facing changes
- Add docstrings for all public functions/classes
- Update API documentation if endpoints change
- Include code examples in docstrings

Example:
```python
def encrypt(self, plaintext: str) -> Tuple[str, str]:
    """
    Encrypt plaintext data.

    Args:
        plaintext: Data to encrypt

    Returns:
        Tuple of (ciphertext, salt) both base64-encoded

    Raises:
        EncryptionError: If encryption fails

    Example:
        >>> encryption = SecretEncryption("my-secret-key")
        >>> ciphertext, salt = encryption.encrypt("secret")
        >>> len(ciphertext) > 0
        True
    """
```

## Project Structure

```
onetimesecret/
├── src/onetimesecret/
│   ├── api/           # FastAPI routes and endpoints
│   ├── core/          # Business logic and schemas
│   ├── crypto/        # Cryptographic operations
│   ├── db/            # Database models
│   ├── services/      # External services
│   └── utils/         # Utilities
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # Integration tests
│   └── fixtures/      # Test fixtures
└── docs/              # Documentation
```

## Review Process

1. Automated checks run on all PRs:
   - Tests must pass
   - Code coverage must be maintained
   - Linting must pass
   - Type checking must pass
   - Security scans must pass

2. Code review by maintainers
3. Address review feedback
4. Merge once approved

## Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Report bugs or suggest features
- **Email**: support@onetimesecret.com

## Recognition

Contributors will be:
- Listed in release notes
- Mentioned in the README (for significant contributions)
- Added to the contributors list

Thank you for contributing to OneTimeSecret!
