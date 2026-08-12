# ============================================================================
# 🛍️  FASTAPI SHOP - ПРОФЕССИОНАЛЬНЫЙ СКРИПТ РАЗВЕРТЫВАНИЯ 🛍️
# ============================================================================
set -e
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; MAGENTA='\033[0;35m'; CYAN='\033[0;36m'; NC='\033[0m'; BOLD='\033[1m'
print_header() { echo -e "\n${BOLD}${MAGENTA}╔═══════════════════════════════════════════════════════════════╗${NC}"; echo -e "${BOLD}${MAGENTA}║${NC}  $1"; echo -e "${BOLD}${MAGENTA}╚═══════════════════════════════════════════════════════════════╝${NC}\n"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }; print_error() { echo -e "${RED}✗${NC} $1"; }; print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }; print_info() { echo -e "${CYAN}ℹ${NC} $1"; }; print_step() { echo -e "\n${BOLD}${BLUE}▶${NC} $1${NC}"; }
check_root() { if [ "$EUID" -ne 0 ]; then print_error "Запустите через sudo: sudo bash deploy.sh"; exit 1; fi; }
get_user_input() {
    print_header "НАСТРОЙКА ПАРАМЕТРОВ"
    while true; do
        echo -e "${BOLD}${YELLOW}Введите основной домен (например: vashtera.digital):${NC}"
        read -p "> " DOMAIN
        if [[ "$DOMAIN" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?\.[a-zA-Z]{2,}$ ]]; then print_success "Домен: $DOMAIN"; break; fi
        print_error "Некорректный формат!"
    done
    echo -e "\n${BOLD}${YELLOW}Введите email для SSL:${NC}"; read -p "> " EMAIL
    POSTGRES_USER="user_$(date +%s | tail -c 5)"; POSTGRES_PASSWORD=$(openssl rand -base64 12); POSTGRES_DB="fastapi_shop"
}
fix_project_files() {
    print_step "Исправление конфигурации (Poetry & Dockerignore)"
    if [ -f "backend/pyproject.toml" ]; then
        if ! grep -q "package-mode = false" backend/pyproject.toml; then
            sed -i '/\[tool.poetry\]/a package-mode = false' backend/pyproject.toml 2>/dev/null || sed -i '/\[project\]/a package-mode = false' backend/pyproject.toml
        fi
    fi
    cat <<EOD > backend/.dockerignore
__pycache__/
*.py[cod]
.venv/
.env
.git/
tests/
EOD
}
obtain_ssl_certificates() {
    print_step "Проверка SSL"
    if [ -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then print_success "SSL уже есть. Пропускаем."; return 0; fi
    mkdir -p certbot/www
    docker run --rm -d --name nginx_temp -p 80:80 -v "$(pwd)/certbot/www:/usr/share/nginx/html" nginx:alpine > /dev/null 2>&1
    sleep 5
    certbot certonly --webroot --webroot-path="$(pwd)/certbot/www" --email "$EMAIL" --agree-tos --no-eff-email -d "$DOMAIN" -d "www.$DOMAIN" || true
    docker stop nginx_temp > /dev/null 2>&1 || true
}
update_configs() {
    print_step "Обновление конфигов"
    cat <<EOD > backend/.env
DATABASE_URL=postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@db:5432/$POSTGRES_DB
REDIS_URL=redis://redis:6379/0
SECRET_KEY=$(openssl rand -hex 32)
CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN
EOD
    mkdir -p nginx
    cat <<EOD > nginx/nginx.conf
events { worker_connections 1024; }
http {
    include /etc/nginx/mime.types;
    server {
        listen 80; server_name $DOMAIN www.$DOMAIN;
        location /.well-known/acme-challenge/ { root /var/www/certbot; }
        location / { return 301 https://\$host\$request_uri; }
    }
    server {
        listen 443 ssl http2; server_name $DOMAIN www.$DOMAIN;
        ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
        location / { proxy_pass http://frontend:80; proxy_set_header Host \$host; }
        location /api { proxy_pass http://backend:8000; proxy_set_header Host \$host; }
    }
}
EOD
    cat <<EOD > docker-compose.yml
services:
  backend:
    build: ./backend
    env_file: backend/.env
    depends_on:
      db: { condition: service_healthy }
      redis: { condition: service_started }
    networks: [fashop_network]
  frontend:
    build: { context: ./frontend, args: [VITE_API_BASE_URL=https://$DOMAIN/api] }
    networks: [fashop_network]
  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - ./certbot/www:/var/www/certbot:ro
    ports: ["80:80", "443:443"]
    networks: [fashop_network]
  db:
    image: postgres:16
    environment: { POSTGRES_USER: $POSTGRES_USER, POSTGRES_PASSWORD: $POSTGRES_PASSWORD, POSTGRES_DB: $POSTGRES_DB }
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB"]
      interval: 5s; timeout: 5s; retries: 5
    networks: [fashop_network]
  redis:
    image: redis:7
    networks: [fashop_network]
networks:
  fashop_network:
    driver: bridge
EOD
}
main( ) { check_root; get_user_input; fix_project_files; obtain_ssl_certificates; update_configs; 
    print_step "Сборка и запуск"; docker compose down || true; docker compose up -d --build; 
    print_success "ГОТОВО! Сайт: https://$DOMAIN"; }
main
EOF
