from PyQt5 import QtCore, QtGui, QtWidgets
import speech_recognition as sr
import sys
import os
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QWidget

class WorkerThread(QtCore.QThread):
    update_signal = QtCore.pyqtSignal(str)  

    def __init__(self):
        super().__init__()
        self.audio_source = sr.Microphone()
        self.recognizer = sr.Recognizer()
        self.recording = False

    def run(self):
        with self.audio_source as source:
            while True:
                if self.isInterruptionRequested():
                    break
                if self.recording:
                    try:
                        audio = self.recognizer.listen(source, timeout=5)
                        text = self.recognizer.recognize_google(audio, language="tr-TR")
                        self.update_signal.emit(text)
                    except sr.WaitTimeoutError:
                        pass
                    except sr.UnknownValueError:
                        self.update_signal.emit("Ses anlaşılamadı")
                    except sr.RequestError as e:
                        self.update_signal.emit(f"Sesli komut servisine erişilemiyor: {str(e)}")

class Ui_Form(QWidget):
    def setupUi(self, Form):
        self.Form = Form
        self.worker_thread = WorkerThread()
        self.worker_thread.update_signal.connect(self.update_text)

        self.pushButton_start = QtWidgets.QPushButton(Form)
        self.pushButton_start.setGeometry(QtCore.QRect(10, 270, 211, 101))
        self.pushButton_start.setObjectName("Kayıt Başlat")
        self.pushButton_start.clicked.connect(self.start_recording)

        self.pushButton_stop = QtWidgets.QPushButton(Form)
        self.pushButton_stop.setGeometry(QtCore.QRect(230, 270, 211, 101))
        self.pushButton_stop.setObjectName("Kaydı Durdur")
        self.pushButton_stop.clicked.connect(self.stop_recording)
        self.pushButton_stop.setEnabled(False)

        self.pushButton_save = QtWidgets.QPushButton(Form)
        self.pushButton_save.setGeometry(QtCore.QRect(10, 370, 211, 101))
        self.pushButton_save.setObjectName("Metni Kaydet")
        self.pushButton_save.clicked.connect(self.metin_kaydet)

        self.pushButton_clear = QtWidgets.QPushButton(Form)
        self.pushButton_clear.setGeometry(QtCore.QRect(820, 300, 121, 41))
        self.pushButton_clear.setObjectName("Temizle")
        self.pushButton_clear.clicked.connect(self.temizle)

        Form.setObjectName("Form")
        Form.resize(956, 478)
        self.textEdit = QtWidgets.QTextEdit(Form)
        self.textEdit.setGeometry(QtCore.QRect(15, 35, 931, 231))
        self.textEdit.setObjectName("Metin")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def temizle(self):
        self.textEdit.clear()

    def metin_kaydet(self):
        dosya_ismi = QFileDialog.getSaveFileName(self, "Metni Kaydet", os.getenv("HOME"))

        if dosya_ismi[0]:
            with open(dosya_ismi[0], "w") as file:
                file.write(self.textEdit.toPlainText())

    def start_recording(self):
        self.worker_thread.recording = True
        self.pushButton_start.setEnabled(False)
        self.pushButton_stop.setEnabled(True)
        self.worker_thread.start()

    def stop_recording(self):
        self.worker_thread.recording = False
        self.pushButton_start.setEnabled(True)
        self.pushButton_stop.setEnabled(False)
        self.worker_thread.terminate()

    def update_text(self, text):
        self.textEdit.append(text)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "SES METİN ÇEVİRİCİ"))
        self.pushButton_start.setText(_translate("Form", "Kayıt Başlat"))
        self.pushButton_stop.setText(_translate("Form", "Kaydı Durdur"))
        self.pushButton_save.setText(_translate("Form", "Metni Kaydet"))
        self.pushButton_clear.setText(_translate("Form", "Temizle"))

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
