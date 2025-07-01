"""Модуль для обработки изображений."""
import cv2
import numpy as np


class ImageProcessor:
    """Класс для обработки изображений."""

    @staticmethod
    def load_image(file_path):
        """Загружает изображение из файла."""
        img = cv2.imread(file_path)
        if img is None:
            raise ValueError("Не удалось загрузить изображение!")
        return img

    @staticmethod
    def capture_webcam():
        """Делает снимок с веб-камеры."""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise ValueError("Камера не подключена!")
        ret, frame = cap.read()
        cap.release()
        if not ret:
            raise ValueError("Не удалось получить кадр!")
        return frame

    @staticmethod
    def get_channel(img, channel):
        """Возвращает красный, зелёный или синий канал."""
        b, g, r = cv2.split(img)
        zeros = np.zeros_like(b)
        if channel == 'R':
            return cv2.merge([zeros, zeros, r])
        if channel == 'G':
            return cv2.merge([zeros, g, zeros])
        if channel == 'B':
            return cv2.merge([b, zeros, zeros])
        raise ValueError("Неверный канал. Допустимо: R, G, B")

    @staticmethod
    def crop(img, x1, y1, x2, y2):
        """Обрезает изображение по координатам."""
        return img[y1:y2, x1:x2]

    @staticmethod
    def adjust_brightness(img, value):
        """Увеличивает яркость на value."""
        return cv2.add(img, np.array([value], dtype=np.uint8))

    @staticmethod
    def draw_line(img, x1, y1, x2, y2, thickness):
        """Рисует зелёную линию."""
        img_copy = img.copy()
        cv2.line(img_copy, (x1, y1), (x2, y2), (0, 255, 0), thickness)
        return img_copy
