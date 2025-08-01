# Contributing to Advanced Streaming Panel

We welcome contributions to the Advanced Streaming Panel project! This document provides guidelines for contributing to this open source project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [Making Changes](#making-changes)
5. [Testing](#testing)
6. [Submitting Changes](#submitting-changes)
7. [Style Guidelines](#style-guidelines)
8. [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct to ensure a welcoming environment for all contributors. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11+
- Node.js 18+
- FFmpeg
- PostgreSQL
- Git
- Basic understanding of video streaming concepts

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/streaming-panel.git
   cd streaming-panel
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/expertdevux/streaming-panel.git
   ```

## Development Setup

### Automatic Setup

Use our development setup script:

```bash
./scripts/dev-setup.sh
```

### Manual Setup

1. **Create virtual environment:**
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   npm install
   ```

3. **Setup database:**
   ```bash
   createdb streaming_panel_dev
   export DATABASE_URL="postgresql://localhost/streaming_panel_dev"
   python manage.py db upgrade
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Start development server:**
   ```bash
   python manage.py runserver
   ```

### Development Tools

We use several tools to maintain code quality:

- **Black**: Python code formatting
- **Flake8**: Python linting
- **mypy**: Type checking
- **Prettier**: JavaScript formatting
- **ESLint**: JavaScript linting
- **pytest**: Python testing
- **Jest**: JavaScript testing

Install pre-commit hooks:
```bash
pre-commit install
```

## Making Changes

### Branch Naming

Use descriptive branch names:

- `feature/live-preview-enhancement`
- `fix/rtmp-connection-timeout`
- `docs/api-documentation-update`
- `refactor/stream-manager-cleanup`

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(streaming): add live video preview functionality

Implement HLS.js integration for real-time stream previews
in the dashboard interface with automatic quality switching.

Closes #123
```

```
fix(rtmp): resolve connection timeout issues

- Increase connection timeout to 30 seconds
- Add retry mechanism for failed connections
- Improve error logging for debugging

Fixes #456
```

### Areas for Contribution

We welcome contributions in these areas:

#### 🎥 **Streaming Technology**
- Video encoding optimizations
- New streaming protocols (WebRTC, SRT)
- Hardware acceleration support
- Codec improvements

#### 🌐 **Platform Integrations**
- New streaming platforms
- Social media integrations
- LMS (Learning Management System) connectors
- Video conferencing platforms

#### 📊 **Analytics and Monitoring**
- Real-time analytics
- Performance metrics
- Viewer engagement tracking
- Quality of service monitoring

#### 🎨 **User Interface**
- Dashboard improvements
- Mobile responsiveness
- Accessibility features
- Theme customization

#### 🔧 **DevOps and Infrastructure**
- Docker improvements
- Kubernetes deployments
- CI/CD enhancements
- Monitoring and logging

#### 📚 **Documentation**
- Tutorial improvements
- API documentation
- Installation guides
- Best practices

## Testing

### Running Tests

```bash
# Python tests
pytest

# JavaScript tests
npm test

# Integration tests
pytest tests/integration/

# E2E tests
npm run test:e2e
```

### Test Coverage

Maintain test coverage above 80%:

```bash
# Check Python coverage
pytest --cov=. --cov-report=html

# Check JavaScript coverage
npm run test:coverage
```

### Test Categories

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete user workflows
4. **Performance Tests**: Test streaming performance
5. **Security Tests**: Test security vulnerabilities

### Writing Tests

#### Python Test Example

```python
import pytest
from app import create_app, db
from models import Stream

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

def test_create_stream(app):
    with app.app_context():
        stream = Stream(
            name='Test Stream',
            input_url='rtmp://localhost:1935/live/test',
            latency_mode='tutorial'
        )
        db.session.add(stream)
        db.session.commit()
        
        assert stream.id is not None
        assert stream.name == 'Test Stream'
        assert stream.latency_mode == 'tutorial'
```

#### JavaScript Test Example

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import StreamCard from '../components/StreamCard';

describe('StreamCard', () => {
  const mockStream = {
    id: 1,
    name: 'Test Stream',
    status: 'running',
    viewers: 25
  };

  test('renders stream information', () => {
    render(<StreamCard stream={mockStream} />);
    
    expect(screen.getByText('Test Stream')).toBeInTheDocument();
    expect(screen.getByText('25 viewers')).toBeInTheDocument();
  });

  test('handles start/stop actions', () => {
    const onAction = jest.fn();
    render(<StreamCard stream={mockStream} onAction={onAction} />);
    
    fireEvent.click(screen.getByRole('button', { name: /stop/i }));
    expect(onAction).toHaveBeenCalledWith('stop', 1);
  });
});
```

## Submitting Changes

### Pull Request Process

1. **Update your fork:**
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes:**
   - Follow coding standards
   - Add tests for new functionality
   - Update documentation
   - Ensure all tests pass

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push to your fork:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request:**
   - Use the PR template
   - Provide clear description
   - Link related issues
   - Add screenshots for UI changes

### Pull Request Template

```markdown
## Description

Brief description of changes made.

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing

- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance testing (if applicable)

## Screenshots

(Add screenshots for UI changes)

## Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is commented (complex areas)
- [ ] Documentation updated
- [ ] No new warnings introduced
- [ ] Tests added for new functionality

## Related Issues

Closes #123
Related to #456
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs automatically
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Manual testing of functionality
4. **Documentation**: Review of documentation changes
5. **Approval**: Two approvals required for merge

## Style Guidelines

### Python Style

Follow PEP 8 with these additions:

```python
# Use type hints
def create_stream(name: str, url: str) -> Optional[Stream]:
    pass

# Use docstrings
def start_stream(stream_id: int) -> bool:
    """Start a stream with the given ID.
    
    Args:
        stream_id: The ID of the stream to start
        
    Returns:
        True if stream started successfully, False otherwise
        
    Raises:
        StreamNotFoundError: If stream doesn't exist
    """
    pass

# Use meaningful variable names
max_bitrate = 5000  # Not: mb = 5000
stream_config = {}  # Not: cfg = {}
```

### JavaScript Style

Follow Airbnb style guide:

```javascript
// Use const/let, not var
const streamId = 1;
let isRunning = false;

// Use arrow functions
const handleStreamStart = (id) => {
  // Implementation
};

// Use async/await
const startStream = async (streamId) => {
  try {
    const response = await fetch(`/api/streams/${streamId}/start`);
    return response.json();
  } catch (error) {
    console.error('Failed to start stream:', error);
  }
};

// Use destructuring
const { name, status, viewers } = stream;
```

### CSS/SCSS Style

```css
/* Use BEM methodology */
.stream-card {
  display: flex;
  flex-direction: column;
}

.stream-card__header {
  padding: 1rem;
  background: var(--primary-color);
}

.stream-card__title--featured {
  font-weight: bold;
  color: var(--accent-color);
}

/* Use CSS custom properties */
:root {
  --primary-color: #007bff;
  --secondary-color: #6c757d;
  --success-color: #28a745;
}
```

### Database Migrations

```python
"""Add live preview support

Revision ID: abc123
Revises: def456
Create Date: 2025-01-01 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('streams', 
        sa.Column('preview_enabled', sa.Boolean(), default=True))
    
def downgrade():
    # Remove columns
    op.drop_column('streams', 'preview_enabled')
```

## Community

### Communication Channels

- **GitHub Discussions**: General questions and feature requests
- **GitHub Issues**: Bug reports and specific feature requests
- **Discord Server**: Real-time chat and community support
- **Mailing List**: Development announcements

### Getting Help

1. **Check Documentation**: Read existing docs first
2. **Search Issues**: Look for existing solutions
3. **Ask Questions**: Use GitHub Discussions
4. **Join Discord**: Real-time help from community

### Contributor Recognition

We recognize contributors through:

- **Contributors page** on our website
- **Changelog** entries for significant contributions
- **Social media** shoutouts for major features
- **Swag and stickers** for regular contributors

### Maintainer Responsibilities

Maintainers are responsible for:

- Reviewing and merging pull requests
- Triaging and labeling issues
- Maintaining project roadmap
- Ensuring code quality standards
- Supporting community members

## Development Workflow

### Feature Development

1. **Discuss the feature**: Open an issue to discuss
2. **Design review**: For large features, create design document
3. **Implementation**: Create PR with feature implementation
4. **Code review**: Address feedback from maintainers
5. **Testing**: Ensure comprehensive test coverage
6. **Documentation**: Update relevant documentation
7. **Release**: Feature included in next release

### Bug Fix Workflow

1. **Reproduce the bug**: Create test case that demonstrates issue
2. **Fix implementation**: Implement minimal fix
3. **Regression test**: Add test to prevent future occurrences
4. **Documentation**: Update docs if behavior changed

### Release Process

1. **Version planning**: Plan features for next version
2. **Feature freeze**: Stop adding new features
3. **Testing period**: Intensive testing of release candidate
4. **Release notes**: Document all changes
5. **Release**: Tag and publish new version

## Performance Guidelines

### Backend Performance

- Use database indexes for frequently queried fields
- Implement connection pooling for database connections
- Cache frequently accessed data with Redis
- Profile code to identify bottlenecks
- Use async/await for I/O operations

### Frontend Performance

- Minimize bundle size with code splitting
- Optimize images and video assets
- Use lazy loading for components
- Implement virtual scrolling for large lists
- Minimize re-renders with React.memo

### Streaming Performance

- Use hardware acceleration when available
- Optimize encoding settings for target bitrates
- Implement adaptive bitrate streaming
- Monitor and alert on performance metrics
- Use CDN for global content distribution

## Security Guidelines

### General Security

- Never commit secrets or credentials
- Use environment variables for configuration
- Implement proper input validation
- Follow OWASP security guidelines
- Regular security audits

### Authentication & Authorization

- Use strong password requirements
- Implement rate limiting
- Use JWT tokens with expiration
- Implement role-based access control
- Log security events

### Data Protection

- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper session management
- Regular security updates
- Data backup and recovery procedures

## Thank You

Thank you for contributing to the Advanced Streaming Panel! Your contributions help make this project better for everyone in the streaming community.

---

*Copyright © 2025 Expert Dev UX. All rights reserved.*