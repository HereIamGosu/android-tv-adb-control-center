# ADB TV Control Center

## Назначение

`ADB TV Control Center` — Windows-first desktop-приложение на Python/PySide6 для управления Android TV / Google TV через внешние `adb.exe` и `scrcpy.exe`.

Приложение не реализует собственный ADB-протокол. Оно формирует безопасные команды и показывает пользователю команду, stdout, stderr и интерпретацию ошибок.

## Возможности MVP

- настройка путей к `adb.exe` и `scrcpy.exe`;
- проверка версий инструментов;
- создание профиля устройства;
- `adb pair`, `adb connect`, `adb disconnect`;
- `adb devices -l`;
- запуск `scrcpy -s <serial>`;
- установка APK;
- снятие скриншота через `exec-out screencap -p`;
- быстрые keyevent-команды пульта;
- простое shell-окно;
- лог последней команды и русскоязычная диагностика ошибок.

## Требования

- Windows 10 или Windows 11;
- Python 3.11+;
- Android SDK Platform Tools с `adb.exe`;
- `scrcpy.exe`;
- Android TV / Google TV-устройство с включённым режимом разработчика и Wireless Debugging.

## Установка

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск

```powershell
python -m app.main
```

## Первичная настройка

1. Откройте `Settings`.
2. Укажите путь к `adb.exe`.
3. Укажите путь к `scrcpy.exe`.
4. Укажите папку для скриншотов.
5. Нажмите `Check tools`.

## Pair и Connect

1. Создайте профиль устройства.
2. Введите IP, pair-port и connect-port.
3. Нажмите `Pair` и введите pairing code с экрана TV.
4. Нажмите `Connect`.
5. После connect приложение выполнит `adb devices -l` и проверит serial.

Pair-port и connect-port часто разные. Для `adb pair` используйте порт из окна сопряжения с кодом, для `adb connect` — порт из строки IP-адреса и порта Wireless Debugging.

## Зеркалирование через scrcpy

После подключения нажмите `Launch scrcpy`. Команда запускается в виде:

```powershell
scrcpy -s <serial> <extra_args>
```

## Установка APK

Нажмите `Install APK`, выберите `.apk` файл и подтвердите установку. Путь APK передаётся отдельным аргументом процесса.

## Скриншоты

Нажмите `Screenshot`. Приложение выполняет:

```powershell
adb -s <serial> exec-out screencap -p
```

PNG-данные читаются из stdout как bytes и записываются в файл `screenshot_YYYY-MM-DD_HH-mm-ss.png`.

## Диагностика ошибок

Интерпретируются распространённые ошибки:

- `protocol fault`;
- `failed to connect`;
- `more than one device/emulator`;
- `unauthorized`;
- `device offline`;
- `INSTALL_FAILED_VERSION_DOWNGRADE`;
- `INSTALL_FAILED_UPDATE_INCOMPATIBLE`;
- `INSTALL_PARSE_FAILED_NO_CERTIFICATES`.

Технический stdout/stderr не скрывается.

## Безопасность

Приложение не добавляет destructive-функции в интерфейс. Shell-окно предупреждает перед потенциально опасными командами:

- `pm uninstall`;
- `cmd package uninstall`;
- `settings put`;
- `reboot bootloader`;
- `reboot recovery`;
- `wipe`;
- `rm -rf`;
- `dd`;
- `su`.

## Ограничения MVP

- Logcat в текущем каркасе оставлен stub-кнопкой.
- Интерактивный PTY shell не реализован.
- Реальные сценарии pair/connect/scrcpy/APK/screenshot требуют Android TV-устройство и установленные `adb.exe`/`scrcpy.exe`.
