import sys
from kfit import models, tools
# from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, \
    QWidget, QAction, QTabWidget, QVBoxLayout, QFileDialog, \
    QSizePolicy, QTableView
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QAbstractTableModel, QVariant
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas_qtmodel import PandasModel

plt.style.use('fivethirtyeight')

class App(QMainWindow):
    
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 500
        self.top = 200
        self.width = 2000
        self.height = 1200
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('../images/K.png'))
        
        # temporary data 
        x = np.linspace(0, 10, 100)
        y = models.gauss(x, 1, 3, 2) + \
            models.gauss(x, 0.4, 5, 1) + \
            models.gauss(x, 15, 8, 1)
        self.data = pd.DataFrame([x,y]).T

        self.table_widget = DataTable(self)
        self.plot_widget = WidgetPlot(self)
        self.tabs_widget = TabsWidget(self)
        self.setCentralWidget(self.tabs_widget)

        
        # add import button
        import_btn = QPushButton('Import', self)
        import_btn.clicked.connect(self.import_data)
        import_btn.resize(import_btn.sizeHint())
        import_btn.move(600,12.5)
        
        # add clear canvas button
        clear_btn = QPushButton('Clear Data', self)
        clear_btn.clicked.connect(self.update_canvas)
        clear_btn.resize(clear_btn.sizeHint())
        clear_btn.move(720, 12.5)

        # add quit button
        quit_btn = QPushButton('Quit', self)
        quit_btn.clicked.connect(self.close_app)
        quit_btn.resize(quit_btn.sizeHint())
        quit_btn.move(887.5, 12.5)

        self.show()
        
    def close_app(self):
        print('\nExiting kfit...\n')
        sys.exit()
        
    def import_data(self):
        print('\nImporting .csv file...\n')
        file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if file_name != '':
            print(file_name)
            df = tools.to_df(file_name)
            print(df)
            print('Done.\n')
        else:
            print('Import cancelled.')
        
        # clear canvas
        self.update_canvas()
        
        
    def update_canvas(self):
        self.plot_widget.canvas.ax.clear()
        self.plot_widget.canvas.draw()


class TabsWidget(QWidget):
    
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        
        # Initialize tabs screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300,200)
        
        # Add tabs
        self.tabs.addTab(self.tab1,"Graph View")
        self.tabs.addTab(self.tab2,"Data View")
        
        # Graph View tab
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.parent().plot_widget)
        self.tab1.setLayout(self.tab1.layout)

        # Table View tab
        self.tab2.layout = QVBoxLayout(self)
        self.tab2.layout.addWidget(self.parent().table_widget)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)
        self.show()
        
class DataTable(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        df = pd.DataFrame(data=self.parent().data)
        self.setLayout(QVBoxLayout(self))
        self.table = QTableView(self)
        self.table.setMinimumSize(2000, 1075)
        self.model = PandasModel(df)
        self.table.setModel(self.model)
        self.table.resizeColumnsToContents()

class WidgetPlot(QWidget):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setLayout(QVBoxLayout(self))
        self.canvas = PlotCanvas(self)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.layout().addWidget(self.canvas)
        self.layout().addWidget(self.toolbar)

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None, width=9, height=6, dpi=150):
        fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.ax = self.figure.add_subplot(111)
        self.plot()

    def plot(self):
        x = np.linspace(0, 10, 100)
        y = models.gauss(x, 1, 3, 2) + \
            models.gauss(x, 0.4, 5, 1) + \
            models.gauss(x, 15, 8, 1)
        self.ax.scatter(
            x, y, s=150, c='None', edgecolors='black',
            linewidth=2
        )
        self.draw()


def run():
    app = QApplication(sys.argv)
    GUI = App()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    run()
