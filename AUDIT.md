# AUDIT.md

## Контекст проверки

Проверяется существующий репозиторий `ADB TV Control Center`, Windows-first desktop GUI на Python/PySide6 для управления Android TV / Google TV через `adb.exe` и `scrcpy.exe`.

Источник задачи: запрос пользователя от 2026-05-13. Дополнительные локальные источники: `README.md`, текущая реализация `app/*`.

## Среда

| Параметр | Значение |
|---|---|
| OS | Windows, PowerShell |
| Python | `Python 3.11.9` |
| pip | `pip 26.0.1` |
| PySide6 | `6.11.0`, уже установлен |
| pytest | `9.0.2`, установлен в активном окружении |

## Команды проверки

| Команда | Результат |
|---|---|
| `python --version` | `Python 3.11.9` |
| `pip --version` | `pip 26.0.1` |
| `python -m pip install -r requirements.txt` | Зависимости уже установлены |
| `python -m compileall app` | Проходит |
| `python -m pytest` до исправлений | Не проходит как проверка качества: `collected 0 items`, тесты отсутствуют |
| `python -m pytest` после исправлений | `16 passed` |
| `python -m pytest` после исправления worker lifecycle | `18 passed` |
| `python -m pytest` после явных timeout-контрактов | `20 passed` |
| `python -m compileall app tests` после исправлений | Проходит |
| `$env:QT_QPA_PLATFORM='offscreen'; python -m app.main` | Процесс не завершился за 10 секунд, ожидаемо из-за запуска event loop GUI |
| `$env:QT_QPA_PLATFORM='offscreen'; python -c "... MainWindow() ..."` | Главное окно создается |
| `rg "shell=True\|os\.system\|subprocess\.run\(" app tests` | `shell=True` и `os.system` не найдены; найдены только контролируемые `subprocess.run()` в `ADBRunner` и `ScrcpyRunner` |
| `npx jest --runInBand --no-coverage` | Не применимо: `package.json` отсутствует, проект Python |
| `npm run build` | Не применимо: `package.json` отсутствует, проект Python |

## Структура проекта

```text
app/
  main.py                         # точка входа PySide6
  core/
    adb_runner.py                 # запуск adb, парсинг adb devices
    apk_install_service.py        # установка APK через ADBRunner
    command_interpreter.py        # интерпретация типовых ошибок ADB
    command_result.py             # модель результата команды
    device_info_service.py        # чтение getprop
    device_profile.py             # настройки и профиль устройства
    scrcpy_runner.py              # запуск scrcpy
    settings_store.py             # JSON settings в APPDATA
    screenshot_service.py         # screencap bytes в PNG
    validators.py                 # валидация IP/host/port/path/serial
  ui/
    main_window.py                # основной workflow и фоновые workers
    dialogs/
      device_profile_dialog.py    # редактирование профиля
      settings_dialog.py          # пути adb/scrcpy и папка скриншотов
      shell_window.py             # одноразовые adb shell команды
    widgets/
      command_log_widget.py       # отображение command/stdout/stderr/interpretation
      device_status_widget.py     # статус выбранного serial
      remote_control_widget.py    # keyevent-кнопки
README.md
requirements.txt
DEV_CHECKLIST.md                  # локальный процессный журнал, сейчас в .gitignore
```

## Найденные дефекты

### Critical

- Исправлено: `app/ui/dialogs/shell_window.py` больше не выполняет `adb shell` синхронно из обработчика кнопки; команда запускается через `QRunnable`.
- Исправлено: добавлен тестовый контур. `python -m pytest` выполняет 16 тестов.

### High

- Исправлено: `app/core/device_profile.py` хранит `pair_port`; диалог профиля позволяет задать pair-port отдельно от connect-port.
- Исправлено: `app/ui/main_window.py` включает `scrcpy serial` только после подтвержденного состояния `device`.
- Исправлено: `app/core/scrcpy_runner.py` требует serial в `launch(serial, ...)`; auto-режим вынесен в `launch_auto()`.

### Medium

- Исправлено: `app/core/adb_runner.py` нормализует неизвестные состояния `adb devices` в `unknown`.
- Исправлено: `README.md` приведен к требуемой русскоязычной структуре.
- Исправлено: `app/ui/dialogs/device_profile_dialog.py` обновляет `updated_at` при редактировании профиля.

### Low

- Реальный запуск `adb.exe`, `scrcpy.exe` и Android TV сценарии не проверялись: в среде нет подключенного устройства и настроенных путей инструментов.

## Сверка с источниками

- Android Developers ADB: официальная документация описывает `adb devices`, состояния `offline`/`device`, `adb install path_to_apk`, а также форму `adb [-d | -e | -s serial_number] command` для выбора устройства при нескольких подключениях. Источник: https://developer.android.com/tools/adb
- Android Developers Wireless debugging: для TV/Wear OS указан Android 13 / API 33+ и одна Wi-Fi сеть. Источник: https://developer.android.com/tools/adb
- Android Developers Logcat: `adb logcat` является сокращением для `adb shell logcat`, вывод потоковый. Источник: https://developer.android.com/tools/logcat
- Genymobile/scrcpy: при нескольких устройствах нужен выбор через `scrcpy -s <serial>` или другие selector-режимы; для TCP/IP доступен `--tcpip=IP:PORT`. Источник: https://github.com/Genymobile/scrcpy/blob/master/doc/connection.md
- Qt for Python QProcess: `readyReadStandardOutput`, `readyReadStandardError`, `finished`, `terminate()` и `kill()` предусмотрены для долгоживущих процессов. Источник: https://doc.qt.io/qtforpython-6.5/PySide6/QtCore/QProcess.html
- Python subprocess: `subprocess.run()` является рекомендуемым API для конечных команд, `Popen` применяется для продвинутых сценариев; `shell=False` является параметром API, `timeout` и `capture_output` поддерживаются. Источник: https://docs.python.org/3.11/library/subprocess.html

## Что исправлено

- `app/core/adb_runner.py`: timeout-значения вынесены в явные константы. Быстрые ADB-команды ограничены 10 секундами, pair/connect 30 секундами, shell 45 секундами, screenshot 20 секундами, install APK 180 секундами.
- `app/core/scrcpy_runner.py`: `scrcpy --version` ограничен 10 секундами.
- `tests/test_adb_runner.py`, `tests/test_scrcpy_runner.py`: добавлены проверки timeout-контрактов для публичных runner-методов.
- `README.md`: добавлено описание timeout-лимитов.
- `app/ui/main_window.py`: устранен crash-кандидат после `Check tools` и других фоновых действий. `CommandWorker` теперь `setAutoDelete(False)`, удерживается в `self._active_workers`, удаляется из набора только после обработки сигнала. Повторный запуск операции во время активной операции игнорируется.
- `app/ui/main_window.py`: исключения в UI callback после успешного worker больше не пробрасываются в Qt event loop; они переводятся в управляемую ошибку через `_fail_worker()`.
- `app/ui/dialogs/shell_window.py`: применена та же схема удержания `ShellCommandWorker`, чтобы shell-команды не теряли Python/QObject-обвязку сигналов.
- `tests/test_main_window_workers.py`: добавлены регрессионные тесты на `Check tools` с отсутствующими exe и на исключение в callback без утечки worker.
- `app/core/device_profile.py`: добавлено поле `pair_port` в профиль устройства, сохранена обратная совместимость при загрузке старых JSON без этого поля.
- `app/ui/dialogs/device_profile_dialog.py`: добавлено поле pair-port, валидация pair-port и обновление `updated_at` при редактировании.
- `app/ui/main_window.py`: pair-port загружается из профиля; `scrcpy serial` блокируется до подтвержденного состояния `device`; auto-запуск scrcpy использует отдельный метод.
- `app/core/scrcpy_runner.py`: `launch()` требует serial и формирует `scrcpy -s <serial>`; добавлен `launch_auto()`.
- `app/ui/dialogs/shell_window.py`: выполнение `adb shell` перенесено в фоновой `QRunnable`, чтобы не блокировать shell-окно.
- `app/core/adb_runner.py`: неизвестные состояния `adb devices -l` нормализуются в `unknown`.
- `tests/*`: добавлены unit-тесты validators, command_interpreter, settings_store, devices parser, ADB command formation, screenshot bytes, scrcpy command formation и dangerous shell patterns.
- `requirements.txt`: добавлен `pytest>=8`, потому что тесты являются частью Definition of Done.
- `README.md`: переписан на русском языке в структуре текущего задания.

## Что осталось за пределами текущего прохода

- Реальная ручная проверка pair/connect/scrcpy/APK/screenshot/keyevent на Android TV.
- Полноценное окно streaming logcat с start/stop через `QProcess`.
- Хранение и live-сбор stdout/stderr долгоживущего `scrcpy` процесса. Сейчас MVP фиксирует успешный старт процесса и OSError при запуске.

## Риски

- Часть поведения можно проверить только с установленными `adb.exe`, `scrcpy.exe` и Android TV в одной сети.
- `python -m app.main` запускает GUI event loop и не должен завершаться сам; для автоматической проверки используется offscreen-конструирование `MainWindow`.
- В текущем проходе не выполнялась ручная сверка конкретной установленной версии `scrcpy.exe --version` и ее полного набора CLI-параметров.
- `DEV_CHECKLIST.md` обновлен локально, но файл находится в `.gitignore`; если журнал должен версионироваться, нужно убрать его из `.gitignore` отдельным решением.

## Ручные проверки перед релизом

- Настроить реальные пути к `adb.exe` и `scrcpy.exe`.
- Выполнить `adb pair IP:PAIR_PORT` через UI с новым pairing code.
- Выполнить `adb connect IP:CONNECT_PORT` и убедиться, что `adb devices -l` показывает serial в состоянии `device`.
- Запустить `scrcpy -s <serial>` из UI.
- Установить тестовый APK.
- Сохранить PNG-скриншот и открыть файл.
- Отправить keyevent-команды пульта.
