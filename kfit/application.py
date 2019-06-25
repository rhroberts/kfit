import sys
import time
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from kfit import models, tools
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvas, \
    NavigationToolbar2QT as NavigationToolbar

idx_error_msg = "Error: Can't convert index to integer!"
msg_length = 2000

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 500
        self.top = 200
        self.width = 2000
        self.height = 1400
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.model = None
        self.result = None

        # temporary data 
        x = np.linspace(0,10,500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
                models.gauss(x, 0.8, 5, 0.2) + \
                models.gauss(x, 0.4, 6, 0.3)
        self.data = pd.DataFrame([x,y]).T
        self.data.columns = ['x', 'y']

        self.initUI()

    def initUI(self):
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        self.setWindowIcon(QIcon('../images/K.png'))

        # set up the status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.setStyleSheet(
            'background-color: white; color: purple'
        )
        self.statusBar.showMessage('Welcome to kfit!', msg_length)
        
        # Create the Main Tab Widget
        self.tabs = QTabWidget(self)
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget(self)
        self.tab2 = QTableView(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1,'Graph')
        self.tabs.addTab(self.tab2,'Data')
        self.tabs.addTab(self.tab3,'Output')

        # Tab 1 - Graph / Model
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(9,6), dpi=110)
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.toolbar =  NavigationToolbar(self.tab1.canvas, self)
        graph_layout = QGridLayout()
        graph_layout.addWidget(self.tab1.canvas, 0, 0)
        graph_layout.addWidget(self.tab1.toolbar, 1, 0)
        model_layout = QHBoxLayout()
        ## specify number of gaussian curves
        gauss_label = QLabel(self)
        gauss_label.setText('Gaussians:')
        gauss_label.setAlignment(Qt.AlignVCenter)
        self.gauss_entry = QLineEdit(self)
        self.gauss_entry.setAlignment(Qt.AlignCenter)
        self.gauss_entry.setPlaceholderText('0')
        self.gauss_entry.returnPressed.connect(self.fit)
        model_layout.addSpacing(200)
        model_layout.addWidget(gauss_label)
        model_layout.addWidget(self.gauss_entry)
        model_layout.addSpacing(50)
        ## specify number of lorentzian curves
        lorentz_label = QLabel(self)
        lorentz_label.setText('Lorentzians:')
        lorentz_label.setAlignment(Qt.AlignVCenter)
        self.lorentz_entry = QLineEdit(self)
        self.lorentz_entry.setAlignment(Qt.AlignCenter)
        self.lorentz_entry.setPlaceholderText('0')
        self.lorentz_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(lorentz_label)
        model_layout.addWidget(self.lorentz_entry)
        model_layout.addSpacing(50)
        ## specify number of pseudo-voigt curves
        voigt_label = QLabel(self)
        voigt_label.setText('Pseudo-Voigts:')
        voigt_label.setAlignment(Qt.AlignVCenter)
        self.voigt_entry = QLineEdit(self)
        self.voigt_entry.setAlignment(Qt.AlignCenter)
        self.voigt_entry.setPlaceholderText('0')
        self.voigt_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(voigt_label)
        model_layout.addWidget(self.voigt_entry)
        model_layout.addSpacing(50)
        ## specify number of linear curves
        line_label = QLabel(self)
        line_label.setText('Lines:')
        line_label.setAlignment(Qt.AlignVCenter)
        self.line_entry = QLineEdit(self)
        self.line_entry.setAlignment(Qt.AlignCenter)
        self.line_entry.setPlaceholderText('1')
        self.line_entry.returnPressed.connect(self.fit)
        model_layout.addWidget(line_label)
        model_layout.addWidget(self.line_entry)
        model_layout.addSpacing(200)

        graph_layout.addLayout(model_layout, 2, 0)
        self.tab1.setLayout(graph_layout)
        self.plot()

        # Tab 2 - Data Table
        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()

        # Tab 3 - Output
        tab3_layout = QGridLayout()
        self.tab3.setLayout(tab3_layout)

        # quit button
        self.quitButton = QPushButton('Quit', self)
        self.quitButton.clicked.connect(self.close_app)
        self.quitButton.resize(100,55)
        self.quitButton.move(1900, 0)

        # import button
        self.importButton = QPushButton('Import', self)
        self.importButton.clicked.connect(self.get_data)
        self.importButton.resize(100, 55)
        self.importButton.move(1800, 0)

        # fit button
        self.fitButton = QPushButton('', self)
        self.fitButton.setIcon(QIcon.fromTheme('dialog-apply'))
        self.fitButton.clicked.connect(self.fit)
        self.fitButton.resize(100, 55)
        self.fitButton.move(1700, 0)
        self.fitButton.setStyleSheet('font-style: bold')
        
        # get column header for x
        self.xLabel = QLabel(self)
        self.xLabel.setText('ColumnIndex(X):')
        self.xLabel.resize(300, 45)
        self.xLabel.move(500, 5)
        self.xLineEntry = QLineEdit(self)
        self.xLineEntry.resize(75, 45)
        self.xLineEntry.move(725, 5)
        self.xLineEntry.setPlaceholderText('0')
        self.xLineEntry.setAlignment(Qt.AlignCenter)
        self.xLineEntry.returnPressed.connect(self.xset_click)
        self.xSet = QPushButton('Set', self)
        self.xSet.resize(50, 45)
        self.xSet.move(800, 5)
        self.xSet.clicked.connect(self.xset_click)

        # get column header for y
        self.yLabel = QLabel(self)
        self.yLabel.setText('ColumnIndex(Y):')
        self.yLabel.resize(300, 45)
        self.yLabel.move(900, 5)
        self.yLineEntry = QLineEdit(self)
        self.yLineEntry.resize(75, 45)
        self.yLineEntry.move(1125, 5)
        self.yLineEntry.setPlaceholderText('1')
        self.yLineEntry.setAlignment(Qt.AlignCenter)
        self.yLineEntry.returnPressed.connect(self.yset_click)
        self.ySet = QPushButton('Set', self)
        self.ySet.resize(50, 45)
        self.ySet.move(1200, 5)
        self.ySet.clicked.connect(self.yset_click)

        self.show()

    @pyqtSlot()
    def init_model(self):
        self.model = models.line_mod(self.nlin)
        try:
            if self.gauss_entry.text() != '':
                self.ngau = int(self.gauss_entry.text())
            if self.lorentz_entry.text() != '':
                self.nlor = int(self.lorentz_entry.text())
            if self.voigt_entry.text() != '':
                self.nvoi = int(self.voigt_entry.text())
            if self.line_entry.text() != '':
                self.nlin = int(self.line_entry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return

        self.statusBar.showMessage(
                "Model updated: " + \
                str([self.ngau, self.nlor, self.nvoi, self.nlin]),
            msg_length
        )

    @pyqtSlot()
    def fit(self):
        self.init_model()
        if self.ngau != 0:
            self.model += models.gauss_mod(self.ngau) 
        if self.nlor != 0:
            self.model += models.lor_mod(self.nlor)
        if self.nvoi != 0:
            self.model += models.voigt_mod(self.nvoi)

        self.result = self.model.fit(
            data=self.data.iloc[:,self.ycol_idx],
            x=self.data.iloc[:,self.xcol_idx]
        )
        print(self.result.fit_report())
        self.plot()

    @pyqtSlot()
    def xset_click(self):
        try:
            idx = int(self.xLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.xcol_idx = idx
        self.plot()
        self.statusBar.showMessage(
            'ColumnIndex(X) = ' + str(idx), msg_length
        )

    @pyqtSlot()
    def yset_click(self):
        try:
            idx = int(self.yLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.ycol_idx = idx
        self.plot()
        self.statusBar.showMessage(
            'ColumnIndex(Y) = ' + str(idx), msg_length
        )

    @pyqtSlot()
    def close_app(self):
        sys.exit()

    @pyqtSlot()
    def get_data(self):
        # reset column indices
        # !!! need to clear the boxes as well...
        self.xcol_idx = 0
        self.ycol_idx = 1
        # open file dialog
        self.file_name,_ = QFileDialog.getOpenFileName(
            self, 'Open File', '', 'CSV files (*.csv)'
        )
        if self.file_name != '':
            # this message isn't showing up...
            self.statusBar.showMessage(
                'Importing .csv file: ' + self.file_name, msg_length
            )
            df = tools.to_df(self.file_name)
            self.data = df
        else:
            self.statusBar.showMessage(
                'Import cancelled.', msg_length
            )
            return

        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()
        self.plot()
        self.statusBar.showMessage(
            'Import finished.', msg_length
        )

    def plot(self):
        x = self.data.iloc[:,self.xcol_idx].values
        y = self.data.iloc[:,self.ycol_idx].values
        self.tab1.figure.clear()
        ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        ax.scatter(
            x, y, s=200, c='None',
            edgecolors='purple', linewidth=3
        )
        if self.result != None:
            yfit = self.result.best_fit.values
            ax.plot(x, yfit, c='r')
            cmap = cm.get_cmap('Dark2')
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                ax.plot(
                    x, components[comp],
                    linewidth=2, linestyle='--',
                    c=cmap(i/len(components))
                )
        ax.set_xlabel(self.data.columns[self.xcol_idx], labelpad=10)
        ax.set_ylabel(self.data.columns[self.ycol_idx], labelpad=15)
        self.tab1.canvas.draw()

class PandasModel(QAbstractTableModel): 
    def __init__(self, df = pd.DataFrame(), parent=None): 
        QAbstractTableModel.__init__(self, parent=parent)
        self._df = df

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if orientation == Qt.Horizontal:
            try:
                return self._df.columns.tolist()[section]
            except (IndexError, ):
                return QVariant()
        elif orientation == Qt.Vertical:
            try:
                # return self.df.index.tolist()
                return self._df.index.tolist()[section]
            except (IndexError, ):
                return QVariant()

    def data(self, index, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return QVariant()

        if not index.isValid():
            return QVariant()

        return QVariant(str(self._df.iloc[index.row(), index.column()]))

    def setData(self, index, value, role):
        row = self._df.index[index.row()]
        col = self._df.columns[index.column()]
        if hasattr(value, 'toPyObject'):
            # PyQt4 gets a QVariant
            value = value.toPyObject()
        else:
            # PySide gets an unicode
            dtype = self._df[col].dtype
            if dtype != object:
                value = None if value == '' else dtype.type(value)
        self._df.set_value(row, col, value)
        return True

    def rowCount(self, parent=QModelIndex()): 
        return len(self._df.index)

    def columnCount(self, parent=QModelIndex()): 
        return len(self._df.columns)

    def sort(self, column, order):
        colname = self._df.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._df.sort_values(colname, ascending= order == Qt.AscendingOrder, inplace=True)
        self._df.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


def run():
    app = QApplication(sys.argv)
    GUI = App()
    sys.exit(app.exec_())

    
if __name__ == '__main__':
    run()
