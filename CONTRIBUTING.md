# Contributing to Photo Date Classifier

Thank you for your interest in contributing to Photo Date Classifier! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Development Environment Setup

1. **Fork and Clone**

```bash
git clone https://github.com/YOUR-USERNAME/photoclassification.git
cd photoclassification
```

2. **Create Virtual Environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Development Dependencies**

```bash
pip install -e ".[dev]"
```

4. **Install Pre-commit Hooks**

```bash
pre-commit install
```

## Development Workflow

### Before Making Changes

1. Create a new branch for your feature/fix:

```bash
git checkout -b feature/your-feature-name
```

2. Make sure tests pass:

```bash
pytest
```

### Making Changes

1. **Write Code**: Follow the coding standards below
2. **Add Tests**: Ensure new code has test coverage
3. **Update Documentation**: Update README.md, docstrings, etc.
4. **Run Tests**: Verify all tests pass
5. **Run Linters**: Ensure code quality checks pass

### Code Quality Checks

Run these before committing:

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/

# Security check
bandit -r src/

# Run tests with coverage
pytest --cov=photo_date_classifier --cov-report=term-missing
```

### Pre-commit Hooks

Pre-commit hooks automatically run on `git commit`:

- Black (code formatting)
- Ruff (linting)
- Mypy (type checking)
- Bandit (security)
- Trailing whitespace removal
- End-of-file fixer

If hooks fail, fix the issues and commit again.

## Coding Standards

### Python Style

- Follow PEP 8 style guide
- Use Black for formatting (line length: 100)
- Use type hints for all functions
- Write descriptive docstrings (Google style)

Example:

```python
def process_photo(photo: Photo, config: Config) -> ClassificationResult:
    """
    Process a single photo and classify it.
    
    Args:
        photo: Photo object with metadata
        config: Configuration for classification
        
    Returns:
        Classification result with destination path
        
    Raises:
        ValueError: If photo has no date information
    """
    # Implementation
    pass
```

### Testing Standards

- Write tests for all new functionality
- Aim for >90% code coverage
- Use descriptive test names: `test_function_name_scenario`
- Use pytest fixtures for common setup
- Mock external dependencies

Example:

```python
def test_extract_metadata_with_exif(tmp_path: Path) -> None:
    """Test metadata extraction from file with valid EXIF data."""
    # Arrange
    test_file = tmp_path / "test.dng"
    test_file.write_bytes(b"fake data")
    
    # Act
    result = extract_photo_metadata(test_file)
    
    # Assert
    assert result.date_taken is not None
    assert result.exif_source == "datetime_original"
```

### Documentation Standards

- Update README.md for user-facing changes
- Add docstrings to all public functions/classes
- Include type hints in docstrings
- Provide usage examples where applicable

## Testing

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=photo_date_classifier --cov-report=html

# Specific test file
pytest tests/test_exif_reader.py

# Specific test
pytest tests/test_exif_reader.py::test_extract_photo_metadata

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Test Organization

```
tests/
├── __init__.py
├── conftest.py          # Shared fixtures
├── test_models.py       # Model tests
├── test_exif_reader.py  # EXIF reader tests
├── test_organizer.py    # Organizer tests
├── test_hashing.py      # Hashing tests
└── test_cli.py          # CLI tests
```

## Security

### Security Considerations

- Never commit secrets or credentials
- Validate all user inputs
- Sanitize file paths to prevent traversal
- Use secure hash algorithms (SHA-256+)
- Avoid shell injection (use subprocess with list args)
- Keep dependencies updated

### Security Tools

Run security checks:

```bash
# Static analysis
bandit -r src/

# Dependency vulnerabilities
pip-audit

# Check for outdated dependencies
pip list --outdated
```

## Pull Request Process

1. **Update Documentation**: Ensure README and docstrings are current
2. **Add Tests**: Include tests for new functionality
3. **Pass All Checks**: Ensure CI passes
4. **Update CHANGELOG**: Add entry under "Unreleased"
5. **Write Clear Description**: Explain what and why
6. **Link Issues**: Reference related issues with `#issue-number`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Checklist
- [ ] Tests pass locally
- [ ] Added/updated tests
- [ ] Updated documentation
- [ ] Ran linters and formatters
- [ ] Updated CHANGELOG.md
```

## Commit Messages

Follow conventional commits format:

```
type(scope): brief description

Longer description if needed

Fixes #123
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```
feat(cli): add --json output option
fix(exif): handle missing datetime tags gracefully
docs(readme): add installation instructions
```

## Release Process

Maintainers follow this process for releases:

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md with release date
3. Create git tag: `git tag -a v0.1.0 -m "Release v0.1.0"`
4. Push tag: `git push origin v0.1.0`
5. Build and publish: `python -m build && twine upload dist/*`

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with bug report template
- **Features**: Open a GitHub Issue with feature request template
- **Security**: See [SECURITY.md](SECURITY.md) for reporting security issues

## Recognition

Contributors will be recognized in:
- CHANGELOG.md for each release
- GitHub contributors page
- Special thanks in README.md for major contributions

Thank you for contributing! 🎉
