# Contributing Guide

## Development Setup

### 1. Clone and setup environment
```bash
git clone https://github.com/yourusername/my_llm_service.git
cd my_llm_service

python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Установить все dev зависимости
pip install -r requirements-dev.txt
```

### 2. Pre-commit Setup (Optional but Recommended)
```bash
# Установить pre-commit hooks
./venv/bin/pre-commit install

# или если вы установили pre-commit глобально:
pre-commit install
```

После установки, все коммиты будут автоматически проверяться перед сохранением.

## Code Quality Standards

### Linting
```bash
# Check code style
ruff check .

# Auto-fix issues
ruff check --fix .

# Format code
black .

# Type checking
mypy .
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. tests/

# Run specific test
pytest tests/test_api.py::TestSummarize::test_valid_request -v

# Run tests in parallel
pytest -n auto
```

### Pre-commit Checks
All commits must pass:
- ✅ Ruff linting
- ✅ Black formatting
- ✅ Pytest tests
- ✅ Type checking with mypy

## Commit Guidelines

- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Example: `feat: add new cache invalidation strategy`
- Keep commits atomic and focused

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/amazing-feature`
2. Make your changes
3. Run tests: `pytest`
4. Run linting: `ruff check . && black . && mypy .`
5. Commit with conventional message
6. Push to branch: `git push origin feature/amazing-feature`
7. Create Pull Request

## Code Style

- Line length: 100 characters
- Use type hints for all functions
- Follow PEP 8 conventions
- Add docstrings to classes and functions

Example:
```python
async def summarize(self, text: str, temperature: float) -> str:
    """Summarize the provided text.

    Args:
        text: Text to summarize (10-10000 characters)
        temperature: Creativity level (0.0-1.0)

    Returns:
        Summary text

    Raises:
        ValidationError: If text is invalid
        LLMAPIError: If LLM API call fails
    """
```

## Testing Requirements

- Write tests for new features
- Maintain >80% code coverage
- Test both success and failure paths
- Use descriptive test names

Example:
```python
@pytest.mark.asyncio
async def test_summarize_with_valid_text():
    """Test successful text summarization"""
    pipeline = SummarizationPipeline()
    request = SummarizeRequest(text="Sample text " * 50)

    response = await pipeline.execute(request)

    assert response.summary
    assert response.original_text_length > 0
    assert not response.from_cache
```

## Report Issues

- Use GitHub Issues
- Describe the problem clearly
- Include steps to reproduce
- Add relevant logs/screenshots

## Questions?

Open a discussion or contact the maintainers.
