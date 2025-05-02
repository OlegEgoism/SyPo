🔌 WOR_SYS
- 🇧🇾 Приложение для управления питанием и выполнением системных действий в системном трее 🇧🇾
 
🧾 Основные функции:
- Ожидание и выполнение действий: выключение, перезагрузка, блокировка экрана.
- Установка и управление таймерами для выполнения действий через заданное время.
- Возможность настроить действие и время через диалоговое окно настроек.
- Всплывающие уведомления перед выполнением действия.
- Логирование всех действий и уведомлений.

🎥 Видео-демо
Посмотрите, как OFF_RES работает на практике:
[![OFF_RES Видео-демо](https://img.youtube.com/vi/AVzxt623t2A/0.jpg)](https://www.youtube.com/watch?v=TDo2tV02jaE&ab)

-  ЗАПУСК В РЕЖИМИ РАЗАРБОТКИ.

💡 Установка apt для Debian/Ubuntu (основные библиотеки).
```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```
💡 Python-зависимости.
```bash
pip install -r requirements.txt
```

💡 Дополнительно (для GNOME Shell).
```bash
sudo apt install gnome-shell-extension-appindicator
```

💡 Запуск
```bash
python3 app.py
```

-  СБОРКА ПРИЛОЖЕНИЯ КАК УСТАНОВОЧНЫЙ ПАКЕТ.

💡 Запуск как пакет приложения
```bash
chmod +x build_deb.sh
./build_deb.sh
sudo dpkg -i deb_build/wor-sys.deb
```
💡 Сделай исполняемым:
```bash
chmod +x build_deb.sh
```

💡 Запуск
```bash
./build_deb.sh
```

💡 Установи пакет
```bash
sudo dpkg -i deb_build/wor-sys.deb
```

По вопросам писать на почту 📨: olegpustovalov220@gmail.com 