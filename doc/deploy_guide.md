# Руководство по деплою LLM Telegram Bot

## 🏠 Локальное тестирование

### Подготовка окружения
```bash
# 1. Клонирование репозитория
git clone <repository-url>
cd llm-tg-bot-start

# 2. Создание .env файла
cp env.example .env
# Заполните .env своими токенами

# 3. Настройка системного промпта
# Отредактируйте src/system_prompt.md под вашу компанию
```

### Локальный запуск через uv
```bash
# Установка зависимостей
make install

# Запуск тестов
make test

# Запуск бота
make dev  # Интерактивный режим
# или
make run  # В фоне
```

### Локальный запуск через Docker
```bash
# Сборка образа
make build

# Запуск в контейнере
make run-docker

# Просмотр логов
make logs-docker

# Остановка
make stop-docker
```

## 🌐 Деплой на VPS

### Требования к серверу
- **OS:** Ubuntu 20.04+ или аналог
- **RAM:** Минимум 512MB
- **Docker:** Версия 20.10+
- **Docker Compose:** Версия 2.0+
- **Git:** Любая современная версия
- **Интернет:** Постоянное подключение

### Подготовка VPS

#### 1. Обновление системы
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Установка Docker
```bash
# Установка Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Добавление пользователя в группу docker
sudo usermod -aG docker $USER

# Перелогиньтесь для применения изменений
exit
```

#### 3. Установка Docker Compose
```bash
# Docker Compose уже включен в современные версии Docker
docker compose version
```

#### 4. Установка Git
```bash
sudo apt install git -y
```

### Деплой приложения

#### 1. Клонирование репозитория
```bash
cd /opt  # или любая другая директория
sudo git clone <repository-url> llm-bot
sudo chown -R $USER:$USER llm-bot
cd llm-bot
```

#### 2. Настройка окружения
```bash
# Создание production .env
cp env.example .env

# Заполните .env БОЕВЫМИ токенами
nano .env
```

**Пример production .env:**
```env
# Telegram Bot (БОЕВОЙ токен от @BotFather)
TELEGRAM_BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA

# OpenRouter API (БОЕВОЙ ключ)
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 3. Настройка системного промпта
```bash
# Отредактируйте промпт под вашу компанию
nano src/system_prompt.md
```

#### 4. Сборка и запуск
```bash
# Сборка образа
docker compose build

# Запуск в production режиме
docker compose up -d

# Проверка статуса
docker compose ps
```

### Проверка работоспособности

#### 1. Проверка контейнера
```bash
# Статус контейнера
docker compose ps

# Логи приложения
docker compose logs -f

# Ресурсы
docker stats llm-telegram-bot
```

#### 2. Тестирование бота
- Отправьте `/start` боту в Telegram
- Проверьте ответ на команды `/help`, `/clear`
- Задайте вопрос боту и убедитесь в корректности ответа

## 🔄 Обновление приложения

### Процесс обновления
```bash
cd /opt/llm-bot

# 1. Получение изменений
git pull origin main

# 2. Пересборка образа (если изменились зависимости)
docker compose build

# 3. Перезапуск сервиса
docker compose down
docker compose up -d

# 4. Проверка логов
docker compose logs -f
```

### Автоматизация обновлений (опционально)
Создайте скрипт `update.sh`:
```bash
#!/bin/bash
cd /opt/llm-bot
git pull origin main
docker compose build
docker compose down
docker compose up -d
echo "Бот обновлен и перезапущен"
```

## 📊 Мониторинг и поддержка

### Просмотр логов
```bash
# Логи приложения
docker compose logs -f

# Логи из файла (если настроено двойное логирование)
tail -f logs/llm_bot.log

# Логи за последний час
docker compose logs --since 1h
```

### Полезные команды
```bash
# Статус сервисов
docker compose ps

# Использование ресурсов
docker stats

# Перезапуск без пересборки
docker compose restart

# Полная очистка (ОСТОРОЖНО!)
docker compose down --rmi all --volumes
```

### Backup логов
```bash
# Создание архива логов
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/

# Автоматическая ротация (добавить в cron)
# 0 2 * * * cd /opt/llm-bot && tar -czf logs-backup-$(date +\%Y\%m\%d).tar.gz logs/ && find . -name "logs-backup-*.tar.gz" -mtime +30 -delete
```

## 🚨 Устранение неполадок

### Проблема: Бот не отвечает
```bash
# 1. Проверьте статус контейнера
docker compose ps

# 2. Посмотрите логи
docker compose logs

# 3. Проверьте .env файл
cat .env | grep -v "^#"

# 4. Перезапустите сервис
docker compose restart
```

### Проблема: Ошибки API
```bash
# Проверьте токены в .env
# Убедитесь что:
# - TELEGRAM_BOT_TOKEN корректный
# - OPENROUTER_API_KEY действующий
# - Есть доступ к интернету
```

### Проблема: Нехватка места
```bash
# Очистка Docker
docker system prune -f

# Очистка старых образов
docker image prune -a -f

# Проверка места
df -h
```

## 🔧 Дополнительные настройки

### Настройка автозапуска
Docker Compose с `restart: unless-stopped` автоматически перезапускает контейнеры при перезагрузке сервера.

### Настройка файрвола (если нужен)
```bash
# Основной трафик идет через Telegram API (исходящий)
# Входящие подключения не нужны
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing
```

### Мониторинг ресурсов
```bash
# Установка htop для мониторинга
sudo apt install htop -y

# Просмотр ресурсов
htop
```

---

**Готово!** 🎉 Ваш LLM Telegram Bot успешно развернут и готов к работе.

Для поддержки обращайтесь к документации или проверяйте логи при возникновении проблем.