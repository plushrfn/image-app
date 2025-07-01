"""Главное окно приложения для редактирования изображений."""
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QWidget, QFileDialog, QMessageBox, QInputDialog, QHBoxLayout
)
import cv2
from processor.image_processor import ImageProcessor


class MainWindow(QMainWindow):
    """Класс главного окна приложения."""

    def __init__(self):
        """Инициализирует главное окно."""
        super().__init__()
        self.setWindowTitle("Редактор изображений")
        self.setFixedSize(600, 600)
        # Обработчик изображений
        self.processor = ImageProcessor()
        self.current_image = None
        self.original_image = None

        # Виджеты
        self.label = QLabel("Здесь будет изображение")
        self.label.setFixedSize(600, 400)
        self.btn_load = QPushButton("Загрузить фото")
        self.btn_camera = QPushButton("Сделать снимок")
        self.btn_channel = QPushButton("Показать канал (R/G/B)")
        self.btn_reset_channel = QPushButton("Сбросить канал")
        self.btn_crop = QPushButton("Обрезать")
        self.btn_brightness = QPushButton("Увеличить яркость")
        self.btn_line = QPushButton("Нарисовать линию")

        # Горизонтальный layout для кнопок канала
        channel_layout = QHBoxLayout()
        channel_layout.addWidget(self.btn_channel)
        channel_layout.addWidget(self.btn_reset_channel)

        # Размещение
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.btn_load)
        layout.addWidget(self.btn_camera)
        layout.addLayout(channel_layout)
        layout.addWidget(self.btn_crop)
        layout.addWidget(self.btn_brightness)
        layout.addWidget(self.btn_line)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Подключение кнопок
        self.btn_load.clicked.connect(self.load_image)
        self.btn_camera.clicked.connect(self.capture_image)
        self.btn_channel.clicked.connect(self.show_channel)
        self.btn_reset_channel.clicked.connect(self.reset_channel)
        self.btn_crop.clicked.connect(self.crop_image)
        self.btn_brightness.clicked.connect(self.adjust_brightness)
        self.btn_line.clicked.connect(self.draw_line)

    def load_image(self):
        """Загружает изображение из файла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите фото", "", "Images (*.png *.jpg)")
        if file_path:
            try:
                self.current_image = self.processor.load_image(file_path)
                self.original_image = self.current_image
                self.display_image(self.current_image)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def capture_image(self):
        """Захватывает фото с камеры."""
        try:
            self.current_image = self.processor.capture_webcam()
            self.original_image = self.current_image
            self.display_image(self.current_image)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def show_channel(self):
        """Показывает выбранный канал (R, G, B)."""
        if self.current_image is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала загрузите изображение!")
            return
        channel, ok = QInputDialog.getItem(
            self, "Выбор канала", "Канал:", ["R", "G", "B"], 0, False
        )
        if ok and channel:
            try:
                channel_img = self.processor.get_channel(
                    self.current_image, channel)
                self.display_image(channel_img)
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def reset_channel(self):
        """Возвращает исходное изображение после отображения канала."""
        if self.original_image is not None:
            self.current_image = self.original_image
            self.display_image(self.current_image)
        else:
            QMessageBox.warning(self, "Ошибка",
                                "Сначала загрузите изображение!")

    def display_image(self, img):
        """Отображает изображение."""
        # Конвертируем цвет из BGR в RGB
        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Создаем QImage
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_img = QImage(
            rgb_image.data,
            w,
            h,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )
        # Конвертируем в QPixmap и масштабируем
        pixmap = QPixmap.fromImage(q_img)
        label_size = self.label.size()
        scaled_pixmap = pixmap.scaled(
            label_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )

        self.label.setPixmap(scaled_pixmap)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def crop_image(self):
        """Обрезает изображение с обработкой координат."""
        if self.current_image is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала загрузите изображение!")
            return
        h, w = self.current_image.shape[:2]
        # Диалог для ввода координат (Y вводится от нижнего края)
        x1, ok1 = QInputDialog.getInt(
            self, "Обрезка", "X1 (начало):", 0, 0, w-1)
        y1_bottom, ok2 = QInputDialog.getInt(
            self, "Обрезка", "Y1 (начало):", 0, 0, h-1)
        x2, ok3 = QInputDialog.getInt(
            self, "Обрезка", "X2 (конец):", w-1, x1+1, w-1)
        y2_bottom, ok4 = QInputDialog.getInt(
            self, "Обрезка", "Y2 (конец):", h-1, y1_bottom+1, h-1)

        if not (ok1 and ok2 and ok3 and ok4):
            return
        # Преобразуем Y-координаты
        y1 = h - y1_bottom - 1
        y2 = h - y2_bottom - 1
        try:
            # Обрезаем
            cropped_img = self.current_image[y2:y1, x1:x2]
            self.current_image = cropped_img
            self.original_image = cropped_img
            self.display_image(self.current_image)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка обрезки: {str(e)}")

    def adjust_brightness(self):
        """Изменяет яркость с проверкой значения."""
        if self.current_image is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала загрузите изображение!")
            return
        value, ok = QInputDialog.getInt(
            self, "Яркость", "Значение (0-100):", 10, 0, 100
        )
        if not ok:
            return
        try:
            bright_image = self.processor.adjust_brightness(
                self.current_image, value)
            self.current_image = bright_image
            self.original_image = bright_image
            self.display_image(self.current_image)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка яркости: {e}")

    def draw_line(self):
        """Рисует линию с обработкой координат."""
        if self.current_image is None:
            QMessageBox.warning(
                self, "Ошибка", "Сначала загрузите изображение!")
            return
        h, w = self.current_image.shape[:2]
        # Диалоги для ввода (Y вводится от нижнего края)
        x1, ok1 = QInputDialog.getInt(self, "Линия", "X1:", 0, 0, w-1)
        y1_bottom, ok2 = QInputDialog.getInt(
            self, "Линия", "Y1:", 0, 0, h-1)
        x2, ok3 = QInputDialog.getInt(self, "Линия", "X2:", w-1, 0, w-1)
        y2_bottom, ok4 = QInputDialog.getInt(
            self, "Линия", "Y2:", h-1, 0, h-1)
        thickness, ok5 = QInputDialog.getInt(
            self, "Линия", "Толщина:", 2, 1, 10)
        if not (ok1 and ok2 and ok3 and ok4 and ok5):
            return
        # Преобразуем Y-координаты (из нижнего угла в верхний)
        y1 = h - y1_bottom - 1
        y2 = h - y2_bottom - 1
        try:
            line_image = self.processor.draw_line(
                self.current_image, x1, y1, x2, y2, thickness)
            self.current_image = line_image
            self.original_image = line_image
            self.display_image(self.current_image)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка рисования: {e}")
