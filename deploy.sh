ls
cd /root/telegram-bot-queue/ && git pull origin develop
docker-compose -f docker-compose.prod.yml stop
docker-compose -f docker-compose.prod.yml up -d --build
