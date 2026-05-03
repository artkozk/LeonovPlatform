# Google OAuth Production Setup — 2026-04-23

## 1. Цель

Включить вход через Google на production-площадке Leonov Care без изменения кода и без повторной разработки frontend.

Текущий production контур:

- Frontend URL: `http://85.198.82.221:8511`
- API URL: `http://85.198.82.221:8510/api/v1`
- Backend OAuth старт: `GET /api/v1/auth/oauth/google/start`
- Критичный env: `GOOGLE_CLIENT_ID`

Почему это важно:

- Пока `GOOGLE_CLIENT_ID` пустой, кнопка Google в UI корректно показывает статус `Setup`, но вход не может быть завершен.
- После заполнения `GOOGLE_CLIENT_ID` вход включается сразу, потому что frontend берет client id и из backend runtime.

## 2. Что видно на вашем скриншоте и что это значит

На странице Google Cloud Console `APIs & Services -> Credentials` видно:

1. `No OAuth clients to display` — OAuth client еще не создан.
2. Баннер `Remember to configure the OAuth consent screen...` — экран согласия не заполнен.

Это нормальная промежуточная стадия. Нужно сделать два шага: consent screen и OAuth client.

## 3. Шаги в Google Cloud Console

### Шаг 3.1 — Настроить OAuth consent screen

Откройте кнопку `Configure consent screen` и заполните:

1. App name: `Leonov Care`
2. User support email: ваш рабочий email (можно временный)
3. Developer contact email: ваш рабочий email
4. Audience:
- если аккаунты только ваши/команды на старте: `External` + тестовые пользователи
- если планируете сразу публично: `External` и пройти verification позже
5. Сохранить (`Save and Continue`) все шаги.

Примечание:

- Для базового входа через Google Sign-In scope `openid email profile` обычно подставляется автоматически.

### Шаг 3.2 — Создать OAuth Client ID

В `Credentials -> + Create credentials -> OAuth client ID`:

1. Application type: `Web application`
2. Name: `LeonovCare Web Prod`
3. Authorized JavaScript origins:
- `http://85.198.82.221:8511`
- (опционально для локальной разработки) `http://localhost:5173`
4. Authorized redirect URIs:
- для текущей реализации ID token callback в JS можно оставить пустым
- если Google просит обязательный URI, укажите `http://85.198.82.221:8511`
5. Сохранить.

Результат:

- получите `Client ID` вида `xxxx-xxxx.apps.googleusercontent.com`

## 4. Применение Client ID на сервере

Ниже production-команды для вашего сервера:

```bash
ssh root@85.198.82.221
# password: Publish_Tw36gi

cd /opt/leonovcare-platform/current

# 1) проставить GOOGLE_CLIENT_ID в PM2 ecosystem
sed -i 's#GOOGLE_CLIENT_ID: ".*"#GOOGLE_CLIENT_ID: "REPLACE_WITH_REAL_CLIENT_ID"#' deploy/server/ecosystem.config.cjs

# 2) перезапустить backend процессы
pm2 restart leonovcare-api leonovcare-worker

# 3) проверить статус
pm2 status
curl -s http://127.0.0.1:8510/api/v1/auth/oauth/google/start
```

Ожидаемый ответ после успеха:

- `status: ready_for_id_token`
- `clientId: <ваш client id>`

## 5. Runtime проверка в браузере

1. Откройте `http://85.198.82.221:8511`
2. На auth-странице нажмите `Continue with Google`
3. Выберите аккаунт Google
4. После входа ожидаем редирект в `/dashboard`

Если вход не произошел:

1. Проверить, что origin точно совпадает (`http://85.198.82.221:8511` без лишнего слэша).
2. Проверить, что в backend `GOOGLE_CLIENT_ID` совпадает символ-в-символ с Google Console.
3. Проверить в DevTools Network ответы:
- `/auth/oauth/google/start` должен быть `ready_for_id_token`
- `/auth/oauth/google/callback` должен вернуть `200` и токены.

## 6. Что уже реализовано в коде (без дополнительных доработок)

1. Backend валидирует Google `id_token` через Google tokeninfo endpoint.
2. Backend проверяет `aud == GOOGLE_CLIENT_ID` и `email_verified=true`.
3. Frontend поддерживает оба режима:
- build-time `VITE_GOOGLE_CLIENT_ID`
- runtime client id из backend `/auth/oauth/google/start`
4. Если Google не настроен, UI показывает честный статус `Setup` вместо ложной "активной" кнопки.

## 7. Почему текущий подход выбран именно так

1. Runtime-получение `clientId` снижает риск после деплоя: не нужен отдельный rebuild frontend для каждой замены Google Client ID.
2. Проверка `aud` и `email_verified` нужна для защиты от подмены токенов и неподтвержденных аккаунтов.
3. Минимальный production-путь позволяет быстро включить Google вход без миграций БД и без refactor auth-контуров.

## 8. История обновления документа

- v1.0 (2026-04-23): добавлен полный production runbook для включения Google OAuth на текущей площадке с конкретными origin/командами проверки.

## 9. Статус на 2026-04-29 (launch profile)

1. Этот runbook сохранен как историческая инструкция.
2. В текущем launch-профиле пользовательский OAuth вход отключен (email-only auth).
3. Почему так сделано:
- для старта на первую когорту выбран минимальный и предсказуемый auth-контур без зависимости от сторонних OAuth-провайдеров.
4. Когда возвращать OAuth:
- после стабилизации основного запуска,
- после отдельного security-review,
- после включения только полностью верифицированных provider flow.
