import sys
import numpy as np
import CircularSection as cs

from PyQt5.QtWidgets import QMessageBox
from fbs_runtime.application_context import ApplicationContext
from PyQt5 import QtWidgets

from math import degrees
from scipy.misc import derivative
from scipy.optimize import root

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class Main(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle( "Dairesel Kesit Hidrolik")

        # a figure instance to plot on
        # self.figure = plt.figure()
        self.figure = Figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        # central widget
        self.centralWidget = QtWidgets.QWidget(self)

        # main layout
        self.mhLayout = QtWidgets.QHBoxLayout(self.centralWidget)

        # main layout
        self.vLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        # button horizantal layout
        self.bhLayout = QtWidgets.QHBoxLayout(self.centralWidget)

        # main layout
        self.cvLayout = QtWidgets.QVBoxLayout(self.centralWidget)

        # main button
        self.cb_hq = QtWidgets.QCheckBox(self.centralWidget)
        self.cb_hq.setText('Su yüksekliği için çöz')

        self.m_hq = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.m_hq.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.m_hq.setPrefix('Debi, Q = ')
        self.m_hq.setSuffix(' [m³/s]')
        self.m_hq.setDecimals(4)
        self.m_hq.setValue(10)

        self.m_d = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.m_d.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.m_d.setPrefix('Çap, D = ')
        self.m_d.setSuffix(' [m]')
        self.m_d.setDecimals(4)
        self.m_d.setValue(3.5)

        self.m_n = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.m_n.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.m_n.setPrefix('Manning Katsayı, n = ')
        self.m_n.setDecimals(5)
        self.m_n.setValue(0.016)

        self.m_s = QtWidgets.QDoubleSpinBox(self.centralWidget)
        self.m_s.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.m_s.setPrefix('Taban Eğimi, J = ')
        self.m_s.setSuffix(' [m/m]')
        self.m_s.setDecimals(6)
        self.m_s.setValue(0.006)

        self.m_result = QtWidgets.QTextEdit(self.centralWidget)
        self.m_result.setMinimumHeight(300)

        self.m_OK = QtWidgets.QPushButton(self.centralWidget)
        self.m_OK.setText('Hesapla')

        self.m_EXIT = QtWidgets.QPushButton(self.centralWidget)
        self.m_EXIT.setText('Çıkış')

        self.m_rc= QtWidgets.QPushButton(self.centralWidget)
        self.m_rc.setText('Kapasite Eğri')

        self.m_be = QtWidgets.QPushButton(self.centralWidget)
        self.m_be.setText('Boyutsuz Eğri')

        # horizontal layout for buttons
        self.bhLayout.addWidget(self.m_be)
        self.bhLayout.addWidget(self.m_rc)
        self.bhLayout.addWidget(self.m_OK)
        self.bhLayout.addWidget(self.m_EXIT)

        # add all main to the main vLayout
        self.vLayout.addWidget(self.cb_hq)
        self.vLayout.addWidget(self.m_hq)
        self.vLayout.addWidget(self.m_d)
        self.vLayout.addWidget(self.m_n)
        self.vLayout.addWidget(self.m_s)
        self.vLayout.addWidget(self.m_result)
        self.vLayout.addLayout(self.bhLayout)

        # add canvas items to vertical layout
        self.cvLayout.addWidget(self.canvas)
        self.cvLayout.addWidget(self.toolbar)

        # add all main to the main mhLayout
        self.mhLayout.addLayout(self.vLayout)
        self.mhLayout.addLayout(self.cvLayout)

        # set central widget
        self.setCentralWidget(self.centralWidget)

        self.setLayout(self.mhLayout)

        self.cb_hq.setChecked(False)

        self.cb_hq.stateChanged.connect(self.cb_hq_changed)
        self.m_OK.clicked.connect(self.hesapla)
        self.m_rc.clicked.connect(self.draw_rating_curve)
        self.m_be.clicked.connect(self.draw_dimensionless_curve)
        self.m_EXIT.clicked.connect(self.close)


    def cb_hq_changed(self, state):
        if self.cb_hq.isChecked():
            self.m_hq.setPrefix('Su yükseklik, h = ')
            self.m_hq.setSuffix(' [m]')
        else:
            self.m_hq.setPrefix('Debi, Q = ')
            self.m_hq.setSuffix(' [m³/s]')

    def hesapla(self):
        h, q = 0.0, 0.0
        if self.cb_hq.isChecked():
            h = self.m_hq.value()
        else:
            q = self.m_hq.value()
        s = self.m_s.value()
        n = self.m_n.value()
        d = self.m_d.value()

        self.m_result.clear()
        try:
            sect = cs.CircularSection(q, s, n, d, h=h)
            self.m_result.append("Debi, Q = {0:0.2f} m³/s".format(sect.Q))
            self.m_result.append("Çap, D = {0:0.2f} m".format(d))
            self.m_result.append("Manning katsayı, n = {0:0.4f}".format(n))
            self.m_result.append("Taban eğimi, J = {0:0.6f} m/m".format(s))
            self.m_result.append("")
            sectUniform = sect.get_uniform_properties()
            sectCritic = sect.get_critical_properties()
            self.draw_rating_curve()
        except Exception as e:
            QMessageBox.critical(self.centralWidget, "Hata", str(e))
            print(e)
            return

        self.write_results("Üniform Özellikler:", sectUniform)
        self.m_result.append("")
        self.write_results("Kritik Özellikler:", sectCritic)

    def write_results(self, name, sect:cs.CircularSection):
        self.m_result.append("<b>{0}</b>".format(name))
        self.m_result.append("Su yüksekliği, h = {0:0.2f} m".format(sect.h[0]))
        self.m_result.append("Islak alan, A = {0:0.4f} m²".format(sect.A))
        self.m_result.append("Su yüzü genişliği, T = {0:0.6f} m".format(sect.T))
        self.m_result.append("Hidrolik yarıçap, R = {0:0.4f} m".format(sect.R))
        self.m_result.append("Hız, V = {0:0.4f} m/s".format(sect.V))
        self.m_result.append("Froude, Fr = {0:0.4f}".format(sect.Fr))
        self.m_result.append("Hız yükü, hv = {0:0.4f} m".format(sect.hv))
        self.m_result.append("Enerji, E = {0:0.4f} m".format(sect.E[0]))
        self.m_result.append("Ortalama hidrolik derinlik, Dm = {0:0.4f} m".format(sect.Dm))
        self.m_result.append("Su yüzü ağırlık merkezi, Z = {0:0.4f} m".format(sect.Z))
        self.m_result.append("Momentum, M = {0:0.4f} m³".format(sect.M))
        self.m_result.append("beta = {0:0.2f} °".format(degrees(sect.beta)))

    def draw_rating_curve(self):
        q = self.m_hq.value()
        s = self.m_s.value()
        n = self.m_n.value()
        d = self.m_d.value()
        try:
            sect = cs.CircularSection(q, s, n, d)
        except Exception as e:
            QMessageBox.critical(self.centralWidget, "Hata", str(e))
            return

        df = lambda y: derivative(sect.calculate_discharge, y, dx=1e-6)
        ymax = root(df, 0.95 * sect.D, method='lm').x[0]
        qmax = sect.calculate_discharge(ymax)
        y_arr = np.arange(0.001, sect.D, 0.001, np.float)
        q_arr = np.fromiter((sect.calculate_discharge(y) for y in y_arr), np.float)

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(y_arr, q_arr, linestyle='solid')
        ax.set_title('Dairesel Kesit Kapasite Eğrisi \n(Qmaks={0:0.2f} m³/sn, Ymax={1:0.2f} m, Qtam={2:0.2f} m³/sn)'.
                 format(qmax, ymax, sect.calculate_full_discharge()))
        ax.set_xlabel('Su Seviyesi (m)')
        ax.set_ylabel(r'Debi (m³/s)')
        ax.grid(which='both')

        # refresh canvas
        self.canvas.draw()

    def draw_dimensionless_curve(self):
        d, n, So, Q = 1.0, 0.014, 0.001, 0.0
        p, t, a, z, r, beta = [], [], [], [], [], []
        h_ = np.linspace(0.0001, d, 1000)
        for val in h_:
            try:
                sect = cs.CircularSection(Q, So, n, d, h=val)
                sect.calculate_hydraulic_properties(val)
            except Exception as e:
                QMessageBox.critical(self.centralWidget, "Hata", str(e))
                return

            p.append(sect.P)
            t.append(sect.T)
            z.append(sect.Z)
            a.append(sect.A)
            r.append(sect.R)
            beta.append(sect.beta)
        self.figure.clear()
        ax1 = self.figure.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.grid(which='both')
        line1, = ax1.plot(h_, t, color='red', linestyle='--', linewidth=2)
        line2, = ax1.plot(h_, a, color='green', linestyle='--', linewidth=2)
        line3, = ax1.plot(h_, p, color='blue')
        line4, = ax1.plot(h_, beta, color='magenta', linestyle='-.', linewidth=2)
        line5, = ax2.plot(h_, r, color='black')
        line6, = ax2.plot(h_, z, color='cyan', linestyle='-.', linewidth=2)
        ax1.set_xlabel('h')
        ax2.set_ylabel('Z ve R')
        ax1.set_ylabel(r'$\beta$, T, A ve P')
        ax1.legend([line1, line2, line3, line4, line5, line6], ['Su yüzü genişlik (T)', 'Alan (A)', 'Islak çevre (P)',
                                                                r'$\beta$', 'Hidrolik Yarıçap (R)',
                                                                'Ağırlık merkezi derinlik (Z)'], loc='best')
        ax1.set_title('Dairesel Kesit Hidrolik Özellikleri Boyutuz Eğriler', verticalalignment='bottom')
        # refresh canvas
        self.canvas.draw()


class AppContext(ApplicationContext):           # 1. Subclass ApplicationContext
    def run(self):                              # 2. Implement run()
        window = Main()
        window.show()
        return self.app.exec_()                 # 3. End run() with this line


if __name__ == '__main__':
    appctxt = AppContext()                      # 4. Instantiate the subclass
    exit_code = appctxt.run()                   # 5. Invoke run()
    sys.exit(exit_code)