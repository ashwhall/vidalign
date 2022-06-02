from PySide6 import QtWidgets, QtCore, QtGui
from vidalign.constants import COLOURS
from vidalign.widgets.modules import StyledButton


class EncodingProgressDialog(QtWidgets.QDialog):
    on_cancel_encode = QtCore.Signal()
    on_finalise_encoding = QtCore.Signal()

    def __init__(self, output_directory, percentage=None, stdout_lines=None):
        super().__init__()
        self.output_directory = output_directory

         # Display the commands in a dialog, one per line
        self.setWindowTitle(f'Encoding: starting...')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.resize(960, 600)
        self.layout = QtWidgets.QVBoxLayout()
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        # Black background, white foreground, monospace font
        self.text_edit.setStyleSheet(f'background-color: #101010; color: {COLOURS["white"]}; font-family: monospace;')
        self.layout.addWidget(self.text_edit)
        # Disallow closing
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.CustomizeWindowHint | QtCore.Qt.WindowTitleHint)

        # Cancel button
        cancel_btn_layout = QtWidgets.QHBoxLayout()
        cancel_btn = StyledButton('Cancel Encoding', StyledButton.Style.NEGATIVE)
        cancel_btn.clicked.connect(self.cancel_encode)
        cancel_btn_layout.addWidget(cancel_btn)
        self.cancel_btn_widget = QtWidgets.QWidget()
        self.cancel_btn_widget.setLayout(cancel_btn_layout)

        # Okay button
        okay_btn_layout = QtWidgets.QHBoxLayout()
        ok_btn = StyledButton('Cool beans', StyledButton.Style.PRIMARY)
        ok_btn.clicked.connect(self.finalise_encoding)
        okay_btn_layout.addWidget(ok_btn)

        open_dir_btn = StyledButton('Open output directory')
        open_dir_btn.clicked.connect(self.open_output_directory)
        okay_btn_layout.addWidget(open_dir_btn)
        
        self.okay_btn_widget = QtWidgets.QWidget()
        self.okay_btn_widget.setLayout(okay_btn_layout)

        self.set_values(percentage, stdout_lines)

        self.layout.addWidget(self.cancel_btn_widget)
        self.setLayout(self.layout)

    def set_values(self, percentage, stdout_lines):
        if percentage >= 1:
            self.setWindowTitle('Encoding complete!')
            # Remove the cancel button and replace with okay button
            if self.cancel_btn_widget:
                self.layout.removeWidget(self.cancel_btn_widget)
                self.cancel_btn_widget.deleteLater()
                self.cancel_btn_widget = None
            self.layout.addWidget(self.okay_btn_widget)
        else:
            self.setWindowTitle(f'Encoding: {100 * percentage:.1f}%')
            self.text_edit.setPlainText('\n'.join(stdout_lines))
            self.text_edit.moveCursor(QtGui.QTextCursor.End)

    # Disallow escape key close
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            event.ignore()
        else:
            super().keyPressEvent(event)

    @QtCore.Slot()
    def cancel_encode(self):
        self.on_cancel_encode.emit()
        self.close()

    @QtCore.Slot()
    def finalise_encoding(self):
        self.on_finalise_encoding.emit()
        self.close()

    @QtCore.Slot()
    def open_output_directory(self):
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(self.output_directory))