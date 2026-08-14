# Production-развёртывание AI и visual refinement BizFlow, 14 августа 2026

## Назначение отчёта

Документ фиксирует фактическое состояние production после выпуска карточек-досье, новой визуальной системы, безопасного AI-контракта, интерактивной карты связей, перетаскиваемых блоков шаблонов и мобильных исправлений. Здесь отдельно записан внешний блокер Groq, чтобы локальный fallback не был ошибочно принят за подтверждённую работу облачной модели.

## Состав релиза

- Продуктовый коммит: `46b3237 feat(business-control): refine AI and interactive workspace`.
- Операционный коммит: `b2f0931 ops(business-control): harden AI visual deployment`.
- Ветка: `artkozk/business-control-platform`.
- Production-домен: `https://control.e-rd.ru`.
- Новый release: `/opt/business-control/releases/20260814-ai-visual-46b3237`.
- Предыдущий release: `/opt/business-control/releases/20260814-autonomous-audit-c425d66`.
- SHA-256 Linux-бинарника: `effe9d39bb36d0aff14b175ec38d0120da4ac8e678a7ac3749ba4b5985d696eb`.

Отображаемое имя закрытого продукта изменено на `BizFlow`. Это рабочее имя текущего контура, а не подтверждённый публичный товарный знак: до запуска независимых команд необходимо отдельно проверить домен и права на бренд.

## Предрелизная проверка

Локально выполнены:

```text
node --check web/app.js                         ok
go test ./...                                  ok
go vet ./...                                   ok
git diff --check                               ok
поиск шаблона Groq-секрета в коде и docs       совпадений нет
```

В реальном браузере до выкладки проверены desktop `1280x720` и mobile `390x844`: обзор, рабочая очередь, карточка, custom select, карта связей, шаблоны, мобильное меню, backdrop, закрытие слоёв и перестроение контекста карточки. Ошибок консоли в пройденных сценариях не обнаружено.

На сервер были загружены только временные артефакты в `/tmp`. Перед изменением production выполнены:

1. `bash -n` обоих release-скриптов.
2. Проверка SHA-256 загруженного бинарника против локального файла.
3. Применение seed к отдельной SQLite-копии production-БД.
4. Повторное применение seed для проверки идемпотентности.
5. `PRAGMA integrity_check`, вернувший `ok`.
6. `pragma_foreign_key_check`, вернувший `0` нарушений.

Dry-run создал ровно четыре задачи разработки и четыре доказательства. Корневая цель на копии получила название `Развитие платформы «BizFlow»` и прогресс `72`.

## Развёртывание и backup

Развёртывание выполнено скриптом `business-control/deploy/deploy-ai-visual-refinement-20260814.sh`. Скрипт останавливает сервис только после успешного dry-run, делает консистентный SQLite backup, применяет seed, атомарно меняет симлинк `current` и ждёт health-check. При ошибке он восстанавливает одновременно предыдущий release и БД, а не только бинарник.

- Backup: `/var/lib/business-control/backups/business-control-20260814-111709-pre-ai-visual.db`.
- SHA-256 backup: `bd8195182bbc1668e9b25b5acf501be232d94ce7d84b659398d49122ebfb5c41`.
- Результат переключения: exit code `0`.
- Первый локальный health-запрос попал в короткое окно старта процесса и не подключился; следующий запрос внутри предусмотренного цикла прошёл. Это ожидаемое поведение retry-проверки, а не незавершённый релиз.

## Фактический статус Groq

Ключ был передан на сервер через стандартный ввод SSH, без аргумента командной строки, frontend, Git и карточек проекта. Файл окружения до проверки имел и после изменений сохранил режим `600 root:root`.

Прямой запрос `GET /openai/v1/models` с production-сервера вернул:

```text
HTTP 403
message: Forbidden
```

Ответ не позволяет доказанно различить блокировку IP/региона, ограничение аккаунта или политику самого ключа. Поэтому выполнены следующие действия:

- ключ не оставлен в активном `/etc/business-control.env`;
- защищённая копия сохранена в `/etc/business-control.groq.disabled` с режимом `600 root:root`;
- сервис запущен без `GROQ_API_KEY` и использует быстрый локальный fallback;
- задача настройки Groq оставлена `blocked`, прогресс `80%`, а не отмечена выполненной;
- в карточку задачи добавлено доказательство фактического ответа `403` без значения секрета.

Такое решение сохраняет работающий AI-интерфейс и не добавляет задержку от повторных безуспешных обращений к провайдеру. Для активации Groq сначала нужен успешный серверный запрос с HTTP `200`; только после него конфигурацию можно вернуть в активный env и перезапустить сервис.

Поскольку ключ был опубликован в пользовательском сообщении, после устранения причины `403` его следует заменить новым. Старое значение не должно возвращаться в активное окружение.

## Production smoke

После переключения независимо проверено:

```text
systemd service                              active
/opt/business-control/current               20260814-ai-visual-46b3237
http://127.0.0.1:8522/api/health             {"status":"ok"}
https://control.e-rd.ru/                     200
https://control.e-rd.ru/api/health           200
https://control.e-rd.ru/app.js               200, 217386 bytes
https://control.e-rd.ru/styles.css           200, 125784 bytes
https://control.e-rd.ru/fonts/Onest-Variable.ttf 200, 193056 bytes
HTML title BizFlow                           найден ровно один раз
SQLite integrity_check                      ok
SQLite foreign key violations               0
ошибки business-control в journal за 10 минут 0
```

Production-БД содержит:

- четыре выполненные задачи visual/AI-релиза от `artkozk`;
- четыре доказательства их выполнения;
- корневую цель `Развитие платформы «BizFlow»` с прогрессом `72%`;
- отдельную Groq-задачу `blocked|80`, отражающую реальное внешнее состояние.

В production-браузере дополнительно проверен незалогиненный экран: отдельной общей HTTP-авторизации `founders` нет, открывается собственная форма входа BizFlow, логотип и локальный Onest отображаются корректно.

## Откат

Откат нужен только при подтверждённой регрессии. Если после релиза появились новые пользовательские записи, сначала необходимо сделать новый backup или перенести эти записи: восстановление pre-release snapshot удалит более поздние изменения.

```bash
systemctl stop business-control
ln -sfn /opt/business-control/releases/20260814-autonomous-audit-c425d66 /opt/business-control/current.next
mv -Tf /opt/business-control/current.next /opt/business-control/current
rm -f /var/lib/business-control/business-control.db-wal /var/lib/business-control/business-control.db-shm
install -o business-control -g business-control -m 0640 \
  /var/lib/business-control/backups/business-control-20260814-111709-pre-ai-visual.db \
  /var/lib/business-control/business-control.db.restore
mv -f /var/lib/business-control/business-control.db.restore \
  /var/lib/business-control/business-control.db
systemctl start business-control
curl -fsS http://127.0.0.1:8522/api/health
```

После отката обязательны `PRAGMA integrity_check`, `pragma_foreign_key_check`, HTTPS health-check и просмотр `journalctl -u business-control`.
