# ADB TV Control Center

## Назначение

`ADB TV Control Center` — Windows-first desktop-приложение на Python/PySide6 для управления Android TV, Google TV и Xiaomi TV Stick через официальные инструменты `adb.exe` и `scrcpy.exe`.

Приложение не реализует собственный ADB-протокол. Оно формирует безопасные команды, запускает внешние инструменты без shell-интерпретации, показывает stdout/stderr, код завершения и инженерное объяснение типовых ошибок.

## Возможности

- настройка путей к `adb.exe` и `scrcpy.exe`;
- профили устройств с IP, pair-port, connect-port, serial, аргументами scrcpy и папкой скриншотов;
- `adb pair`, `adb connect`, `adb devices -l`, reset ADB server;
- запуск `scrcpy -s <serial>`;
- установка APK через `adb -s <serial> install <apk>`;
- PNG-скриншот через `adb -s <serial> exec-out screencap -p`;
- кнопки пульта через `adb shell input keyevent`;
- простое shell-окно для `adb -s <serial> shell <command>`;
- русские диагностические сообщения для распространенных ADB/APK ошибок.

## Требования

| Компонент | Требование |
|---|---|
| OS | Windows 10/11 |
| Python | 3.11+ |
| GUI | PySide6 |
| ADB | `adb.exe` из Android SDK Platform Tools |
| Зеркалирование | `scrcpy.exe` |
| Тесты | pytest |
| Устройство | Android TV / Google TV с включенным Wireless Debugging |

Для Android TV официальная документация Android указывает Wireless Debugging для Android 13 / API 33+ и работу компьютера и устройства в одной сети.

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Запуск

```powershell
python -m app.main
```

Проверка без открытия обычной GUI-сессии:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
python -c "from PySide6.QtWidgets import QApplication; from app.ui.main_window import MainWindow; import sys; app=QApplication(sys.argv); w=MainWindow(); print('main window constructed')"
```

## Первичная настройка

1. Откройте `Settings`.
2. Укажите путь к `adb.exe`.
3. Укажите путь к `scrcpy.exe`.
4. Укажите папку для скриншотов.
5. Создайте профиль устройства.

Настройки хранятся локально:

```text
%APPDATA%\ADBTVControlCenter\settings.json
```

Если JSON поврежден, приложение создает backup и новый `settings.json`.

## Pair и Connect

Pair-port и connect-port нельзя считать одним и тем же портом.

```text
adb pair IP:PAIR_PORT
adb connect IP:CONNECT_PORT
```

- `PAIR_PORT` берется из окна «Pair device with pairing code». Этот порт относится к текущей pairing-сессии.
- `CONNECT_PORT` берется из основной строки «IP address & Port» на экране Wireless Debugging.
- После `connect` приложение выполняет `adb devices -l`.
- Device-действия включаются только когда выбранный serial находится в состоянии `device`.

Если подключено несколько устройств, команды выполняются с `-s <serial>`.

## Зеркалирование через scrcpy

Основной режим MVP:

```powershell
scrcpy -s <serial>
```

Serial для TCP/IP обычно имеет вид:

```text
192.168.1.10:5555
```

Дополнительные аргументы scrcpy вводятся в профиле и разбираются как список аргументов, без shell-интерпретации.

## Установка APK

Команда:

```powershell
adb -s <serial> install <path-to-apk>
```

APK должен существовать и иметь расширение `.apk`. Путь передается отдельным аргументом, поэтому пробелы в пути допустимы.

## Скриншоты

Команда:

```powershell
adb -s <serial> exec-out screencap -p
```

PNG читается из stdout как bytes и сохраняется в папку профиля. Shell redirection не используется.

## Команды пульта

Кнопки пульта вызывают:

```powershell
adb -s <serial> shell input keyevent <KEYCODE>
```

Поддерживаются DPAD, OK, Back, Home, Menu, Volume Up/Down и Power.

## Диагностика ошибок

Приложение интерпретирует типовые ошибки:

| Ошибка | Объяснение |
|---|---|
| `protocol fault` | Вероятно перепутан pair-port/connect-port, устарела pairing-сессия или завис adb-server |
| `failed to connect` | Нужно проверить IP, connect-port, одну Wi-Fi сеть, Wireless Debugging и firewall |
| `more than one device/emulator` | Нужно выбрать serial и выполнять команды с `-s` |
| `unauthorized` | Нужно подтвердить отладку на экране TV |
| `device offline` | Нужно перезапустить adb-server и Wireless Debugging |
| `INSTALL_FAILED_VERSION_DOWNGRADE` | Установленная версия приложения новее APK |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Пакет установлен с другой подписью |

## Безопасность

- Внешние команды формируются списком аргументов.
- `shell=True` не используется для ADB/scrcpy команд.
- Pairing code передается в stdin и не пишется в command log.
- У конечных ADB/scrcpy операций есть явные timeout-лимиты: быстрые проверки до 10 секунд, pair/connect до 30 секунд, shell-команда до 45 секунд, скриншот до 20 секунд, установка APK до 180 секунд.
- Потенциально опасные shell-паттерны требуют подтверждения: `pm uninstall`, `cmd package uninstall`, `settings put`, `reboot bootloader`, `reboot recovery`, `wipe`, `rm -rf`, `dd`, `su`.
- Приложение не скачивает APK, не обходит DRM, подписки, региональные ограничения или платный доступ.

## Ограничения MVP

- Полноценное streaming-окно `adb logcat` пока не реализовано.
- Реальные сценарии pair/connect/scrcpy/APK/screenshot требуют установленного `adb.exe`, `scrcpy.exe` и Android TV в одной сети.
- Автотесты не требуют реального устройства и проверяют только локальную логику, формирование команд и обработку результатов.
