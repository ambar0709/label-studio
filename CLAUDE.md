# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture Overview

Label Studio is a Django-based data labeling platform with a React frontend. The architecture consists of:

- **Backend**: Django REST API with PostgreSQL/SQLite database
- **Frontend**: React application built with Nx monorepo tools, using MobX for state management  
- **Key Components**:
  - `label_studio/` - Main Django application
  - `web/` - React frontend with Nx workspace containing multiple libs and apps
  - `label_studio/core/` - Core Django settings and utilities
  - `label_studio/projects/` - Project management
  - `label_studio/tasks/` - Task and annotation handling
  - `label_studio/data_manager/` - Data management and filtering
  - `label_studio/io_storages/` - Storage connectors (S3, GCS, Azure, Local)
  - `label_studio/ml/` - Machine learning backend integration

## Development Commands

### Backend Development
```bash
# Setup development environment
poetry install
make migrate-dev              # Run migrations with SQLite
make run-dev                 # Start Django dev server with SQLite
make shell-dev               # Django shell with SQLite

# Testing
make test                    # Run backend tests with pytest
cd label_studio && DJANGO_DB=sqlite pytest -v -m "not integration_tests"

# Database operations
make makemigrations-dev      # Create new migrations
make migrate-dev             # Apply migrations
```

### Frontend Development  
```bash
# Setup and development
cd web
yarn install --frozen-lockfile
yarn run dev                 # Hot module replacement dev server
yarn run watch              # Build continuously on file changes
yarn run build              # Production build

# Testing
yarn test:unit              # Run unit tests
yarn test:e2e               # Run end-to-end tests
yarn ls:e2e                 # Label Studio e2e tests
yarn lsf:e2e                # Label Studio Frontend e2e tests

# Specific component development
yarn ls:dev                 # Label Studio app dev server
yarn lsf:serve              # Editor standalone dev server
yarn dm:watch               # Data Manager continuous build
```

### Docker Development
```bash
make docker-dev-setup       # Setup docker development files
make docker-run-dev         # Run with docker-compose
make docker-migrate-dev     # Run migrations in docker
make build-testing-image    # Build testing image
make docker-testing-shell   # Interactive testing container
```

### Code Quality
```bash
make fmt                    # Format changed files
make fmt-all                # Format all files
make fmt-check              # Check for lint issues on branch
make configure-hooks        # Setup pre-commit hooks
```

## Key Architecture Details

### Django Apps Structure
- **Core**: Settings, middleware, basic utilities (`label_studio/core/`)
- **Projects**: Project CRUD, configuration, permissions (`label_studio/projects/`)
- **Tasks**: Task creation, annotation storage (`label_studio/tasks/`)
- **Users/Organizations**: Multi-tenant user management (`label_studio/users/`, `label_studio/organizations/`)
- **Data Export/Import**: Bulk operations (`label_studio/data_export/`, `label_studio/data_import/`)
- **ML Integration**: ML backend connections (`label_studio/ml/`)
- **Storage**: Cloud storage integrations (`label_studio/io_storages/`)

### Frontend Architecture (React/Nx)
- **Apps**: Main applications in `web/apps/`
  - `labelstudio/` - Main Label Studio app
  - `playground/` - Standalone playground
  - `labelstudio-e2e/` - E2E tests
- **Libraries**: Reusable components in `web/libs/`
  - `editor/` - Label Studio Frontend (LSF) annotation interface
  - `datamanager/` - Data Manager for task browsing/filtering
  - `core/` - Shared utilities and API clients
  - `app-common/` - Common UI components

### Key Configuration Files
- `pyproject.toml` - Python dependencies and build config
- `web/package.json` - Frontend dependencies and scripts
- `label_studio/core/settings/` - Django settings modules
- `web/nx.json` - Nx monorepo configuration
- `label_studio/feature_flags.json` - Feature flag definitions

## Development Workflow Patterns

### Adding New Django Features
1. Create models in appropriate app's `models.py`
2. Add API endpoints in `api.py` with DRF serializers
3. Add URL routing in `urls.py`
4. Create migrations with `make makemigrations-dev`
5. Add tests in `tests/` directory

### Frontend Development Patterns
- Use MobX stores for state management (found in stores/ directories)
- Components use React hooks and functional patterns
- API calls go through the core API client in `web/libs/core/`
- Use Nx generators for consistent code structure: `nx g @nx/react:component`

### Testing Patterns
- Backend: pytest with Django test client, factories in `tests/factories.py`
- Frontend: Jest for unit tests, Cypress for E2E tests
- Integration tests use Tavern (YAML-based API testing)

## Important Constraints and Patterns

### Database Considerations
- Default to SQLite for development, PostgreSQL for production
- Use Django ORM migrations, never raw SQL in migrations
- Batch size limits: `BATCH_SIZE = 1000`, `MAX_TASK_BATCH_SIZE = 1000`
- Task limits: `TASKS_MAX_NUMBER = 1,000,000` per project

### API Design Patterns
- Follow DRF conventions with ViewSets and serializers
- Use `drf-yasg` for OpenAPI documentation
- Pagination: `PAGE_SIZE = 100`
- File uploads limited to `DATA_UPLOAD_MAX_MEMORY_SIZE = 250MB`

### Frontend State Management
- MobX stores for complex state (projects, tasks, annotations)
- React Context for simple shared state
- API state managed through tanstack-query in newer components

### Security Considerations
- CSRF protection enabled by default
- Content Security Policy configured in `django-csp`
- File upload validation for SVG and other formats
- Authentication via Django sessions or JWT tokens

### Performance Considerations
- Redis used for caching and task queues (RQ)
- Large dataset handling through pagination and filtering
- Storage backends abstracted through Django-storages
- Frontend code splitting and lazy loading for performance

## Current Limitations to Address for Enterprise Use

The current codebase has several limitations for enterprise deployment:
- Single-tenant design with basic organization structure
- Limited RBAC (Role-Based Access Control)
- No comprehensive audit logging
- Basic authentication without enterprise SSO
- Limited scalability patterns for high-volume workloads
- No advanced workflow management or approval processes
- Basic monitoring and observability
- Limited multi-region deployment support

When developing enterprise features, consider these architectural patterns and ensure new code follows the existing conventions while addressing these limitations.