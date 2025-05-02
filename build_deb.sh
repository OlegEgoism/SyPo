#!/bin/bash

# Переменные
APP_NAME="wor-sys"
VERSION="1.0"
BUILD_DIR="deb_build"
INSTALL_DIR="${BUILD_DIR}/${APP_NAME}/usr/local/bin/${APP_NAME}"
ICON_DIR="${BUILD_DIR}/${APP_NAME}/usr/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="${BUILD_DIR}/${APP_NAME}/usr/share/applications"

# Очистка старых сборок
rm -rf "$BUILD_DIR"
mkdir -p "$INSTALL_DIR"
mkdir -p "$ICON_DIR"
mkdir -p "$DESKTOP_DIR"

# Копируем файлы
cp app.py logo.png requirements.txt "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/app.py"

# Создаем DEBIAN/control
mkdir -p "${BUILD_DIR}/${APP_NAME}/DEBIAN"
cat > "${BUILD_DIR}/${APP_NAME}/DEBIAN/control" <<EOF
Package: ${APP_NAME}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: all
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-appindicator3-0.1, python3-psutil
Maintainer: You <olegpustovalov220@gmail.com>
Description: System tray monitor.
EOF

# Создаем .desktop файл
cat > "${DESKTOP_DIR}/${APP_NAME}.desktop" <<EOF
[Desktop Entry]
Name=SysMon
Exec=python3 /usr/local/bin/${APP_NAME}/app.py
Icon=${APP_NAME}
Type=Application
Categories=Utility;
EOF

# Копируем иконку
cp logo.png "${ICON_DIR}/${APP_NAME}.png"

# Создание .deb пакета
dpkg-deb --build "${BUILD_DIR}/${APP_NAME}"

# Удаление временных директорий после сборки
rm -rf "$BUILD_DIR"

echo "Deb package ${APP_NAME}-${VERSION}.deb created successfully!"
