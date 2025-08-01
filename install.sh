#!/bin/bash

# Advanced Streaming Panel - Automatic Installation Script
# Copyright © 2025 Expert Dev UX

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.11"
NODE_VERSION="20"
POSTGRES_VERSION="14"

print_header() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "  Advanced Streaming Panel - Auto Installation"
    echo "  Copyright © 2025 Expert Dev UX"
    echo "=================================================="
    echo -e "${NC}"
}

print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_os() {
    print_step "Detecting operating system..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/debian_version ]; then
            OS="debian"
            DISTRO=$(lsb_release -si 2>/dev/null || echo "Debian")
        elif [ -f /etc/redhat-release ]; then
            OS="redhat"
            DISTRO=$(cat /etc/redhat-release | cut -d' ' -f1)
        else
            OS="linux"
            DISTRO="Generic Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        DISTRO="macOS"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
    
    print_info "Detected: $DISTRO"
}

check_requirements() {
    print_step "Checking system requirements..."
    
    # Check available memory
    if [[ "$OS" == "linux" || "$OS" == "debian" || "$OS" == "redhat" ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
        if [ "$MEMORY_GB" -lt 2 ]; then
            print_warning "Low memory detected. Recommended: 4GB+ for optimal performance"
        fi
    fi
    
    # Check disk space
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$DISK_SPACE" -lt 10 ]; then
        print_warning "Low disk space. Recommended: 20GB+ for media storage"
    fi
    
    print_info "System requirements check completed"
}

install_system_dependencies() {
    print_step "Installing system dependencies..."
    
    case "$OS" in
        "debian")
            sudo apt-get update
            sudo apt-get install -y \
                curl \
                wget \
                git \
                build-essential \
                software-properties-common \
                apt-transport-https \
                ca-certificates \
                gnupg \
                lsb-release \
                ffmpeg \
                nginx \
                supervisor \
                postgresql-$POSTGRES_VERSION \
                postgresql-contrib \
                postgresql-server-dev-$POSTGRES_VERSION \
                redis-server \
                certbot \
                python3-certbot-nginx
            ;;
        "redhat")
            sudo yum update -y
            sudo yum install -y \
                curl \
                wget \
                git \
                gcc \
                gcc-c++ \
                make \
                epel-release
            sudo yum install -y \
                ffmpeg \
                nginx \
                supervisor \
                postgresql$POSTGRES_VERSION-server \
                postgresql$POSTGRES_VERSION-contrib \
                postgresql$POSTGRES_VERSION-devel \
                redis \
                certbot \
                python3-certbot-nginx
            ;;
        "macos")
            # Check if Homebrew is installed
            if ! command -v brew &> /dev/null; then
                print_info "Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            brew update
            brew install \
                git \
                ffmpeg \
                nginx \
                postgresql@$POSTGRES_VERSION \
                redis \
                supervisor \
                certbot
            ;;
    esac
    
    print_info "System dependencies installed successfully"
}

install_python() {
    print_step "Installing Python $PYTHON_VERSION..."
    
    if command -v python$PYTHON_VERSION &> /dev/null; then
        print_info "Python $PYTHON_VERSION already installed"
        return
    fi
    
    case "$OS" in
        "debian")
            sudo add-apt-repository ppa:deadsnakes/ppa -y
            sudo apt-get update
            sudo apt-get install -y \
                python$PYTHON_VERSION \
                python$PYTHON_VERSION-venv \
                python$PYTHON_VERSION-dev \
                python3-pip
            ;;
        "redhat")
            sudo yum install -y python$PYTHON_VERSION python$PYTHON_VERSION-devel python3-pip
            ;;
        "macos")
            brew install python@$PYTHON_VERSION
            ;;
    esac
    
    # Create symbolic link if needed
    if ! command -v python3 &> /dev/null; then
        sudo ln -sf /usr/bin/python$PYTHON_VERSION /usr/bin/python3
    fi
    
    print_info "Python $PYTHON_VERSION installed successfully"
}

install_nodejs() {
    print_step "Installing Node.js $NODE_VERSION..."
    
    if command -v node &> /dev/null; then
        NODE_CURRENT=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        if [ "$NODE_CURRENT" -ge "$NODE_VERSION" ]; then
            print_info "Node.js $NODE_VERSION+ already installed"
            return
        fi
    fi
    
    # Install using NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | sudo -E bash -
    
    case "$OS" in
        "debian")
            sudo apt-get install -y nodejs
            ;;
        "redhat")
            sudo yum install -y nodejs npm
            ;;
        "macos")
            brew install node@$NODE_VERSION
            ;;
    esac
    
    print_info "Node.js $NODE_VERSION installed successfully"
}

setup_database() {
    print_step "Setting up PostgreSQL database..."
    
    # Initialize PostgreSQL if needed
    case "$OS" in
        "redhat")
            sudo postgresql-setup --initdb
            ;;
    esac
    
    # Start PostgreSQL service
    case "$OS" in
        "debian")
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        "redhat")
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
            ;;
        "macos")
            brew services start postgresql@$POSTGRES_VERSION
            ;;
    esac
    
    # Create database and user
    sudo -u postgres createuser --interactive --pwprompt streamuser || true
    sudo -u postgres createdb streamdb --owner=streamuser || true
    
    print_info "PostgreSQL database setup completed"
}

create_project_structure() {
    print_step "Creating project structure..."
    
    # Create directories
    mkdir -p /opt/streaming-panel
    mkdir -p /opt/streaming-panel/logs
    mkdir -p /opt/streaming-panel/static/streams/hls
    mkdir -p /opt/streaming-panel/static/streams/dash
    mkdir -p /opt/streaming-panel/static/recordings
    mkdir -p /etc/streaming-panel
    
    # Set permissions
    sudo chown -R $USER:$USER /opt/streaming-panel
    sudo chmod -R 755 /opt/streaming-panel
    
    print_info "Project structure created"
}

install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    cd /opt/streaming-panel
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    cat > requirements.txt << EOF
flask==3.0.0
flask-sqlalchemy==3.1.1
gunicorn==21.2.0
psycopg2-binary==2.9.9
redis==5.0.1
celery==5.3.4
sqlalchemy==2.0.23
werkzeug==3.0.1
email-validator==2.1.0
python-dotenv==1.0.0
Pillow==10.1.0
requests==2.31.0
pyjwt==2.8.0
bcrypt==4.1.2
ffmpeg-python==0.2.0
websockets==12.0
aiofiles==23.2.1
fastapi==0.104.1
uvicorn==0.24.0
EOF
    
    pip install -r requirements.txt
    
    deactivate
    
    print_info "Python dependencies installed successfully"
}

setup_nginx() {
    print_step "Configuring Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/streaming-panel << EOF > /dev/null
server {
    listen 80;
    server_name _;
    
    client_max_body_size 100M;
    
    # Static files
    location /static/ {
        alias /opt/streaming-panel/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # HLS streams
    location /hls/ {
        alias /opt/streaming-panel/static/streams/hls/;
        add_header Cache-Control no-cache;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization";
    }
    
    # DASH streams
    location /dash/ {
        alias /opt/streaming-panel/static/streams/dash/;
        add_header Cache-Control no-cache;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, OPTIONS";
        add_header Access-Control-Allow-Headers "Origin, Content-Type, Accept, Authorization";
    }
    
    # RTMP stats
    location /rtmp-stats {
        rtmp_stat all;
        rtmp_stat_stylesheet stat.xsl;
        add_header Access-Control-Allow-Origin *;
    }
    
    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/streaming-panel /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_info "Nginx configured successfully"
}

setup_rtmp_module() {
    print_step "Setting up RTMP module for Nginx..."
    
    # Install nginx-rtmp-module
    case "$OS" in
        "debian")
            sudo apt-get install -y libnginx-mod-rtmp
            ;;
        "redhat")
            # Build from source for RHEL/CentOS
            cd /tmp
            wget https://github.com/arut/nginx-rtmp-module/archive/master.zip
            unzip master.zip
            # Note: This requires rebuilding nginx with the module
            print_warning "RTMP module requires manual nginx compilation on RHEL/CentOS"
            ;;
        "macos")
            brew install nginx-full --with-rtmp-module
            ;;
    esac
    
    # Add RTMP configuration to nginx.conf
    sudo tee -a /etc/nginx/nginx.conf << EOF > /dev/null

# RTMP Configuration
rtmp {
    server {
        listen 1935;
        chunk_size 4096;
        
        application live {
            live on;
            record off;
            
            # HLS
            hls on;
            hls_path /opt/streaming-panel/static/streams/hls;
            hls_fragment 3s;
            hls_playlist_length 60s;
            
            # DASH
            dash on;
            dash_path /opt/streaming-panel/static/streams/dash;
            dash_fragment 3s;
            dash_playlist_length 60s;
            
            # Authentication
            on_publish http://127.0.0.1:5000/rtmp/auth;
            on_publish_done http://127.0.0.1:5000/rtmp/done;
        }
    }
}
EOF
    
    print_info "RTMP module configured"
}

setup_supervisor() {
    print_step "Setting up Supervisor for process management..."
    
    # Create Supervisor configuration
    sudo tee /etc/supervisor/conf.d/streaming-panel.conf << EOF > /dev/null
[program:streaming-panel]
command=/opt/streaming-panel/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 main:app
directory=/opt/streaming-panel
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/streaming-panel/logs/app.log
environment=PATH="/opt/streaming-panel/venv/bin"

[program:celery-worker]
command=/opt/streaming-panel/venv/bin/celery -A app.celery worker --loglevel=info
directory=/opt/streaming-panel
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/streaming-panel/logs/celery.log
environment=PATH="/opt/streaming-panel/venv/bin"

[program:redis-server]
command=redis-server
autostart=true
autorestart=true
user=redis
redirect_stderr=true
stdout_logfile=/var/log/redis/redis-server.log
EOF
    
    # Reload Supervisor
    sudo supervisorctl reread
    sudo supervisorctl update
    
    print_info "Supervisor configured successfully"
}

create_environment_file() {
    print_step "Creating environment configuration..."
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Create .env file
    cat > /opt/streaming-panel/.env << EOF
# Database Configuration
DATABASE_URL=postgresql://streamuser:password@localhost/streamdb

# Security
SESSION_SECRET=$SECRET_KEY
JWT_SECRET_KEY=$SECRET_KEY

# Redis Configuration
REDIS_URL=redis://localhost:6379

# FFmpeg Configuration
FFMPEG_PATH=/usr/bin/ffmpeg
FFPROBE_PATH=/usr/bin/ffprobe

# Application Settings
FLASK_ENV=production
DEBUG=False
UPLOAD_FOLDER=/opt/streaming-panel/static/uploads
MAX_CONTENT_LENGTH=104857600

# RTMP Settings
RTMP_PORT=1935
RTMP_TIMEOUT=30

# Stream Storage
HLS_PATH=/opt/streaming-panel/static/streams/hls
DASH_PATH=/opt/streaming-panel/static/streams/dash
RECORDINGS_PATH=/opt/streaming-panel/static/recordings

# Security Headers
SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=31536000
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_BROWSER_XSS_FILTER=True
EOF
    
    # Set proper permissions
    chmod 600 /opt/streaming-panel/.env
    
    print_info "Environment configuration created"
}

setup_systemd_services() {
    print_step "Setting up systemd services..."
    
    # Create systemd service file
    sudo tee /etc/systemd/system/streaming-panel.service << EOF > /dev/null
[Unit]
Description=Advanced Streaming Panel
After=network.target postgresql.service redis.service
Requires=postgresql.service redis.service

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=/opt/streaming-panel
Environment=PATH=/opt/streaming-panel/venv/bin
ExecStart=/opt/streaming-panel/venv/bin/gunicorn --bind 127.0.0.1:5000 --workers 4 --timeout 120 main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Enable and start service
    sudo systemctl daemon-reload
    sudo systemctl enable streaming-panel
    
    print_info "Systemd services configured"
}

setup_firewall() {
    print_step "Configuring firewall..."
    
    # Configure UFW (Ubuntu/Debian)
    if command -v ufw &> /dev/null; then
        sudo ufw allow 22/tcp      # SSH
        sudo ufw allow 80/tcp      # HTTP
        sudo ufw allow 443/tcp     # HTTPS
        sudo ufw allow 1935/tcp    # RTMP
        sudo ufw --force enable
    fi
    
    # Configure firewalld (RHEL/CentOS)
    if command -v firewall-cmd &> /dev/null; then
        sudo firewall-cmd --permanent --add-service=ssh
        sudo firewall-cmd --permanent --add-service=http
        sudo firewall-cmd --permanent --add-service=https
        sudo firewall-cmd --permanent --add-port=1935/tcp
        sudo firewall-cmd --reload
    fi
    
    print_info "Firewall configured"
}

setup_ssl() {
    print_step "Setting up SSL certificates..."
    
    read -p "Enter your domain name (leave blank to skip SSL setup): " DOMAIN
    
    if [ -n "$DOMAIN" ]; then
        # Update Nginx configuration with domain
        sudo sed -i "s/server_name _;/server_name $DOMAIN;/" /etc/nginx/sites-available/streaming-panel
        sudo nginx -t && sudo systemctl reload nginx
        
        # Obtain SSL certificate
        sudo certbot --nginx -d $DOMAIN
        
        print_info "SSL certificate obtained for $DOMAIN"
    else
        print_info "SSL setup skipped"
    fi
}

copy_application_files() {
    print_step "Copying application files..."
    
    # Copy all application files to /opt/streaming-panel
    cp -r * /opt/streaming-panel/ 2>/dev/null || true
    
    # Set proper ownership
    sudo chown -R $USER:$USER /opt/streaming-panel
    
    print_info "Application files copied successfully"
}

run_database_migrations() {
    print_step "Running database migrations..."
    
    cd /opt/streaming-panel
    source venv/bin/activate
    
    # Initialize database
    python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"
    
    deactivate
    
    print_info "Database migrations completed"
}

create_admin_user() {
    print_step "Creating admin user..."
    
    read -p "Enter admin username: " ADMIN_USER
    read -s -p "Enter admin password: " ADMIN_PASS
    echo
    
    cd /opt/streaming-panel
    source venv/bin/activate
    
    python3 -c "
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='$ADMIN_USER',
        email='admin@localhost',
        password_hash=generate_password_hash('$ADMIN_PASS')
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully')
"
    
    deactivate
    
    print_info "Admin user created: $ADMIN_USER"
}

start_services() {
    print_step "Starting all services..."
    
    # Start database services
    sudo systemctl start postgresql redis-server
    
    # Start application services
    sudo systemctl start nginx
    sudo supervisorctl start all
    
    # Start streaming panel
    sudo systemctl start streaming-panel
    
    print_info "All services started successfully"
}

print_completion() {
    echo
    echo -e "${GREEN}=================================================="
    echo "  Installation Completed Successfully!"
    echo "==================================================${NC}"
    echo
    echo -e "${BLUE}Access your streaming panel at:${NC}"
    echo "  → http://localhost (or your domain)"
    echo
    echo -e "${BLUE}RTMP streaming endpoint:${NC}"
    echo "  → rtmp://localhost:1935/live/your_stream_key"
    echo
    echo -e "${BLUE}Service management:${NC}"
    echo "  → sudo systemctl status streaming-panel"
    echo "  → sudo supervisorctl status"
    echo "  → sudo nginx -t && sudo systemctl reload nginx"
    echo
    echo -e "${BLUE}Log files:${NC}"
    echo "  → Application: /opt/streaming-panel/logs/app.log"
    echo "  → Nginx: /var/log/nginx/access.log"
    echo "  → PostgreSQL: /var/log/postgresql/"
    echo
    echo -e "${YELLOW}Important:${NC}"
    echo "  → Update database password in /opt/streaming-panel/.env"
    echo "  → Configure your domain and SSL certificates"
    echo "  → Review firewall settings for your environment"
    echo
    echo -e "${GREEN}Thank you for using Advanced Streaming Panel!${NC}"
    echo -e "${BLUE}Copyright © 2025 Expert Dev UX${NC}"
    echo
}

# Main installation flow
main() {
    print_header
    
    # Pre-installation checks
    check_os
    check_requirements
    
    # System setup
    install_system_dependencies
    install_python
    install_nodejs
    setup_database
    
    # Application setup
    create_project_structure
    copy_application_files
    install_python_dependencies
    create_environment_file
    
    # Service configuration
    setup_nginx
    setup_rtmp_module
    setup_supervisor
    setup_systemd_services
    setup_firewall
    
    # Database and user setup
    run_database_migrations
    create_admin_user
    
    # SSL setup (optional)
    setup_ssl
    
    # Start services
    start_services
    
    # Completion message
    print_completion
}

# Run installation
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi