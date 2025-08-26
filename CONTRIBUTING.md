# Contributing to OpenEducation

Thank you for your interest in contributing to OpenEducation! This document provides guidelines for contributing to this comprehensive educational services platform.

## Educational Mission

OpenEducation is designed to provide complete educational service delivery with:
- Standards-compliant instruction (WIDA, ACTFL)
- Research-based pedagogical practices
- Technology integration for enhanced learning
- Inclusive design for diverse student populations
- Professional development support

## Development Workflow

### 1. Getting Started
```bash
# Clone the repository
git clone https://github.com/llamasearchai/OpenEducation.git
cd OpenEducation

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Development Process
1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow Code Standards**
   - Use type hints for all function parameters and return values
   - Follow PEP 8 style guidelines
   - Write comprehensive docstrings
   - Ensure all code is production-ready (no placeholders, no stubs)

3. **Write Tests**
   - Create comprehensive unit tests for new functionality
   - Ensure all tests pass before submitting
   - Maintain test coverage above 80%

4. **Update Documentation**
   - Update README.md for new features
   - Update API documentation for new endpoints
   - Ensure examples work correctly

### 3. Testing Requirements
```bash
# Run all tests
pytest -v

# Run specific module tests
pytest tests/test_eld.py -v
pytest tests/test_world_languages.py -v

# Run with coverage
pytest --cov=openeducation --cov-report=html

# Run linting
flake8 openeducation/
mypy openeducation/
```

### 4. Educational Standards Compliance

When contributing educational modules, ensure:

#### ELD (English Language Development) Standards
- **WIDA Framework Compliance**: All ELD features must align with WIDA standards
- **Can-Do Descriptors**: Include appropriate proficiency descriptors
- **Research-Based Strategies**: All instructional methods must be evidence-based
- **Multi-Domain Assessment**: Cover Social/Interpersonal, Instructional, Academic Language

#### World Languages Standards
- **ACTFL Proficiency Guidelines**: Novice Low to Distinguished levels
- **Communication Modes**: Interpersonal, Interpretive, Presentational
- **Cultural Integration**: Authentic cultural content and perspectives
- **Standards Alignment**: Full compliance with state and national standards

### 5. Code Standards

#### Python Best Practices
- **Type Hints**: All functions must have complete type annotations
- **Docstrings**: Comprehensive documentation for all modules, classes, and functions
- **Error Handling**: Proper exception handling and user-friendly error messages
- **Security**: No hardcoded secrets, proper input validation

#### Educational Module Requirements
- **No Placeholders**: All functionality must be fully implemented
- **No Emojis**: Professional documentation without decorative elements
- **Production Ready**: All code must be suitable for educational deployment
- **Inclusive Design**: Support for diverse learning needs and backgrounds

### 6. Documentation Standards

#### README Updates
- Update module descriptions in README.md
- Add CLI examples for new commands
- Document API endpoints and parameters
- Include educational standards compliance information

#### Code Documentation
```python
def example_function(param1: str, param2: int) -> Dict[str, Any]:
    """
    Comprehensive function description.

    Args:
        param1 (str): Description of first parameter
        param2 (int): Description of second parameter

    Returns:
        Dict[str, Any]: Description of return value

    Raises:
        ValueError: Description of when this exception is raised

    Examples:
        >>> example_function("test", 42)
        {'result': 'success'}
    """
```

### 7. Pull Request Process

1. **Create Pull Request**
   - Use descriptive title following conventional commits
   - Reference any related issues
   - Provide comprehensive description

2. **Pull Request Template**
   ```
   ## Description
   [Brief description of changes]

   ## Educational Standards Compliance
   [How does this meet WIDA/ACTFL standards?]

   ## Testing
   [What tests were added/modified?]

   ## Documentation
   [What documentation was updated?]

   ## Breaking Changes
   [Any breaking changes?]
   ```

3. **Review Process**
   - At least one maintainer review required
   - All tests must pass
   - Code standards compliance verified
   - Educational standards alignment confirmed

### 8. Commit Message Guidelines

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat: Add Japanese middle school curriculum with WIDA alignment

- Complete Japanese language curriculum for grades 6-8
- WIDA standards compliance for ELD integration
- Cultural activities and assessment tools
- Comprehensive lesson plans and resources

Closes #123
```

### 9. Security Considerations

- Never commit API keys, passwords, or sensitive data
- Use environment variables for configuration
- Validate all user inputs
- Follow secure coding practices
- Run security checks before committing

### 10. Educational Research Integration

When adding educational features:
- **Cite Research**: Reference peer-reviewed studies supporting methods
- **Evidence-Based**: Ensure all strategies have research backing
- **Standards Alignment**: Verify compliance with educational standards
- **Diverse Learners**: Consider needs of all student populations
- **Professional Development**: Include resources for educator training

## Support

For questions or support:
- Create an issue on GitHub
- Follow the issue template for bug reports or feature requests
- Check existing documentation before creating new issues

## License

By contributing to OpenEducation, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- Repository contributors list
- Release notes for significant contributions
- Author credits in relevant modules

Thank you for contributing to OpenEducation and helping advance educational service delivery through technology and research-based practices!
