import gi
import os
import signal

gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')

from gi.repository import Gtk, AppIndicator3, GLib

POWER_OFF_LABEL = "Выключение"
REBOOT_LABEL = "Перезагрузка"
LOCK_LABEL = "Блокировка"
SETTINGS_LABEL = "Настройки"
EXIT_APP_LABEL = "Выход"


class PowerControlApp:
    def __init__(self):
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

    def _create_menu(self):
        menu = Gtk.Menu()
        items = [
            (POWER_OFF_LABEL, self._confirm_action, self._shutdown, f"{POWER_OFF_LABEL}?"),
            (REBOOT_LABEL, self._confirm_action, self._reboot, f"{REBOOT_LABEL}?"),
            (LOCK_LABEL, self._confirm_action, self._lock_screen, f"{LOCK_LABEL}?"),
            (SETTINGS_LABEL, self._open_settings, None, None),
            (None, None, None, None),
            (EXIT_APP_LABEL, self._quit, None, None),
        ]
        for label, callback, action, message in items:
            if label is None:
                menu.append(Gtk.SeparatorMenuItem())
            else:
                item = Gtk.MenuItem(label=label)
                item.connect("activate", callback, action, message)
                menu.append(item)
        menu.show_all()
        return menu

    def _confirm_action(self, widget, action_callback, message):
        dialog = Gtk.MessageDialog(
            transient_for=None,
            flags=0,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.OK_CANCEL,
            text=message or "Выполнить это действие?"
        )
        dialog.set_title("Подтверждение действия")
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.OK and action_callback:
            action_callback()

    def _open_settings(self, *_):
        dialog = Gtk.Dialog(title="Настройки", flags=0)
        content = dialog.get_content_area()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6, margin=6)
        content.add(box)

        # Ввод времени
        time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        time_label = Gtk.Label(label="Минуты:")
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
        action_label = Gtk.Label(label="Действие:")
        action_label.set_xalign(0)
        action_combo = Gtk.ComboBoxText()
        action_combo.append_text(POWER_OFF_LABEL)
        action_combo.append_text(REBOOT_LABEL)
        action_combo.append_text(LOCK_LABEL)
        action_combo.set_active(0)
        action_combo.set_size_request(150, -1)
        action_box.pack_start(action_label, True, True, 0)
        action_box.pack_start(action_combo, False, False, 0)

        # Кнопки
        apply_button = Gtk.Button(label="Применить")
        cancel_button = Gtk.Button(label="Отмена")
        reset_button = Gtk.Button(label="Сбросить")

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
                self._show_message("Ошибка", "Введите значение больше 0.")
                dialog.destroy()
                return

            self.scheduled_action = action
            self.remaining_seconds = minutes * 60

            # ✅ Сохраняем ID таймеров
            if minutes > 1:
                self._notify_timer_id = GLib.timeout_add_seconds((minutes - 1) * 60, self._notify_before_action, action)
            self._action_timer_id = GLib.timeout_add_seconds(self.remaining_seconds, self._delayed_action, action)

            if self._update_timer_id:
                GLib.source_remove(self._update_timer_id)
            self._update_timer_id = GLib.timeout_add_seconds(1, self._update_indicator_label)

            self._show_message("Запланировано", f"{action} через {minutes} минут.")

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
        self._show_message("Отменено", "Запланированное действие сброшено.")

    def _notify_before_action(self, action):
        self._notify_timer_id = None
        self._show_message("Предупреждение", f"{action} через 1 минуту.")
        return False  # таймер удаляется

    def _update_indicator_label(self):
        if self.remaining_seconds <= 0:
            self.indicator.set_label("", "")
            return False
        hours = self.remaining_seconds // 3600
        minutes = (self.remaining_seconds % 3600) // 60
        seconds = self.remaining_seconds % 60
        label = f"  {self.scheduled_action} через: {hours:02d}:{minutes:02d}:{seconds:02d}"
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

        if action == POWER_OFF_LABEL:
            self._shutdown()
        elif action == REBOOT_LABEL:
            self._reboot()
        elif action == LOCK_LABEL:
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
