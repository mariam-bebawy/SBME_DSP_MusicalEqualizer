# import sounddevice as sd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
# import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, uic
from PyQt5.QtWidgets import QFileDialog
from pydub import AudioSegment
from PyQt5.Qt import Qt
import vlc
import os
# import logo_rc
# from numpy.fft import fft
# from numpy.lib import real
import numpy as np
import sys
from scipy.io import wavfile
import matplotlib
matplotlib.use('Qt5Agg')
from music21 import *
from music21.stream import Stream

import logging

# DEBUG: Detailed information, typically of interest only when diagnosing problems.

# INFO: Confirmation that things are working as expected.

# WARNING: An indication that something unexpected happened, or indicative of some problem in the near future (e.g. ‘disk space low’). The software is still working as expected.

# ERROR: Due to a more serious problem, the software has not been able to perform some function.

# CRITICAL: A serious error, indicating that the program itself may be unable to continue running.

logging.basicConfig(
    level = logging.INFO,
    # logging.DEBUG floods the log file with unnecessary data that has to do with pyqt5
    # instead we opt for logging.INFO to display our needed logging messages
    format = "{asctime} {levelname:<8} {message}",  # level formatting
    style = '{',
    filename = '%slog' % __file__[:-2],  # log file name
    filemode = 'w'  # overwite log file instead of append
)

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        uic.loadUi(r'finaltask3tamer.ui', self)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(200)

        self.xMin = 0
        self.xMax = 1
        self.changed = False
        self.recordedData = []
        # button connections
        self.openFileButton.clicked.connect(lambda: self.open())
        self.playButton.clicked.connect(lambda: self.playMusic())
        self.pianoButton.toggled.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.xylophoneButton.toggled.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.BongosButton.toggled.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        # Slider connections
        self.doubleBass.valueChanged.connect(lambda: self.play())
        self.bass.valueChanged.connect(lambda: self.play())
        self.trumpet.valueChanged.connect(lambda: self.play())
        self.Piano.valueChanged.connect(lambda: self.play())
        self.electronic.valueChanged.connect(lambda: self.play())
        self.volumeSlider.valueChanged.connect(lambda: self.volumeControl())

        self.spectroCanvas = MplCanvas(
            self.specPlot,  width=5, height=4, dpi=100)
        self.specLayout = QtWidgets.QVBoxLayout()
        self.specLayout.addWidget(self.spectroCanvas)
        self.originalCanvas = MplCanvas(
            self.signalPlot,  width=5.5, height=4.5, dpi=90)
        self.originalLayout = QtWidgets.QVBoxLayout()
        self.originalLayout.addWidget(self.originalCanvas)

        self.graph = pg.PlotItem()
        pg.PlotItem.hideAxis(self.graph, 'left')
        pg.PlotItem.hideAxis(self.graph, 'bottom')

# piano connections
        self.c.setShortcut('q')
        self.csharp.setShortcut('a')
        self.d.setShortcut('w')
        self.dsharp.setShortcut('s')
        self.e.setShortcut('e')
        self.f.setShortcut('r')
        self.fsharp.setShortcut('d')
        self.g.setShortcut('t')
        self.gsharp.setShortcut('f')
        self.a.setShortcut('y')
        self.asharp.setShortcut('g')
        self.b.setShortcut('u')
        self.c.clicked.connect(lambda: self.PianoEvents('c'))
        self.csharp.clicked.connect(lambda: self.PianoEvents('c#'))
        self.d.clicked.connect(lambda: self.PianoEvents('d'))
        self.dsharp.clicked.connect(lambda: self.PianoEvents('d#'))
        self.e.clicked.connect(lambda: self.PianoEvents('e'))
        self.f.clicked.connect(lambda: self.PianoEvents('f'))
        self.fsharp.clicked.connect(lambda: self.PianoEvents('f#'))
        self.g.clicked.connect(lambda: self.PianoEvents('g'))
        self.gsharp.clicked.connect(lambda: self.PianoEvents('g#'))
        self.a.clicked.connect(lambda: self.PianoEvents('a'))
        self.asharp.clicked.connect(lambda: self.PianoEvents('a#'))
        self.b.clicked.connect(lambda: self.PianoEvents('b'))

# xylophone connections
        self.c1.setShortcut('q')
        self.d1.setShortcut('w')
        self.e1.setShortcut('e')
        self.f1.setShortcut('r')
        self.g1.setShortcut('t')
        self.a1.setShortcut('y')
        self.b1.setShortcut('u')
        self.c2.setShortcut('i')
        self.d2.setShortcut('o')
        self.f2.setShortcut('p')
        self.g2.setShortcut('a')
        self.a2.setShortcut('s')
        self.b2.setShortcut('d')
        self.c3.setShortcut('f')
        self.c1.clicked.connect(lambda: self.xylophoneEvents('c1'))
        self.d1.clicked.connect(lambda: self.xylophoneEvents('d1'))
        self.e1.clicked.connect(lambda: self.xylophoneEvents('e1'))
        self.f1.clicked.connect(lambda: self.xylophoneEvents('f1'))
        self.g1.clicked.connect(lambda: self.xylophoneEvents('g1'))
        self.a1.clicked.connect(lambda: self.xylophoneEvents('a1'))
        self.b1.clicked.connect(lambda: self.xylophoneEvents('b1'))
        self.c2.clicked.connect(lambda: self.xylophoneEvents('c2'))
        self.d2.clicked.connect(lambda: self.xylophoneEvents('d2'))
        self.f2.clicked.connect(lambda: self.xylophoneEvents('f2'))
        self.g2.clicked.connect(lambda: self.xylophoneEvents('g2'))
        self.a2.clicked.connect(lambda: self.xylophoneEvents('a2'))
        self.b2.clicked.connect(lambda: self.xylophoneEvents('b2'))
        self.c3.clicked.connect(lambda: self.xylophoneEvents('c3'))

# Bongos connections
        self.left.setShortcut('q')
        self.right.setShortcut('w')
        self.left.clicked.connect(lambda: self.BongosEvents('c4'))
        self.right.clicked.connect(lambda: self.BongosEvents('d3'))

# creating piano notes based on the buttons clicked
    def PianoEvents(self , key):
        if self.pianoButton.isChecked() == False:
            pass
        if key == 'c' :
            name = 'c4'
        elif key == 'c#':
            name = 'c4#'
        elif key == 'd':
            name = 'd4'
        elif key == 'd#':
            name = 'd4#'
        elif key == 'e':
            name = 'e4'
        elif key == 'f':
            name = 'f4'
        elif key == 'f#':
            name = 'f4#'
        elif key == 'g':
            name = 'g4'
        elif key == 'g#':
            name = 'g4#'
        elif key == 'a':
            name = 'a4'
        elif key == 'a#':
            name = 'a4#'
        elif key == 'b':
            name = 'b4'
        self.generatePiano(name)

# playing the notes sent from PianoEvents 
    def generatePiano(self, name):
        x = instrument.Piano()
        keyNote = note.Note(name)
        keyNote.duration.quarterLength = 1
        keyNote.volume.velocity = 120 
        output_notes=[]
        output_notes.append(x)
        output_notes.append(keyNote)
        streamNote = Stream(output_notes)
        midi.realtime.StreamPlayer(streamNote).play(playForMilliseconds=50, blocked=False)

# creating xylophone notes based on the buttons clicked
    def xylophoneEvents(self , key):
        if self.xylophoneButton.isChecked() == False:
            pass
        if key == 'c1' :
            name = 'c7'
        elif key == 'd1':
            name = 'd7'
        elif key == 'e1':
            name = 'e7'
        elif key == 'f1':
            name = 'f7'
        elif key == 'g1':
            name = 'g7'
        elif key == 'a1':
            name = 'a7'
        elif key == 'b1':
            name = 'b7'
        elif key == 'c2':
            name = 'c8'
        elif key == 'd2':
            name = 'd8'
        elif key == 'f2':
            name = 'f8'
        elif key == 'g2':
            name = 'g8'
        elif key == 'a2':
            name = 'a8'
        elif key == 'b2':
            name = 'b8'
        elif key == 'c3':
            name = 'c9'
        self.generateXylophone(name)

# playing the notes sent from xylophoneEvents 
    def generateXylophone(self, name):
        x = instrument.Xylophone()
        keyNote = note.Note(name)
        keyNote.duration.quarterLength = 1
        keyNote.volume.velocity = 127 
        output_notes=[]
        output_notes.append(x)
        output_notes.append(keyNote)
        streamNote = Stream(output_notes)
        midi.realtime.StreamPlayer(streamNote).play(playForMilliseconds=50, blocked=False)

# creating Bongos notes based on the buttons clicked
    def BongosEvents(self , key):
        self.bongoinst = instrument.BongoDrums()
        if self.BongosButton.isChecked() == False:
            pass
        if key == 'c4' :
            name = 'c4'
            self.bongoinst.modifier = 'low'
        elif key == 'd3':
            name = 'e4'
            self.bongoinst.modifier = 'low'
        self.generateBongos(name)

# playing the notes sent from BongosEvents 
    def generateBongos(self , name):
        keyNote = note.Note(name)
        keyNote.duration.quarterLength = 0.5
        keyNote.volume.velocity = 127 
        output_notes=[]
        output_notes.append(self.bongoinst)
        output_notes.append(keyNote)
        streamNote = Stream(output_notes)
        midi.realtime.StreamPlayer(streamNote).play(playForMilliseconds=1000, blocked=True)

################## Equalizer ##################
    def open(self):
        self.fname = QFileDialog.getOpenFileName(
            None, "Select a file...", os.getenv('HOME'), filter="All files (*)")
        path = self.fname[0]
        if '.mp3' in path:
            song = AudioSegment.from_mp3(path)
            song.export(r"./final.wav", format="wav")
            self.f_rate, self.yData = wavfile.read(r"./final.wav")
        else:
            self.f_rate, self.yData = wavfile.read(path)
        if  len(self.yData.shape) > 1:
            self.yData = self.yData[:,0]

        self.yData = self.yData / 2.0**15
        self.yAxisData = self.yData
        self.SIZE = len(self.yAxisData)
        self.xAxisData = np.linspace(
            0, self.SIZE / self.f_rate, num=self.SIZE)
        self.fourier()
        self.p = vlc.MediaPlayer(path)
        self.p.audio_set_volume(50)
        self.volumeLabel.setText(str(self.volumeSlider.value()))
        self.DoubleBassGain.setText(str(self.doubleBass.value()))
        self.BassGain.setText(str(self.bass.value()))
        self.TrumpetGain.setText(str(self.trumpet.value()))
        self.PianoGain.setText(str(self.Piano.value()))
        self.ElectronicGain.setText(str(self.electronic.value()))
        self.plot()
        self.play()

# plotting the song as a signal
    def plot(self):
        self.timer.timeout.connect(self.updateSignal)
        self.timer.start()
        self.originalCanvas.axes.clear()
        self.originalCanvas.axes.plot(
            self.xAxisData, self.yAxisData, linewidth=0.5)
        self.originalCanvas.draw()
        self.signalPlot.setCentralItem(self.graph)
        self.signalPlot.setLayout(self.originalLayout)

# filtering frequencies for instruments 
    def filtermaker(self):
        temp= [[],[],[],[],[]]
        for i, f in enumerate(self.freq):
            if f <= 500 :
                temp[0].append(self.FTydata[i])
            if f <= 1000 and f > 500:
                temp[1].append(self.FTydata[i])
            if f <= 2000 and f > 1000:
                temp[2].append(self.FTydata[i])
            if f <= 5000 and f > 2000:
                temp[3].append(self.FTydata[i])
            if f > 5000:
                temp[4].append(self.FTydata[i])
        self.bands = temp

# gathering data from sliders and use them to control each instrument gain
    def gainmaker(self):
        self.DoubleBassGain.setText(str(self.doubleBass.value()))
        self.BassGain.setText(str(self.bass.value()))
        self.TrumpetGain.setText(str(self.trumpet.value()))
        self.PianoGain.setText(str(self.Piano.value()))
        self.ElectronicGain.setText(str(self.electronic.value()))
        self.gain = [ self.doubleBass.value(), self.bass.value(), self.trumpet.value(
        ), self.Piano.value(),  self.electronic.value()]

# doing fourier transofrm on the data in order to access the frequency component in filter maker
    def fourier(self):
        self.FTydata = np.fft.rfft(self.yData)
        self.bands = []
        self.freq = np.fft.rfftfreq(self.SIZE, d = 1/self.f_rate)
        self.filtermaker()

# plotting a spectrogram based on the data either original or changed
    def plotSpecGram(self):
        self.spectroCanvas.axes.specgram(self.yAxisData, Fs=self.f_rate)
        self.spectroCanvas.draw()
        self.specPlot.setCentralItem(self.graph)
        self.specPlot.setLayout(self.specLayout)

    def volumeControl(self):
        self.p.audio_set_volume(self.volumeSlider.value())
        self.volumeLabel.setText(str(self.volumeSlider.value()))

# organising function in order to call other functions in the correct order for optimised output
    def play(self):
        self.timer.start()
        self.update()
        self.plotSpecGram()
        self.xMin = 0
        self.xMax = 1 
        self.p.play()

# start the music along with the signal plot timer to see them in sync
    def playMusic(self):
        if self.changed == True:
            self.timer.start()
            self.p.play()
            self.changed = False
        else:
            self.Pause()
            self.changed = True

    def Pause(self):
        self.p.pause()
        self.timer.stop()

# updating data after using filters and gain in filter maker and then plot the change and play it
    def update(self):
        self.xMin = 0
        self.xMax = 1
        self.gainmaker()
        fftFilter = []
        for i in range(len(self.gain)):
            band = np.array(self.bands[i])
            gain = int(self.gain[i])
            temp = gain*band
            fftFilter = [*fftFilter, *temp]
        self.yAxisData = np.fft.irfft(fftFilter)
        self.p.stop()
        wavfile.write(r"./filtered.wav",self.f_rate,self.yAxisData)
        self.plot()        
        self.p = vlc.MediaPlayer(r"./filtered.wav")

# playing the signal 
    def updateSignal(self):
        if self.xMax < self.xAxisData[-1]:
            self.xMin, self.xMax = self.originalCanvas.axes.set_xlim(
                auto=False, xmin=self.xMin + .1, xmax=self.xMax + .1)
            self.originalCanvas.draw()

    


def main():
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
