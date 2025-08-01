#!/bin/bash

echo "1. Проверка работы сервиса:"
curl -s http://localhost:8081/ | jq .
echo

echo "2. Проверка состояния сервиса:"
curl -s http://localhost:8081/health | jq .
echo

echo "3. Тест без токена:"
curl -s -w "HTTP Status: %{http_code}\n" http://localhost:8081/reports
echo

echo "4. Получение токена для prothetic1:"
TOKEN=$(curl -s -X POST http://localhost:8080/realms/reports-realm/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=reports-api" \
  -d "client_secret=oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq" \
  -d "username=prothetic1" \
  -d "password=prothetic123" | jq -r '.access_token')

echo "Токен получен: ${TOKEN:0:50}..."
echo

echo "5. Получение отчета с правильным токеном:"
curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8081/reports | jq .
echo

echo "6. Тест с пользователем без роли prothetic_user:"
USER_TOKEN=$(curl -s -X POST http://localhost:8080/realms/reports-realm/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=reports-api" \
  -d "client_secret=oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq" \
  -d "username=user1" \
  -d "password=password123" | jq -r '.access_token')

curl -s -H "Authorization: Bearer $USER_TOKEN" http://localhost:8081/reports
echo

echo "Тестирование завершено" 
