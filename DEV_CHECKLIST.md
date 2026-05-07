# DEV_CHECKLIST

## Development Log

| Дата/время | Действие | Причина | Файлы | Проверка | Результат |
|---|---|---|---|---|---|
| 2026-05-07 20:04:43 +03:00 | Старт задачи, анализ пустого репозитория | Требуется реализовать MVP-каркас по спецификации `ADB TV Control Center v0.1` | `DEV_CHECKLIST.md` | `Get-ChildItem -Force`, `rg --files` | Репозиторий пустой, конфликтующих файлов нет |
| 2026-05-07 20:06:00 +03:00 | Зафиксирован план реализации | Требование AGENTS: перед реализацией указать план и проверки | `DEV_CHECKLIST.md` | Анализ спецификации | План: core-модули -> GUI -> тесты -> проверки |
| 2026-05-07 20:12:00 +03:00 | Добавлены core-модули | Требования к моделям, validators, settings_store, ADBRunner, ScrcpyRunner и сервисам | `app/core/*` | Статический просмотр файлов | Команды формируются списками аргументов; shell=False; PNG stdout хранится как bytes |
| 2026-05-07 20:23:00 +03:00 | Добавлены GUI, README, requirements и unit-тесты | Требования MVP к минимальному окну, документации и проверкам core | `app/ui/*`, `app/main.py`, `README.md`, `requirements.txt`, `tests/*` | Статический просмотр структуры | GUI вызывает core; добавлены тесты без реального устройства |
| 2026-05-07 20:28:00 +03:00 | Установлены зависимости | Для проверки GUI-импорта требовался PySide6 | `requirements.txt` | `python -m pip install -r requirements.txt` | Установлены `PySide6 6.11.0`, `shiboken6 6.11.0`; `pytest` уже был установлен |
| 2026-05-07 20:29:00 +03:00 | Запущены проверки | Требование AGENTS: после изменений запускать доступные проверки | `app/*`, `tests/*` | `python -m pytest`; `python -m compileall app tests`; `python -c "from app.ui.main_window import MainWindow; print('ui import ok')"` | 12 тестов прошли; compileall прошёл; GUI import прошёл |
| 2026-05-07 20:29:30 +03:00 | Проверены обязательные npm-команды | Требование AGENTS указывает `npx jest` и `npm run build` | `package.json` отсутствует | `npx jest --runInBand --no-coverage`; `npm run build` | Неприменимо: проект Python, Jest config и `package.json` отсутствуют |
| 2026-05-07 20:30:00 +03:00 | Удалены generated-файлы `__pycache__` | `compileall` создал временные артефакты проверки | `app/**/__pycache__`, `tests/**/__pycache__` | Безопасное удаление только внутри workspace; повторный поиск | Удалено 6 директорий, остаток `__pycache__`: 0 |
| 2026-05-07 20:33:00 +03:00 | Проверено создание главного окна | Нужно поймать ошибки конструирования PySide6 UI без реальной GUI-сессии | `app/ui/main_window.py` | `$env:QT_QPA_PLATFORM='offscreen'; python -c "... MainWindow() ..."` | Главное окно сконструировано успешно |
| 2026-05-07 20:36:00 +03:00 | Исправлено включение device-действий | Требование UI: действия доступны только после статуса `device`, а не по сохранённому serial | `app/ui/main_window.py` | `python -m pytest`; `python -m compileall app tests`; offscreen `MainWindow()` | 12 тестов прошли; compileall прошёл; окно создаётся |
| 2026-05-07 20:25:11 +03:00 | Начата публикация в GitHub remote | Пользователь указал `git@github.com:HereIamGosu/android-tv-adb-control-center.git`; локальный каталог ещё не был git-репозиторием | `DEV_CHECKLIST.md`, весь текущий каркас проекта | `git status`, `git remote -v`, `git log` | До инициализации команды вернули `not a git repository` |
| 2026-05-07 20:26:00 +03:00 | Добавлен `.gitignore` перед первым коммитом | Нужно не публиковать generated-файлы Python/pytest/venv | `.gitignore`, `.pytest_cache/` | `Get-ChildItem -Force` | `.pytest_cache` обнаружен и исключён из git |
| 2026-05-07 20:28:00 +03:00 | Проверено состояние перед первым коммитом | Нужно подтвердить, что в коммит попадут только исходники, тесты, README, requirements и DEV_CHECKLIST | весь проект | `python -m pytest`; offscreen `MainWindow()`; `git status --short --ignored` | 12 тестов прошли; окно создаётся; `DEV_CHECKLIST.md` не игнорируется |
| 2026-05-07 20:31:00 +03:00 | Создан первый git commit и настроен `origin` | Нужно подготовить проект к публикации в репозиторий пользователя | весь проект | `git add -A`; `git commit -m "Initial ADB TV Control Center MVP"`; `git remote -v` | Коммит `eeb0270`; remote `git@github.com:HereIamGosu/android-tv-adb-control-center.git` |
| 2026-05-07 20:32:00 +03:00 | Выполнена попытка `git push -u origin main` | Пользователь указал push-команду для публикации | локальный `main`, remote `origin` | `git push -u origin main` | Ошибка: `git@github.com: Permission denied (publickey)`; нужен SSH-доступ к GitHub или HTTPS remote |

## Current Task

| Поле | Значение |
|---|---|
| Задача | Создать MVP-каркас Windows-first приложения `ADB TV Control Center` на Python/PySide6 |
| Источник требования | Спецификация пользователя `ADB TV Control Center`, версия документа `0.1` |
| Статус | Завершено |
| Риски | GUI и реальные ADB/scrcpy сценарии нельзя полноценно проверить без Windows GUI-сессии, установленных инструментов и Android TV-устройства |
| Definition of Done | Созданы структура, core-модули, минимальный GUI, README, requirements, unit-тесты; запущены доступные проверки; ограничения проверки зафиксированы |

## Test Matrix

| Область | Команда / сценарий | Результат | Комментарий |
|---|---|---|---|
| Unit | `python -m pytest` | Passed: 12 tests | Не требует Android-устройство |
| Syntax | `python -m compileall app tests` | Passed | Созданные `__pycache__` удалены после проверки |
| GUI import | `python -c "from app.ui.main_window import MainWindow; print('ui import ok')"` | Passed | PySide6 установлен через `requirements.txt` |
| GUI construction | `$env:QT_QPA_PLATFORM='offscreen'; python -c "... MainWindow() ..."` | Passed | Проверяет создание виджетов без запуска event loop |
| JS tests | `npx jest --runInBand --no-coverage` | Not applicable | Нет Jest config; проект Python |
| Build | `npm run build` | Not applicable | Нет `package.json`; проект Python |
| Manual ADB | Pair/connect/scrcpy/APK/screenshot/keyevents на Android TV | Not run | Требуются `adb.exe`, `scrcpy.exe` и устройство |
| Publish | `git push -u origin main` | Failed | GitHub SSH auth: `Permission denied (publickey)` |

## Changelog

### Unreleased

#### Added

- Core-модели `CommandResult`, `DeviceProfile`, `AppSettings`.
- Валидаторы IP/host, port, executable, APK path, serial.
- JSON-хранилище settings/profiles с backup повреждённого JSON.
- `ADBRunner`, `ScrcpyRunner`, интерпретатор ошибок, сервисы screenshot/APK/device info.
- Минимальный PySide6 GUI: настройки, профиль, pair/connect/devices, scrcpy, APK, screenshot, shell, пульт, command log.
- README на русском языке и `requirements.txt`.
- `.gitignore` для Python/pytest/venv/generated артефактов.

#### Tests

- Unit-тесты validators, command_interpreter, settings_store и `adb devices -l` parser.

#### Changed

#### Fixed

- Device-действия включаются только после подтверждённого состояния `device` из `adb devices -l`.

## Open Questions

| Вопрос | Почему важен | Что блокирует | Возможное действие |
|---|---|---|---|
| Нужно ли реализовать полноценный streaming Logcat в MVP вместо stub-кнопки? | В спецификации `FR-ADBGUI-013` допускается MVP-режим logcat, но стартовый промпт разрешает оставить stub | Полное соответствие FR-ADBGUI-013 | Добавить отдельное окно с `QProcess` для `adb -s <serial> logcat` |
| Нужно ли проверять GUI вручную на реальном Android TV? | Unit-тесты не подтверждают реальные ADB/scrcpy сценарии | Подтверждение pair/connect/scrcpy/APK/screenshot/keyevents | Запустить manual checklist из README/спецификации на устройстве |
