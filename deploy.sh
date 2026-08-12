#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

print_header() {
    echo -e "\n${BOLD}${CYAN}===============================================================${NC}"
    echo -e "${BOLD}$1${NC}"
    echo -e "${BOLD}${CYAN}===============================================================${NC}\n"
}

print_step() {
    echo -e "\n${BOLD}${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}


# ---------------------------------------------------------------
# Проверка root
# ---------------------------------------------------------------

check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "Запусти скрипт через sudo или от root."
        exit 1
    fi
}


# ---------------------------------------------------------------
# Ввод параметров
# ---------------------------------------------------------------

get_config() {

    print_header "НАСТРОЙКА ПАРАМЕТРОВ"

    read -p "Домен: " DOMAIN

    if [ -z "$DOMAIN" ]; then
        print_error "Домен не может быть пустым."
        exit 1
    fi

    read -p "Email Let's Encrypt: " EMAIL

    if [ -z "$EMAIL" ]; then
        print_error "Email не может быть пустым."
        exit 1
    fi

    read -p "Название приложения [FastAPI Shop]: " APP_NAME
    APP_NAME=${APP_NAME:-"FastAPI Shop"}

    echo
    echo "Домен:   $DOMAIN"
    echo "WWW:     www.$DOMAIN"
    echo "Email:   $EMAIL"
    echo "App:     $APP_NAME"
    echo

    read -p "Всё верно? (y/n): " CONFIRM

    if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
        print_warning "Отменено."
        exit 0
    fi
}


# ---------------------------------------------------------------
# Проверка структуры проекта
# ---------------------------------------------------------------

check_project() {

    print_step "Проверка структуры проекта"

    REQUIRED_FILES=(
        "docker-compose.yml"
        "backend/Dockerfile"
        "backend/pyproject.toml"
        "backend/poetry.lock"
        "frontend/Dockerfile"
        "nginx"
    )

    for FILE in "${REQUIRED_FILES[@]}"; do
        if [ ! -e "$FILE" ]; then
            print_error "Не найден: $FILE"
            exit 1
        fi
    done

    print_success "Структура проекта корректная"
}


# ---------------------------------------------------------------
# Создание .env
# ---------------------------------------------------------------

create_env() {

    print_step "Создание .env"

    cat > .env << EOF
DOMAIN=$DOMAIN
EMAIL=$EMAIL
APP_NAME=$APP_NAME
DEBUG=False
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
VITE_API_BASE_URL=https://$DOMAIN/api
EOF

    chmod 600 .env

    print_success ".env создан"
}


# ---------------------------------------------------------------
# Backend .env
# ---------------------------------------------------------------

create_backend_env() {

    print_step "Создание backend/.env"

    SECRET_KEY=$(openssl rand -hex 32)

    cat > backend/.env << EOF
APP_NAME=$APP_NAME
DEBUG=False

DATABASE_URL=sqlite:///./shop.db
REDIS_URL=redis://redis:6379/0
CACHE_TTL_SECONDS=86400

SECRET_KEY=$SECRET_KEY
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRES_MINUTES=30

CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN

STATIC_DIR=static
IMAGES_DIR=static/images
EOF

    chmod 600 backend/.env

    print_success "backend/.env создан"
}


# ---------------------------------------------------------------
# Добавляем backend/.env в compose, если его там нет
# ---------------------------------------------------------------

configure_compose() {

    print_step "Проверка docker-compose.yml"

    if grep -q "env_file:" docker-compose.yml; then
        print_info "env_file уже присутствует"
    else

        print_info "Добавляем backend/.env в backend service"

        python3 << 'PY'
from pathlib import Path

path = Path("docker-compose.yml")
text = path.read_text()

old = """  backend:
    build:"""

new = """  backend:
    env_file:
      - backend/.env
    build:"""

if old in text:
    text = text.replace(old, new, 1)

path.write_text(text)
PY

        print_success "backend/.env подключён к контейнеру"
    fi
}


# ---------------------------------------------------------------
# Nginx
# ---------------------------------------------------------------

configure_nginx() {

    print_step "Создание Nginx конфигурации"

    mkdir -p nginx

    cat > nginx/nginx.conf << EOF
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server_tokens off;
    client_max_body_size 10M;

    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/json
        application/xml+rss;

    server {
        listen 80;
        server_name $DOMAIN www.$DOMAIN;

        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }

        location / {
            return 301 https://\$host\$request_uri;
        }
    }

    server {
        listen 443 ssl;
        http2 on;

        server_name $DOMAIN www.$DOMAIN;

        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

        ssl_protocols TLSv1.2 TLSv1.3;

        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Content-Type-Options "nosniff" always;

        # Frontend
        location / {
            proxy_pass http://frontend:80;

            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend:8000;

            proxy_set_header Host \$host;
            proxy_set_header X-Real-IP \$remote_addr;
            proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto \$scheme;

            proxy_http_version 1.1;

            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Backend static
        location /static/ {
            alias /app/backend/static/;

            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Health
        location /health {
            proxy_pass http://backend:8000;

            access_log off;
        }
    }
}
EOF

    print_success "Nginx конфигурация создана"
}


# ---------------------------------------------------------------
# Certbot
# ---------------------------------------------------------------

setup_certbot() {

    print_step "Проверка SSL сертификатов"

    mkdir -p certbot/www

    if [ -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_success "SSL сертификаты уже существуют"

        return 0
    fi

    print_info "Получение SSL сертификата..."

    if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
        print_error "Порт 80 занят."
        print_info "Освободи порт 80 и запусти скрипт снова."
        exit 1
    fi

    docker run -d \
        --name certbot-nginx-temp \
        -p 80:80 \
        -v "$(pwd)/certbot/www:/usr/share/nginx/html:ro" \
        nginx:alpine

    sleep 3

    certbot certonly \
        --webroot \
        --webroot-path="$(pwd)/certbot/www" \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN" \
        -d "www.$DOMAIN"

    docker rm -f certbot-nginx-temp >/dev/null 2>&1 || true

    if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
        print_error "SSL сертификат не был создан."
        exit 1
    fi

    print_success "SSL сертификаты получены"
}


# ---------------------------------------------------------------
# Директории
# ---------------------------------------------------------------

create_directories() {

    print_step "Создание необходимых директорий"

    mkdir -p backend/static/images
    mkdir -p certbot/www

    chmod -R 755 backend/static
    chmod -R 755 certbot/www

    print_success "Директории готовы"
}


# ---------------------------------------------------------------
# Проверка Docker Compose
# ---------------------------------------------------------------

validate_compose() {

    print_step "Проверка docker-compose.yml"

    docker compose config >/dev/null

    print_success "docker-compose.yml корректный"
}


# ---------------------------------------------------------------
# Сборка
# ---------------------------------------------------------------

build_containers() {

    print_step "Сборка Docker образов"

    docker compose build

    print_success "Docker образы собраны"
}


# ---------------------------------------------------------------
# Запуск
# ---------------------------------------------------------------

start_containers() {

    print_step "Запуск контейнеров"

    docker compose up -d

    print_info "Ожидание запуска..."
    sleep 10

    docker compose ps

    echo
    print_success "Контейнеры запущены"
}


# ---------------------------------------------------------------
# Проверка
# ---------------------------------------------------------------

health_check() {

    print_step "Проверка приложения"

    sleep 5

    if curl -f -s \
        "https://$DOMAIN/health" \
        >/dev/null 2>&1; then

        print_success "HTTPS работает"

    else

        print_warning "HTTPS пока не отвечает"
        print_info "Проверь логи:"
        echo "docker compose logs nginx"
        echo "docker compose logs backend"
    fi
}


# ---------------------------------------------------------------
# Информация
# ---------------------------------------------------------------

show_info() {

    print_header "РАЗВЕРТЫВАНИЕ ЗАВЕРШЕНО"

    echo -e "${GREEN}Магазин:${NC}"
    echo "https://$DOMAIN"

    echo
    echo -e "${GREEN}API:${NC}"
    echo "https://$DOMAIN/api/docs"

    echo
    echo -e "${GREEN}Health:${NC}"
    echo "https://$DOMAIN/health"

    echo
    echo -e "${GREEN}Полезные команды:${NC}"
    echo
    echo "docker compose ps"
    echo "docker compose logs -f"
    echo "docker compose logs -f backend"
    echo "docker compose logs -f nginx"
    echo "docker compose restart"
    echo "docker compose down"

    echo
}


# ---------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------

main() {

    clear

    print_header "FASTAPI SHOP — DEPLOY"

    check_root
    get_config

    print_header "НАЧАЛО DEPLOY"

    check_project
    create_env
    create_backend_env
    configure_compose
    create_directories
    setup_certbot
    configure_nginx
    validate_compose
    build_containers
    start_containers
    health_check
    show_info
}

main