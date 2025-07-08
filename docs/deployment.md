# Deploying Dev Sentinel from Git Repository

This guide covers various deployment methods for the Dev Sentinel package directly from the Git repository.

## Quick Deployment

### Direct Installation from Git

```bash
# Install latest from main branch
pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Install specific version/tag
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@v0.3.0

# Install from specific branch
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@feature/force-mcp-stdio-integration
```

### Development Installation

```bash
# Clone and install in editable mode
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel
pip install -e .

# Verify installation
dev-sentinel --version
force-mcp-stdio --help
```

## Deployment Methods

### 1. Production Deployment

#### Standard Installation
```bash
# Create virtual environment
python -m venv dev-sentinel-env
source dev-sentinel-env/bin/activate  # Linux/macOS
# or
dev-sentinel-env\Scripts\activate     # Windows

# Install from git
pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Verify CLI commands
dev-sentinel --version
force-mcp-stdio --validation-only
```

#### With Optional Dependencies
```bash
# Install with development tools
pip install "git+https://github.com/peguesj/yj-dev_sentinel.git[dev]"

# Install with documentation tools
pip install "git+https://github.com/peguesj/yj-dev_sentinel.git[docs]"

# Install with all optional dependencies
pip install "git+https://github.com/peguesj/yj-dev_sentinel.git[dev,docs]"
```

### 2. Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install git (required for pip install from git)
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Install Dev Sentinel
RUN pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Create non-root user
RUN useradd -m devsentinel
USER devsentinel

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FORCE_DEBUG=0

# Expose ports for HTTP servers
EXPOSE 8000 8080 8090

# Default command
CMD ["dev-sentinel", "--help"]
```

#### Build and Run
```bash
# Build Docker image
docker build -t dev-sentinel .

# Run Force MCP server
docker run -p 8080:8080 dev-sentinel force-mcp-http --port 8080 --host 0.0.0.0

# Run Dev Sentinel HTTP server
docker run -p 8000:8000 -p 8090:8090 dev-sentinel dev-sentinel-http
```

#### Docker Compose
```yaml
version: '3.8'
services:
  force-mcp:
    build: .
    command: force-mcp-http --port 8080 --host 0.0.0.0
    ports:
      - "8080:8080"
    environment:
      - PYTHONUNBUFFERED=1
      - FORCE_DEBUG=0
    volumes:
      - ./project:/workspace
    working_dir: /workspace

  dev-sentinel:
    build: .
    command: dev-sentinel-http --http-port 8000 --mcp-port 8090
    ports:
      - "8000:8000"
      - "8090:8090"
    environment:
      - PYTHONUNBUFFERED=1
    volumes:
      - ./project:/workspace
    working_dir: /workspace
```

### 3. Cloud Deployment

#### Heroku
```bash
# Create Heroku app
heroku create your-dev-sentinel-app

# Add Python buildpack
heroku buildpacks:set heroku/python

# Create requirements.txt
echo "git+https://github.com/peguesj/yj-dev_sentinel.git" > requirements.txt

# Create Procfile
echo "web: dev-sentinel-http --http-port \$PORT --host 0.0.0.0" > Procfile

# Deploy
git add requirements.txt Procfile
git commit -m "Add Heroku deployment files"
git push heroku main
```

#### AWS Lambda (Serverless)
```python
# lambda_function.py
import json
import asyncio
from dev_sentinel.servers.force_mcp_http import run_http_server

def lambda_handler(event, context):
    # Initialize and run Force MCP server
    # Note: This is a simplified example
    return {
        'statusCode': 200,
        'body': json.dumps('Dev Sentinel Lambda function')
    }
```

#### Google Cloud Run
```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/dev-sentinel', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/dev-sentinel']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'dev-sentinel'
      - '--image'
      - 'gcr.io/$PROJECT_ID/dev-sentinel'
      - '--region'
      - 'us-central1'
      - '--platform'
      - 'managed'
```

### 4. CI/CD Integration

#### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy Dev Sentinel

on:
  push:
    branches: [main]
    tags: ['v*']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
          
      - name: Install from Git
        run: |
          pip install git+https://github.com/peguesj/yj-dev_sentinel.git
          
      - name: Test installation
        run: |
          dev-sentinel --version
          force-mcp-stdio --validation-only
          
      - name: Deploy to production
        run: |
          # Your deployment commands here
          echo "Deploying Dev Sentinel..."
```

#### GitLab CI
```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test_installation:
  stage: test
  image: python:3.10
  script:
    - pip install git+https://github.com/peguesj/yj-dev_sentinel.git
    - dev-sentinel --version
    - force-mcp-stdio --validation-only

deploy_production:
  stage: deploy
  image: python:3.10
  script:
    - pip install git+https://github.com/peguesj/yj-dev_sentinel.git
    - # Your deployment commands
  only:
    - main
    - tags
```

## Environment-Specific Deployments

### Development Environment
```bash
# Clone for development
git clone https://github.com/peguesj/yj-dev_sentinel.git
cd yj-dev_sentinel

# Create development environment
python -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Initialize Force system
dev-sentinel init

# Start development server
force-mcp-stdio --debug
```

### Staging Environment
```bash
# Install specific branch for testing
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@staging

# Set staging environment variables
export FORCE_DEBUG=1
export ENVIRONMENT=staging

# Run validation
force-mcp-stdio --validation-only

# Start staging server
force-mcp-http --port 8080 --debug
```

### Production Environment
```bash
# Install stable version
pip install git+https://github.com/peguesj/yj-dev_sentinel.git@v0.3.0

# Set production environment
export PYTHONUNBUFFERED=1
export FORCE_DEBUG=0
export ENVIRONMENT=production

# Run production health check
dev-sentinel status

# Start production servers
force-mcp-http --port 8080 &
dev-sentinel-http --http-port 8000 --mcp-port 8090 &
```

## Configuration Management

### Environment Variables
```bash
# Core settings
export PYTHONUNBUFFERED=1
export FORCE_DEBUG=0
export ENVIRONMENT=production

# Force framework settings
export FORCE_CONFIG_PATH=/etc/dev-sentinel/force
export FORCE_AUTO_FIX=1

# MCP server settings
export MCP_STDIO_TIMEOUT=30000
export MCP_HTTP_PORT=8080

# Logging settings
export LOG_LEVEL=INFO
export LOG_DIR=/var/log/dev-sentinel
```

### Configuration Files
```bash
# Create configuration directory
sudo mkdir -p /etc/dev-sentinel

# Create main configuration
cat > /etc/dev-sentinel/config.yaml << EOF
force:
  debug: false
  auto_fix: true
  validation_strict: false

mcp:
  stdio_timeout: 30000
  http_port: 8080
  max_connections: 100

logging:
  level: INFO
  file: /var/log/dev-sentinel/app.log
EOF
```

## Deployment Verification

### Health Checks
```bash
# Check CLI installation
dev-sentinel --version

# Verify all commands available
which force-mcp-stdio
which dev-sentinel-stdio
which force-mcp-http
which dev-sentinel-http

# Test Force validation
force-mcp-stdio --validation-only

# Check system status
dev-sentinel status
```

### MCP Server Testing
```bash
# Test stdio server
echo '{"method": "initialize", "params": {}}' | force-mcp-stdio

# Test HTTP server (in background)
force-mcp-http --port 8080 &
curl http://localhost:8080/health

# Test with timeout
timeout 10s force-mcp-stdio --validation-only
```

### Integration Testing
```bash
# Test VS Code integration
cat > test-mcp.json << EOF
{
  "mcpServers": {
    "test": {
      "command": "force-mcp-stdio",
      "args": ["--validation-only"]
    }
  }
}
EOF

# Test configuration
force-mcp-stdio --validation-only
```

## Troubleshooting Deployment Issues

### Common Installation Problems

#### Git Access Issues
```bash
# If you get permission errors
git config --global credential.helper store
git clone https://github.com/peguesj/yj-dev_sentinel.git

# For private repositories
pip install git+https://username:token@github.com/peguesj/yj-dev_sentinel.git
```

#### Python Version Issues
```bash
# Check Python version
python --version

# Use specific Python version
pip3.10 install git+https://github.com/peguesj/yj-dev_sentinel.git

# With pyenv
pyenv local 3.10.0
pip install git+https://github.com/peguesj/yj-dev_sentinel.git
```

#### Permission Issues
```bash
# Install for user only
pip install --user git+https://github.com/peguesj/yj-dev_sentinel.git

# Fix PATH for user installs
export PATH=$PATH:~/.local/bin
```

### Runtime Issues

#### Command Not Found
```bash
# Check installation
pip list | grep dev-sentinel

# Check PATH
echo $PATH | grep -o '[^:]*bin'

# Reinstall if needed
pip uninstall dev-sentinel
pip install git+https://github.com/peguesj/yj-dev_sentinel.git
```

#### Import Errors
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test import
python -c "import dev_sentinel; print('OK')"

# Check dependencies
pip check
```

#### Force Validation Errors
```bash
# Check Force directory
ls -la .force/

# Initialize if missing
dev-sentinel init

# Debug validation
force-mcp-stdio --debug --validation-only
```

## Security Considerations

### Production Security
```bash
# Create dedicated user
sudo useradd -m -s /bin/bash devsentinel

# Install for service user
sudo -u devsentinel pip install git+https://github.com/peguesj/yj-dev_sentinel.git

# Set proper permissions
sudo chown -R devsentinel:devsentinel /opt/dev-sentinel
sudo chmod 750 /opt/dev-sentinel
```

### Network Security
```bash
# Firewall rules for HTTP servers
sudo ufw allow 8080/tcp  # Force MCP HTTP
sudo ufw allow 8000/tcp  # Dev Sentinel HTTP
sudo ufw allow 8090/tcp  # Dev Sentinel MCP

# Restrict to specific IPs
sudo ufw allow from 10.0.0.0/8 to any port 8080
```

### Environment Isolation
```bash
# Use containers for isolation
docker run --rm -it --network none dev-sentinel force-mcp-stdio --validation-only

# Use virtual environments
python -m venv /opt/dev-sentinel/venv
/opt/dev-sentinel/venv/bin/pip install git+https://github.com/peguesj/yj-dev_sentinel.git
```

## Monitoring and Maintenance

### Log Management
```bash
# Configure log rotation
sudo cat > /etc/logrotate.d/dev-sentinel << EOF
/var/log/dev-sentinel/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 devsentinel devsentinel
}
EOF
```

### Health Monitoring
```bash
# Create health check script
cat > /usr/local/bin/check-dev-sentinel << 'EOF'
#!/bin/bash
if ! dev-sentinel status > /dev/null 2>&1; then
    echo "Dev Sentinel health check failed"
    exit 1
fi
echo "Dev Sentinel is healthy"
EOF

chmod +x /usr/local/bin/check-dev-sentinel
```

### Automatic Updates
```bash
# Create update script
cat > /usr/local/bin/update-dev-sentinel << 'EOF'
#!/bin/bash
pip install --upgrade git+https://github.com/peguesj/yj-dev_sentinel.git
dev-sentinel status
EOF

chmod +x /usr/local/bin/update-dev-sentinel

# Schedule with cron
echo "0 2 * * 0 /usr/local/bin/update-dev-sentinel" | sudo crontab -
```

---

## Summary

This deployment guide covers:

- **Quick Installation**: Direct from Git with pip
- **Development Setup**: Editable installation for development
- **Production Deployment**: Docker, cloud platforms, CI/CD
- **Environment Management**: Configuration and variables
- **Troubleshooting**: Common issues and solutions
- **Security**: Best practices for production
- **Monitoring**: Health checks and maintenance

Choose the deployment method that best fits your environment and requirements. All methods provide access to the complete Dev Sentinel CLI suite including `force-mcp-stdio`, `dev-sentinel-stdio`, `force-mcp-http`, and `dev-sentinel-http` commands.
