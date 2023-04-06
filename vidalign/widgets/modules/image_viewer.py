# Thanks to https://stackoverflow.com/a/35514531/5270944

from typing import Optional
from PySide6 import QtCore, QtGui, QtWidgets

from vidalign.utils.video import Box


class ImageViewer(QtWidgets.QGraphicsView):
    cropUpdated = QtCore.Signal(Box)

    def __init__(self):
        super().__init__()
        self._zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._crop_box = QtWidgets.QGraphicsRectItem()
        self._scene.addItem(self._photo)
        self._prevMousePos = None
        self._clickRecipient = None
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def has_image(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_image():
                unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                viewrect = self.viewport().rect()
                scenerect = self.transform().mapRect(rect)
                factor = min(viewrect.width() / scenerect.width(),
                             viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def set_image(self, pixmap=None, reset=False):
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())
        if reset:
            self._zoom = 0
            self.fitInView()

    def set_crop_box(self, crop_box: Optional[Box], interpolated: bool = False):
        if crop_box is not None:
            self._crop_box.setRect(*crop_box.xywh)

            # Show an outline if the crop isn't full frame
            if crop_box.xywh != [0, 0, self._photo.pixmap().width(), self._photo.pixmap().height()]:
                colour = QtGui.QColor(255, 255, 0) if interpolated else QtGui.QColor(255, 0, 0)
                self._crop_box.setPen(QtGui.QPen(colour, 4))
            else:
                self._crop_box.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0, 0), 0))
            # Only add if it's not already there
            if self._crop_box not in self._scene.items():
                self._scene.addItem(self._crop_box)
        else:
            self._scene.removeItem(self._crop_box)

    def adjust_crop_box(self, new_rect: Optional[QtCore.QRectF]):
        if new_rect is None:
            self.cropUpdated.emit(None)
            return

        # Ensure the crop box is within the image
        image_rect = self._photo.pixmap().rect()
        new_rect = new_rect.intersected(image_rect)
        # Ensure it's at least 100x100, retaining the center
        centre = new_rect.center()
        if new_rect.width() < 100:
            new_rect.setWidth(100)
            new_rect.moveCenter(centre)
        if new_rect.height() < 100:
            new_rect.setHeight(100)
            new_rect.moveCenter(centre)

        # Move box to nearest integer location and ensure that its
        # width and height are multiples of 2
        coords = [int(round(x)) for x in new_rect.getCoords()]
        if (coords[2] - coords[0]) % 2 != 0:
            coords[2] += 1
        if (coords[3] - coords[1]) % 2 != 0:
            coords[3] += 1

        self.cropUpdated.emit(Box(*coords))

    def wheelEvent(self, event):
        if not self.has_image():
            return

        ctrl_held = event.modifiers() == QtCore.Qt.ControlModifier
        ctrl_shift_held = event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier)

        if ctrl_held or ctrl_shift_held:
            # Shift held?
            sign = 1 if event.angleDelta().y() > 0 else -1
            change_px = sign * 10
            new_rect = self._crop_box.rect()
            centre = new_rect.center()

            if ctrl_held:
                new_rect.setWidth(new_rect.width() + change_px)
            elif ctrl_shift_held:
                new_rect.setHeight(new_rect.height() + change_px)
            new_rect.moveCenter(centre)
            self.adjust_crop_box(new_rect)
        else:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QtWidgets.QGraphicsView.ScrollHandDrag:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

    def mousePressEvent(self, event):
        if not self.has_image():
            return

        pos = self.mapToScene(event.pos())
        if event.buttons() == QtCore.Qt.LeftButton:
            self._prevMousePos = pos
            self._clickRecipient = None
            if self._crop_box.isUnderMouse() and event.modifiers() == QtCore.Qt.ControlModifier:
                self._clickRecipient = self._crop_box
            elif self._photo.isUnderMouse():
                self._clickRecipient = self._photo
                super(ImageViewer, self).mousePressEvent(event)
        else:
            self.adjust_crop_box(None)

    def mouseMoveEvent(self, event):
        if not self.has_image():
            return

        pos = self.mapToScene(event.pos())
        if self._clickRecipient == self._crop_box:
            if event.buttons() == QtCore.Qt.LeftButton:
                if self._prevMousePos is not None:
                    delta = pos - self._prevMousePos
                    rect = self._crop_box.rect()
                    rect.translate(delta.x(), delta.y())
                    self.adjust_crop_box(rect)
        else:
            super(ImageViewer, self).mouseMoveEvent(event)
        if self._clickRecipient is not None:
            self._prevMousePos = pos

    def mouseReleaseEvent(self, event):
        if not self.has_image():
            return

        self._prevMousePos = None
        self._clickRecipient = None
        super(ImageViewer, self).mouseReleaseEvent(event)
