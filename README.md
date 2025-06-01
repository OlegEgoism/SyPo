- 🇧🇾 Приложение SyPo для управления питанием и выполнением системных действий в системном трее 🇧🇾
 
🧾 Основные функции:
- Ожидание и выполнение действий: выключение, перезагрузка, блокировка экрана.
- Установка и управление таймерами для выполнения действий через заданное время.
- Возможность настроить действие и время через диалоговое окно настроек.
- Всплывающие уведомления перед выполнением действия.
- Логирование всех действий и уведомлений.

🗣 Доступные языки интерфейса:
- Русский, 
- Английский, 
- Китайский, 
- Немецкий.

🎥 Видео-демо
[(https://img.youtube.com/vi/AVzxt623t2A/0.jpg)](https://www.youtube.com/watch?v=TDo2tV02jaE&ab)

---------------------------------------------------------------------------------
-  ЗАПУСК В РЕЖИМИ РАЗАРБОТКИ.

💡 Установка apt для Debian/Ubuntu (основные библиотеки).
```bash
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```
Если буду проблемы добавить
```bash
sudo apt update
sudo apt install python3.10-dev
sudo apt install pkg-config
sudo apt install libcairo2-dev
sudo apt install build-essential
pip install pygobject
```

💡 Python-зависимости.
```bash
pip install --upgrade pip
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

---------------------------------------------------------------------------------
- СБОРКА ПРИЛОЖЕНИЯ

💡 Сборка приложения в пакет (файлы и папки). В файле "build_deb.sh" вся структура проекта для сборки приложения!
```bash
chmod +x build_deb.sh
./build_deb.sh
dpkg-deb --build deb_build/SyPo deb_build/SyPo.deb
```

💡 Установка собранного пакета.
```bash
sudo dpkg -i deb_build/SyPo.deb
```

💡 Удалить пакет
```bash
sudo dpkg -r sypo
sudo apt --fix-broken install
```

💡 Убедится, что пакет удален
```bash
dpkg -l | grep sypo
```

---------------------------------------------------------------------------------
- ОБРАТНАЯ СВЯЗЬ

- Почта: olegpustovalov220@gmail.com 
- Телеграмм: @OlegEgoism

