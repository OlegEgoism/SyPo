import gi
import os
import signal
import json

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib

LANGUAGES = {
    'ru': {
        'power_off': "Выключение",
        'reboot': "Перезагрузка",
        'lock': "Блокировка",
        'settings': "Таймер",
        'exit_app': "Выход",
        'minutes': "Минуты:",
        'action': "",
        'apply': "Применить",
        'cancel': "Отмена",
        'reset': "Сбросить",
        'confirm_title': "Подтверждение действия",
        'confirm_text_power_off': "Выключить компьютер?",
        'confirm_text_reboot': "Перезагрузить компьютер?",
        'confirm_text_lock': "Заблокировать экран?",
        'scheduled': "Запланировано",
        'error': "Ошибка",
        'error_minutes_positive': "Введите значение больше 0.",
        'notification': "Предупреждение",
        'action_in_1_min': "{} через 1 минуту.",
        'action_in_time': "{} через {} минут.",
        'cancelled': "Отменено",
        'cancelled_text': "Запланированное действие сброшено.",
        'language_name': "Русский",
        'language': "Язык",
    },
    'en': {
        'power_off': "Power Off",
        'reboot': "Reboot",
        'lock': "Lock",
        'settings': "Settings",
        'exit_app': "Exit",
        'minutes': "Minutes:",
        'action': "",
        'apply': "Apply",
        'cancel': "Cancel",
        'reset': "Reset",
        'confirm_title': "Confirm Action",
        'confirm_text_power_off': "Power off the computer?",
        'confirm_text_reboot': "Reboot the computer?",
        'confirm_text_lock': "Lock the screen?",
        'scheduled': "Scheduled",
        'error': "Error",
        'error_minutes_positive': "Please enter a value greater than 0.",
        'notification': "Notification",
        'action_in_1_min': "{} in 1 minute.",
        'action_in_time': "{} in {} minutes.",
        'cancelled': "Cancelled",
        'cancelled_text': "Scheduled action cancelled.",
        'language_name': "English",
        'language': "Language",
    },
    'cn': {
        'power_off': "关闭电源",
        'reboot': "重启",
        'lock': "锁屏",
        'settings': "设置",
        'exit_app': "退出",
        'minutes': "分钟:",
        'action': "",
        'apply': "应用",
        'cancel': "取消",
        'reset': "重置",
        'confirm_title': "确认操作",
        'confirm_text_power_off': "关闭计算机？",
        'confirm_text_reboot': "重启计算机？",
        'confirm_text_lock': "锁定屏幕？",
        'scheduled': "已安排",
        'error': "错误",
        'error_minutes_positive': "请输入大于0的值。",
        'notification': "通知",
        'action_in_1_min': "{} 还有1分钟。",
        'action_in_time': "{} 还有{}分钟。",
        'cancelled': "已取消",
        'cancelled_text': "已取消计划操作。",
        'language_name': "中文",
        'language': "语言",
    },
    'de': {
        'power_off': "Herunterfahren",
        'reboot': "Neustart",
        'lock': "Sperren",
        'settings': "Einstellungen",
        'exit_app': "Beenden",
        'minutes': "Minuten:",
        'action': "",
        'apply': "Übernehmen",
        'cancel': "Abbrechen",
        'reset': "Zurücksetzen",
        'confirm_title': "Aktion bestätigen",
        'confirm_text_power_off': "Computer ausschalten?",
        'confirm_text_reboot': "Computer neu starten?",
        'confirm_text_lock': "Bildschirm sperren?",
        'scheduled': "Geplant",
        'error': "Fehler",
        'error_minutes_positive': "Bitte geben Sie einen Wert größer als 0 ein.",
        'notification': "Benachrichtigung",
        'action_in_1_min': "{} in 1 Minute.",
        'action_in_time': "{} in {} Minuten.",
        'cancelled': "Abgebrochen",
        'cancelled_text': "Geplante Aktion abgebrochen.",
        'language_name': "Deutsch",
        'language': "Sprache",
    }
}

SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".power_control_settings.json")
current_lang = 'ru'


def tr(key):
    return LANGUAGES.get(current_lang, LANGUAGES['ru']).get(key, key)


class PowerControlApp:
    def __init__(self):
        global current_lang
        self.settings = self.load_settings()
        current_lang = self.settings.get('language', 'ru')

        self.indicator = AppIndicator3.Indicator.new(
            "work_control",
            "",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        icon_path = os.path.join(os.path.dirname(__file__), "logo.png")
        self.indicator.set_icon_full(icon_path, "Work Control")
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        self.scheduled_action = None
        self.remaining_seconds = 0
        self._update_timer_id = None
        self._notify_timer_id = None
        self._action_timer_id = None

        self.indicator.set_menu(self._create_menu())

    def load_settings(self):
        default = {'language': 'ru'}
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
                default.update(saved)
        except Exception:
            pass
        return default

    def save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print("Ошибка при сохранении настроек:", e)

    def _create_menu(self):
        menu = Gtk.Menu()
        # Основные пункты
        items = [
            (tr('power_off'), self._confirm_action, self._shutdown, tr('confirm_text_power_off')),
            (tr('reboot'), self._confirm_action, self._reboot, tr('confirm_text_reboot')),
            (tr('lock'), self._confirm_action, self._lock_screen, tr('confirm_text_lock')),
            (tr('settings'), self._open_settings, None, None),
        ]

        for label, callback, action, message in items:
            item = Gtk.MenuItem(label=label)
            item.connect("activate", callback, action, message)
            menu.append(item)

        # Разделитель
        menu.append(Gtk.SeparatorMenuItem())

        # Подменю выбора языка
        lang_menu = Gtk.Menu()
        for code in ['ru', 'en', 'cn', 'de']:
            lang_item = Gtk.RadioMenuItem.new_with_label_from_widget(
                None, LANGUAGES[code]['language_name']
            )
            lang_item.set_active(code == current_lang)
            lang_item.connect("activate", self._on_language_selected, code)
            lang_menu.append(lang_item)

        language_menu_item = Gtk.MenuItem(label=tr('language'))
        language_menu_item.set_submenu(lang_menu)
        menu.append(language_menu_item)

        # Разделитель
        menu.append(Gtk.SeparatorMenuItem())

        # Выход
        exit_item = Gtk.MenuItem(label=tr('exit_app'))
        exit_item.connect("activate", self._quit, None, None)
        menu.append(exit_item)

        menu.show_all()
        return menu

    def _on_language_selected(self, widget, lang_code):
        global current_lang
        if widget.get_active():
            if current_lang != lang_code:
                current_lang = lang_code
                self.settings['language'] = current_lang
                self.save_settings()
                self.indicator.set_menu(self._create_menu())

    def _confirm_action(self, widget, action_callback, message):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=message or tr('confirm_title')
        )
        dialog.set_title(tr('confirm_title'))
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and action_callback:
            action_callback()

    def _open_settings(self, *_):
        dialog = Gtk.Dialog(title=tr('settings'), flags=0)
        content = dialog.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=6)
        content.add(box)

        # Ввод времени
        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_label = Gtk.Label(label=tr('minutes'))
        time_label.set_xalign(0)
        adjustment = Gtk.Adjustment(value=1, lower=1, upper=1440, step_increment=1)
        time_spin = Gtk.SpinButton()
        time_spin.set_adjustment(adjustment)
        time_spin.set_numeric(True)
        time_spin.set_value(1)
        time_spin.set_size_request(150, -1)
        time_box.pack_start(time_label, True, True, 0)
        time_box.pack_start(time_spin, False, False, 0)

        # Выбор действия
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        action_label = Gtk.Label(label=tr('action'))
        action_label.set_xalign(0)
        action_combo = Gtk.ComboBoxText()
        action_combo.append_text(tr('power_off'))
        action_combo.append_text(tr('reboot'))
        action_combo.append_text(tr('lock'))
        action_combo.set_active(0)
        action_combo.set_size_request(150, -1)
        action_box.pack_start(action_label, True, True, 0)
        action_box.pack_start(action_combo, False, False, 0)

        # Кнопки
        apply_button = Gtk.Button(label=tr('apply'))
        cancel_button = Gtk.Button(label=tr('cancel'))
        reset_button = Gtk.Button(label=tr('reset'))

        apply_button.connect("clicked", lambda *_: dialog.response(Gtk.ResponseType.OK))
        cancel_button.connect("clicked", lambda *_: dialog.response(Gtk.ResponseType.CANCEL))

        def on_reset_clicked(*_):
            time_spin.set_value(1)
            action_combo.set_active(0)
            self._reset_action_button()

        reset_button.connect("clicked", on_reset_clicked)

        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
        button_box.set_halign(Gtk.Align.END)
        button_box.pack_start(reset_button, False, False, 0)
        button_box.pack_start(cancel_button, False, False, 0)
        button_box.pack_start(apply_button, False, False, 0)

        box.pack_start(time_box, False, False, 0)
        box.pack_start(action_box, False, False, 0)
        box.pack_start(button_box, False, False, 0)

        dialog.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            minutes = time_spin.get_value_as_int()
            action = action_combo.get_active_text()

            if minutes <= 0:
                self._show_message(tr('error'), tr('error_minutes_positive'))
                dialog.destroy()
                return

            self.scheduled_action = action
            self.remaining_seconds = minutes * 60

            if minutes > 1:
                self._notify_timer_id = GLib.timeout_add_seconds((minutes - 1) * 60, self._notify_before_action, action)
            self._action_timer_id = GLib.timeout_add_seconds(self.remaining_seconds, self._delayed_action, action)

            if self._update_timer_id:
                GLib.source_remove(self._update_timer_id)
            self._update_timer_id = GLib.timeout_add_seconds(1, self._update_indicator_label)

            self._show_message(tr('scheduled'), tr('action_in_time').format(action, minutes))

        dialog.destroy()

    def _reset_action_button(self, *_):
        if self._update_timer_id:
            GLib.source_remove(self._update_timer_id)
            self._update_timer_id = None

        if self._notify_timer_id:
            GLib.source_remove(self._notify_timer_id)
            self._notify_timer_id = None

        if self._action_timer_id:
            GLib.source_remove(self._action_timer_id)
            self._action_timer_id = None

        self.scheduled_action = None
        self.remaining_seconds = 0
        self.indicator.set_label("", "")
        self._show_message(tr('cancelled'), tr('cancelled_text'))

    def _notify_before_action(self, action):
        self._notify_timer_id = None
        self._show_message(tr('notification'), tr('action_in_1_min').format(action))
        return False

    def _update_indicator_label(self):
        if self.remaining_seconds <= 0:
            self.indicator.set_label("", "")
            return False
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        label = f"  {self.scheduled_action} {tr('action')} {hours:02d}:{minutes:02d}:{seconds:02d}"
        self.indicator.set_label(label, "")
        self.remaining_seconds -= 1
        return True

    def _delayed_action(self, action):
        self._action_timer_id = None
        self.indicator.set_label("", "")
        self.scheduled_action = None
        self.remaining_seconds = 0
        if self._update_timer_id:
            GLib.source_remove(self._update_timer_id)
            self._update_timer_id = None

        if action == tr('power_off'):
            self._shutdown()
        elif action == tr('reboot'):
            self._reboot()
        elif action == tr('lock'):
            self._lock_screen()
        return False

    def _show_message(self, title, message):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.set_title(title)
        dialog.run()
        dialog.destroy()

    def _shutdown(self):
        os.system("systemctl poweroff")

    def _reboot(self):
        os.system("systemctl reboot")

    def _lock_screen(self):
        os.system("loginctl lock-session")

    def _quit(self, *_):
        Gtk.main_quit()

    def run(self):
        Gtk.main()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = PowerControlApp()
    app.run()
