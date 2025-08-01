## Тестирование API

### Запуск проекта
```bash
docker compose up -d
```

### Тестовые пользователи
- **prothetic1** / **prothetic123** - имеет роль `prothetic_user`
- **prothetic2** / **prothetic123** - имеет роль `prothetic_user`
- **prothetic3** / **prothetic123** - имеет роль `prothetic_user`
- **user1** / **password123** - имеет роль `user` (без доступа к отчетам)

### Получение токена
```bash
curl -X POST http://localhost:8080/realms/reports-realm/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=reports-api" \
  -d "client_secret=oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq" \
  -d "username=prothetic1" \
  -d "password=prothetic123"
```

### Тестирование API отчетов

#### 1. Проверка работы сервиса
```bash
curl http://localhost:8081/
```

#### 2. Проверка состояния сервиса
```bash
curl http://localhost:8081/health
```

#### 3. Получение отчета (с токеном)
```bash
TOKEN="<access_token_из_предыдущего_запроса>"
curl -H "Authorization: Bearer $TOKEN" http://localhost:8081/reports
```

#### 4. Получение конкретного отчета по ID
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8081/reports/test_report_123
```

#### 5. Тест без токена (должен вернуть 401)
```bash
curl http://localhost:8081/reports
```

#### 6. Тест с пользователем без роли prothetic_user (должен вернуть 403)
```bash
# Получаем токен для user1
USER_TOKEN=$(curl -s -X POST http://localhost:8080/realms/reports-realm/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=reports-api" \
  -d "client_secret=oNwoLQdvJAvRcL89SydqCWCe5ry1jMgq" \
  -d "username=user1" \
  -d "password=password123" | jq -r '.access_token')

# Пытаемся получить отчет
curl -H "Authorization: Bearer $USER_TOKEN" http://localhost:8081/reports
```

### Ожидаемые результаты

#### Успешный запрос отчета:
```json
{
  "success": true,
  "message": "Отчет для пользователя prothetic1",
  "data": {
    "user_id": "c3be8c93-b776-4186-9e25-b52de7f4614a",
    "report": "report mock"
  }
}
```

#### Запрос без токена:
```json
{
  "detail": "Not authenticated"
}
```

#### Запрос с неправильной ролью:
```json
{
  "detail": "Доступ запрещен. Требуется роль prothetic_user"
}
```

### Быстрое тестирование
Для быстрого тестирования всех функций API используйте готовый скрипт:

```bash
./test_api.sh
```
