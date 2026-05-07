from __future__ import annotations

from app.core.command_result import CommandResult


MESSAGES = {
    "en": {
        "protocol_fault": (
            "The wrong port may have been used, the pairing session may have expired, or adb-server may be stuck. "
            "Use the port from 'Pair device with pairing code' for adb pair, and the port from 'IP address & Port' for adb connect."
        ),
        "failed_to_connect": (
            "ADB could not connect to the device. Check IP, connect-port, same Wi-Fi/LAN, Wireless Debugging, and firewall."
        ),
        "more_than_one": "ADB sees multiple devices. Select a serial and run commands with -s.",
        "unauthorized": (
            "The device has not authorized debugging. Check the TV screen and approve the prompt. "
            "If needed, reset ADB authorizations in Developer Options."
        ),
        "offline": (
            "ADB sees the device, but the daemon is not responding. Restart adb-server, toggle Wireless Debugging, then connect again."
        ),
        "version_downgrade": (
            "The installed app version is newer than the selected APK. Use a newer APK or uninstall the old app manually outside the MVP flow."
        ),
        "signature": "The package is already installed with a different signature. It cannot be updated over the current version.",
        "certificates": "The APK is damaged or incorrectly signed: Android did not find valid signing certificates.",
        "timeout": "The command did not finish in time. Check the device state and try again.",
        "success": "Command completed successfully.",
        "generic_error": "The command exited with an error. Check stdout/stderr for technical details.",
    },
    "ru": {
        "protocol_fault": (
            "Вероятно, использован неправильный порт, pairing-сессия устарела или adb-server завис. "
            "Для adb pair используйте порт из окна «Сопряжение устройства с кодом», а для adb connect — порт из строки «IP-адрес и порт»."
        ),
        "failed_to_connect": (
            "ADB не смог подключиться к устройству. Проверьте IP, connect-port, одну Wi-Fi сеть, Wireless Debugging и firewall."
        ),
        "more_than_one": "ADB видит несколько устройств. Нужно выбрать serial и выполнять команды с параметром -s.",
        "unauthorized": (
            "Устройство не разрешило отладку. Проверьте экран TV и подтвердите разрешение. "
            "При необходимости сбросьте ADB authorizations в настройках разработчика."
        ),
        "offline": (
            "ADB видит устройство, но daemon не отвечает. Перезапустите adb-server, выключите и включите Wireless Debugging, затем повторите connect."
        ),
        "version_downgrade": (
            "Установленная версия приложения новее APK. Нужна более новая версия APK либо явное удаление старой версии пользователем вне MVP-сценария."
        ),
        "signature": "Пакет уже установлен с другой подписью. Обновление поверх текущей версии невозможно.",
        "certificates": "APK повреждён или неправильно подписан: Android не нашёл корректные сертификаты подписи.",
        "timeout": "Команда не завершилась за отведённое время. Проверьте состояние устройства и повторите операцию.",
        "success": "Команда выполнена успешно.",
        "generic_error": "Команда завершилась с ошибкой. Смотрите stdout/stderr для технических деталей.",
    },
}


class CommandInterpreter:
    RULES: tuple[tuple[str, str], ...] = (
        ("protocol fault", "protocol_fault"),
        ("failed to connect", "failed_to_connect"),
        ("more than one device/emulator", "more_than_one"),
        ("unauthorized", "unauthorized"),
        ("device offline", "offline"),
        ("offline", "offline"),
        ("INSTALL_FAILED_VERSION_DOWNGRADE", "version_downgrade"),
        ("INSTALL_FAILED_UPDATE_INCOMPATIBLE", "signature"),
        ("INSTALL_PARSE_FAILED_NO_CERTIFICATES", "certificates"),
    )

    def __init__(self, language: str = "ru"):
        self.language = language if language in MESSAGES else "en"

    def interpret(self, result: CommandResult) -> str:
        messages = MESSAGES[self.language]
        text = f"{result.stdout}\n{result.stderr}".lower()
        original = f"{result.stdout}\n{result.stderr}"
        for needle, message_key in self.RULES:
            if needle.lower() in text or needle in original:
                return messages[message_key]
        if result.status == "timeout":
            return messages["timeout"]
        if result.status == "success":
            return messages["success"]
        if result.exit_code not in (0, None):
            return messages["generic_error"]
        return ""
