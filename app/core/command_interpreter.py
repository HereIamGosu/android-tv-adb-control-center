from __future__ import annotations

from app.core.command_result import CommandResult


class CommandInterpreter:
    RULES: tuple[tuple[str, str], ...] = (
        (
            "protocol fault",
            "Вероятно, использован неправильный порт, pairing-сессия устарела или adb-server завис. "
            "Проверьте, что для adb pair используется порт из окна «Сопряжение устройства с кодом», "
            "а для adb connect — порт из строки «IP-адрес и порт».",
        ),
        (
            "failed to connect",
            "ADB не смог подключиться к устройству. Проверьте IP, connect-port, одну Wi-Fi сеть, "
            "состояние Wireless Debugging и firewall.",
        ),
        (
            "more than one device/emulator",
            "ADB видит несколько устройств. Нужно выбрать serial и выполнять команды с параметром -s.",
        ),
        (
            "unauthorized",
            "Устройство не разрешило отладку. Проверьте экран TV и подтвердите разрешение. "
            "При необходимости сбросьте ADB authorizations в настройках разработчика.",
        ),
        (
            "device offline",
            "ADB видит устройство, но daemon не отвечает. Перезапустите adb-server, выключите и включите "
            "Wireless Debugging, затем повторите connect.",
        ),
        (
            "offline",
            "ADB видит устройство, но daemon не отвечает. Перезапустите adb-server, выключите и включите "
            "Wireless Debugging, затем повторите connect.",
        ),
        (
            "INSTALL_FAILED_VERSION_DOWNGRADE",
            "Установленная версия приложения новее APK. Нужна более новая версия APK либо явное удаление "
            "старой версии пользователем вне MVP-сценария.",
        ),
        (
            "INSTALL_FAILED_UPDATE_INCOMPATIBLE",
            "Пакет уже установлен с другой подписью. Обновление поверх текущей версии невозможно.",
        ),
        (
            "INSTALL_PARSE_FAILED_NO_CERTIFICATES",
            "APK повреждён или неправильно подписан: Android не нашёл корректные сертификаты подписи.",
        ),
    )

    def interpret(self, result: CommandResult) -> str:
        text = f"{result.stdout}\n{result.stderr}".lower()
        original = f"{result.stdout}\n{result.stderr}"
        for needle, message in self.RULES:
            if needle.lower() in text or needle in original:
                return message
        if result.status == "timeout":
            return "Команда не завершилась за отведённое время. Проверьте состояние устройства и повторите операцию."
        if result.status == "success":
            return "Команда выполнена успешно."
        if result.exit_code not in (0, None):
            return "Команда завершилась с ошибкой. Смотрите stdout/stderr для технических деталей."
        return ""
