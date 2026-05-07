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
| 2026-05-07 20:31:45 +03:00 | Начата переработка README для GitHub продвижения | Пользователь запросил README уровня популярных репозиториев, SEO и Star History | `README.md`, `DEV_CHECKLIST.md` | Просмотр текущего README; анализ README популярных проектов и GitHub docs | Решение: англоязычный README с badges, quick start, SEO-keywords, troubleshooting, roadmap, Star History |
| 2026-05-07 20:36:00 +03:00 | README переписан для GitHub discovery | Нужно повысить понятность, поисковую релевантность и конверсию в stars | `README.md` | `python -m pytest`; `Select-String` по Star History и SEO секциям | 12 тестов прошли; Star History указывает на `HereIamGosu/android-tv-adb-control-center` |
| 2026-05-07 20:38:00 +03:00 | Проверен и удалён некачественный generated screenshot | Offscreen Qt отрисовал текст квадратами; такой asset ухудшил бы README | `docs/assets/android-tv-adb-control-center-main.png` | `view_image`; безопасное удаление внутри workspace | PNG удалён; README оставляет путь для будущего нормального Windows screenshot |
| 2026-05-07 20:41:36 +03:00 | Начата UX-правка подключения | Пользователь не понимает, что вводить и что происходит при подключении | `app/ui/main_window.py`, `app/ui/dialogs/device_profile_dialog.py`, `DEV_CHECKLIST.md` | Анализ текущего GUI | Нужно добавить подсказки рядом с IP/pair/connect полями и видимый статус выполняемой операции |
| 2026-05-07 20:48:00 +03:00 | Добавлены подсказки и статус операций в GUI | Нужно сделать подключение понятным и приложение визуально отзывчивым | `app/ui/main_window.py`, `app/ui/dialogs/device_profile_dialog.py` | `python -m compileall app tests`; `python -m pytest`; offscreen `MainWindow()`; offscreen `DeviceProfileDialog()` | 12 тестов прошли; compileall прошёл; окно и диалог создаются; `__pycache__` удалён |
| 2026-05-07 20:50:00 +03:00 | Коммит и push UX-правки | Пользователь попросил всегда делать коммиты и push самостоятельно | `README.md`, `app/ui/main_window.py`, `app/ui/dialogs/device_profile_dialog.py`, `DEV_CHECKLIST.md` | `git commit -m "Improve connection guidance in UI"`; `git push` | Коммит `cb4bd7b` успешно отправлен в `origin/main` |
| 2026-05-07 20:46:06 +03:00 | Начата переработка GUI в два столбца | Пользователь сообщил, что подсказки не влезают и GUI с артефактами | `app/ui/main_window.py`, `DEV_CHECKLIST.md` | Анализ текущего одноколоночного layout | Нужно разделить левую и правую зоны и ограничить ширину подсказок |
| 2026-05-07 20:52:00 +03:00 | Главное окно переведено в два столбца | Нужно убрать переполнение подсказок и сделать интерфейс читаемым | `app/ui/main_window.py` | `python -m pytest`; `python -m compileall app tests`; offscreen `MainWindow()` | 12 тестов прошли; compileall прошёл; окно создаётся размером 1280x760; `__pycache__` удалён |
| 2026-05-07 20:48:33 +03:00 | Начата реализация смены языка EN/RU | Пользователь запросил переключение языка в приложении | `app/core/device_profile.py`, `app/ui/main_window.py`, `tests/test_settings_store.py`, `DEV_CHECKLIST.md` | Анализ текущего settings и UI | Нужно хранить язык в settings и обновлять основные labels/buttons/help без перезапуска |
| 2026-05-07 20:56:00 +03:00 | Добавлен переключатель языка EN/RU | Нужно дать пользователю смену языка внутри приложения | `app/core/device_profile.py`, `app/ui/main_window.py`, `tests/test_settings_store.py` | `python -m compileall app tests`; `python -m pytest`; offscreen переключение EN/RU | 12 тестов прошли; compileall прошёл; offscreen проверка `language switch ok`; `__pycache__` удалён |

## Current Task

| Поле | Значение |
|---|---|
| Задача | Создать MVP-каркас Windows-first приложения `ADB TV Control Center` на Python/PySide6 |
| Источник требования | Спецификация пользователя `ADB TV Control Center`, версия документа `0.1` |
| Статус | Завершено: переключатель EN/RU |
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
| Publish | `git push` | Passed | HTTPS remote; `cb4bd7b` отправлен в `origin/main` |
| README SEO | Проверка Star History / SEO секций через `Select-String` | Passed | Ссылки используют `HereIamGosu/android-tv-adb-control-center` |
| UI hints | Offscreen construction: `MainWindow()` и `DeviceProfileDialog()` | Passed | Проверяет новые подсказки и layouts без запуска event loop |
| Two-column GUI | Offscreen construction: `MainWindow()` | Passed | Окно создаётся размером 1280x760 |
| Language switch | Offscreen `MainWindow()`: переключение `ru` и `en` | Passed | Заголовок блока меняется `Как подключиться` / `How to connect` |

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

- README переписан на английском языке под GitHub discovery: badges, quick start, features, troubleshooting, security model, SEO topics, roadmap, Star History.
- В GUI добавлены подсказки рядом с IP, pair-port, connect-port и serial, блок `How to connect`, а также строка `Current operation` на время ADB/scrcpy-команд.
- Главное окно перестроено из одного вертикального столбца в два столбца: подключение слева, действия/пульт/лог справа.
- В главное окно добавлен переключатель языка EN/RU с сохранением выбора в `settings.json`.

#### Fixed

- Device-действия включаются только после подтверждённого состояния `device` из `adb devices -l`.

## Open Questions

| Вопрос | Почему важен | Что блокирует | Возможное действие |
|---|---|---|---|
| Нужно ли реализовать полноценный streaming Logcat в MVP вместо stub-кнопки? | В спецификации `FR-ADBGUI-013` допускается MVP-режим logcat, но стартовый промпт разрешает оставить stub | Полное соответствие FR-ADBGUI-013 | Добавить отдельное окно с `QProcess` для `adb -s <serial> logcat` |
| Нужно ли проверять GUI вручную на реальном Android TV? | Unit-тесты не подтверждают реальные ADB/scrcpy сценарии | Подтверждение pair/connect/scrcpy/APK/screenshot/keyevents | Запустить manual checklist из README/спецификации на устройстве |
