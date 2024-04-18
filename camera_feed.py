import sys
from PySide6 import QtWidgets
from PySide6.QtCore import Qt, QThread, Signal, Slot
from PySide6.QtGui import QImage, QTransform
from PySide6.QtGui import QIcon, QPixmap, QImage
from PySide6.QtMultimedia import QMediaDevices
import cv2

class MyWidget(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		
		self.setWindowTitle("ROV GUI")
		self.layout = QtWidgets.QGridLayout(self)
		self.availableCameras = []
		self.getAvailableCameras()
		self.th = Thread(self)
		self.th.finished.connect(self.close)
		self.th.updateFrame.connect(self.setImage)
		
		self.label = QtWidgets.QLabel(self)
		self.label.id_number = 1;
		self.label.setStyleSheet(u"background-color: black;")
		self.layout.addWidget(self.label, 1, 0)

		self.combobox = QtWidgets.QComboBox(self)
		self.combobox.id_number = 1
		self.combobox.addItem("Select--")
		self.combobox.addItems(self.availableCameras)
		self.layout.addWidget(self.combobox, 1, 1)
		self.combobox.currentIndexChanged.connect(self.runWebCam)

	@Slot(QImage)
	def runWebCam(self, indx):
		self.indx = 1
		combo = self.sender()
		print(f"Selected the variable {self.label.id_number} from combo {combo.id_number}")
		self.th.start()

	@Slot(QImage)
	def setImage(self, image):
		image_inv = QImage(image)
		myTransform = QTransform()
		myTransform.rotate(180)
		image_inv = image_inv.transformed(myTransform) 
		self.label.setPixmap(QPixmap.fromImage(image_inv))
		
	def getAvailableCameras(self):
		cameras = QMediaDevices.videoInputs()
		for cameraDevice in cameras:
			self.availableCameras.append(cameraDevice.description())

class Thread(QThread):
	updateFrame = Signal(QImage)
	def __init__(self, parent=None):
		QThread.__init__(self, parent)
		self.status = True
		self.cap = True

	def run(self):
		self.cap = cv2.VideoCapture(0)
		while self.status:
			ret, frame = self.cap.read()
			if not ret:
				continue
			h, w, ch = frame.shape
			img = QImage(frame.data, w, h, ch * w, QImage.Format_RGB888)
			scaled_img = img.scaled(640, 480, Qt.KeepAspectRatio)
			# Emit signal
			self.updateFrame.emit(scaled_img)
		sys.exit(-1)

if __name__ == "__main__":
	app = QtWidgets.QApplication([])
	
	widget = MyWidget()
	widget.resize(800, 600)
	widget.show()

	sys.exit(app.exec())
