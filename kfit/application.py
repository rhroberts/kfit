import sys
import time
import pandas as pd
import numpy as np
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from kfit import models, tools
from lmfit.model import Parameters
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
        self.left = 1000
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
        # empty Parameters to hold parameter guesses/constraints
        self.params = Parameters()

        # temporary data 
        x = np.linspace(0,10,500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
                models.gauss(x, 0.8, 5, 0.2) + \
                models.gauss(x, 0.4, 6, 0.3) + 0.2
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
        self.statusBar.showMessage('Welcome to kfit!', msg_length)
        self.statusBar.setStyleSheet('background-color: white')
        
        # Create the Main Widget and Layout
        self.main_layout = QVBoxLayout()
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # create "top bar" widget
        self.topbar_layout = QHBoxLayout()
        self.topbar_widget = QWidget()
        # import button
        self.importButton = QPushButton('', self)
        self.importButton.setIcon(QIcon.fromTheme('up'))
        self.importButton.setIconSize(QSize(50,50))
        self.importButton.clicked.connect(self.get_data)
        # fit button
        self.fitButton = QPushButton('', self)
        self.fitButton.setIcon(QIcon.fromTheme('dialog-apply'))
        self.fitButton.setIconSize(QSize(50,50))
        self.fitButton.clicked.connect(self.fit)
        self.fitButton.setStyleSheet('font-style: bold')
        # quit button
        self.quitButton = QPushButton('', self)
        self.quitButton.setIcon(QIcon.fromTheme('gtk-cancel'))
        self.quitButton.setIconSize(QSize(50,50))
        self.quitButton.clicked.connect(self.close_app)
        # get column header for x
        self.xLabel = QLabel(self)
        self.xLabel.setText('ColumnIndex(X):')
        self.xLineEntry = QLineEdit(self)
        self.xLineEntry.setPlaceholderText('0')
        self.xLineEntry.setAlignment(Qt.AlignCenter)
        self.xLineEntry.returnPressed.connect(self.xset_click)
        # get column header for y
        self.yLabel = QLabel(self)
        self.yLabel.setText('ColumnIndex(Y):')
        self.yLineEntry = QLineEdit(self)
        self.yLineEntry.setPlaceholderText('1')
        self.yLineEntry.setAlignment(Qt.AlignCenter)
        self.yLineEntry.returnPressed.connect(self.yset_click)
        # add topbar widgets to layout
        self.topbar_layout.addSpacing(500)
        self.topbar_layout.addWidget(self.xLabel)
        self.topbar_layout.addWidget(self.xLineEntry)
        self.topbar_layout.addSpacing(50)
        self.topbar_layout.addWidget(self.yLabel)
        self.topbar_layout.addWidget(self.yLineEntry)
        self.topbar_layout.addSpacing(250)
        self.topbar_layout.addWidget(self.fitButton)
        self.topbar_layout.addWidget(self.importButton)
        self.topbar_layout.addWidget(self.quitButton)
        self.topbar_widget.setLayout(self.topbar_layout)

        # create tabs widget
        self.tabs = QTabWidget(self)
        self.tab1 = QWidget(self)
        self.tab2 = QTableView(self)
        self.tab3 = QWidget(self)
        self.tabs.addTab(self.tab1,'Graph')
        self.tabs.addTab(self.tab2,'Data')
        self.tabs.addTab(self.tab3,'Output')

        # create params widget
        self.params_widget = QWidget() 
        self.params_layout = QGridLayout()
        self.gau_widget = QWidget()
        self.gau_layout = QVBoxLayout()
        self.gau_widget.setLayout(self.gau_layout)
        self.gau_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lor_widget = QWidget()
        self.lor_layout = QVBoxLayout()
        self.lor_widget.setLayout(self.lor_layout)
        self.lor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.voi_widget = QWidget()
        self.voi_layout = QVBoxLayout()
        self.voi_widget.setLayout(self.voi_layout)
        self.voi_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lin_widget = QWidget()
        self.lin_layout = QVBoxLayout()
        self.lin_widget.setLayout(self.lin_layout)
        self.lin_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.params_layout.addWidget(self.gau_widget, 0, 1)
        self.params_layout.addWidget(self.lor_widget, 0, 2)
        self.params_layout.addWidget(self.voi_widget, 0, 3)
        self.params_layout.addWidget(self.lin_widget, 0, 4)
        self.params_widget.setLayout(self.params_layout)

        # add everything to layout
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addWidget(self.topbar_widget)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(self.params_widget)
        self.main_widget.setLayout(self.main_layout)

        # Tab 1 - Graph / Model
        ## Graph
        plt.style.use('fivethirtyeight')
        self.tab1.figure = Figure(figsize=(9,6), dpi=110)
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.toolbar =  NavigationToolbar(self.tab1.canvas, self)
        graph_layout = QGridLayout()
        graph_layout.addWidget(self.tab1.canvas, 0, 0)
        graph_layout.addWidget(self.tab1.toolbar, 1, 0)

        ## The "Set Model" layout
        model_layout = QGridLayout()
        widget_setgau = QWidget()
        layout_setgau = QHBoxLayout()
        layout_setgau.setSizeConstraint(QLayout.SetFixedSize)
        widget_setgau.setLayout(layout_setgau)
        widget_setlor = QWidget()
        layout_setlor = QHBoxLayout()
        layout_setlor.setSizeConstraint(QLayout.SetFixedSize)
        widget_setlor.setLayout(layout_setlor)
        widget_setvoi = QWidget()
        layout_setvoi = QHBoxLayout()
        layout_setvoi.setSizeConstraint(QLayout.SetFixedSize)
        widget_setvoi.setLayout(layout_setvoi)
        widget_setlin = QWidget()
        layout_setlin = QHBoxLayout()
        layout_setlin.setSizeConstraint(QLayout.SetFixedSize)
        widget_setlin.setLayout(layout_setlin)
        model_layout.addWidget(widget_setgau, 0, 0)
        model_layout.addWidget(widget_setlor, 0, 1)
        model_layout.addWidget(widget_setvoi, 0, 2)
        model_layout.addWidget(widget_setlin, 0, 3)

        ## specify number of gaussian curves
        gauss_label = QLabel(self)
        gauss_label.setText('Gaussians')
        gauss_label.setAlignment(Qt.AlignVCenter)
        gauss_button_add = QPushButton('', self)
        gauss_button_add.setIcon(QIcon.fromTheme('list-add'))
        gauss_button_add.clicked.connect(
            lambda: self.increment('gau', True)
        )
        gauss_button_add.clicked.connect(self.init_params)
        gauss_button_sub = QPushButton('', self)
        gauss_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        gauss_button_sub.clicked.connect(
            lambda: self.increment('gau', False)
        )
        gauss_button_sub.clicked.connect(self.init_params)
        layout_setgau.addWidget(gauss_label)
        layout_setgau.addWidget(gauss_button_add)
        layout_setgau.addWidget(gauss_button_sub)
        ## specify number of lorentzian curves
        lorentz_label = QLabel(self)
        lorentz_label.setText('Lorentzians')
        lorentz_label.setAlignment(Qt.AlignVCenter)
        lorentz_button_add = QPushButton('', self)
        lorentz_button_add.setIcon(QIcon.fromTheme('list-add'))
        lorentz_button_add.clicked.connect(
            lambda: self.increment('lor', True)
        )
        lorentz_button_add.clicked.connect(self.init_params)
        lorentz_button_sub = QPushButton('', self)
        lorentz_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        lorentz_button_sub.clicked.connect(
            lambda: self.increment('lor', False)
        )
        lorentz_button_sub.clicked.connect(self.init_params)
        layout_setlor.addWidget(lorentz_label)
        layout_setlor.addWidget(lorentz_button_add)
        layout_setlor.addWidget(lorentz_button_sub)
        ## specify number of voigt curves
        voigt_label = QLabel(self)
        voigt_label.setText('Pseudo-Voigts')
        voigt_label.setAlignment(Qt.AlignVCenter)
        voigt_button_add = QPushButton('', self)
        voigt_button_add.setIcon(QIcon.fromTheme('list-add'))
        voigt_button_add.clicked.connect(
            lambda: self.increment('voi', True)
        )
        voigt_button_add.clicked.connect(self.init_params)
        voigt_button_sub = QPushButton('', self)
        voigt_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        voigt_button_sub.clicked.connect(
            lambda: self.increment('voi', False)
        )
        voigt_button_sub.clicked.connect(self.init_params)
        layout_setvoi.addWidget(voigt_label)
        layout_setvoi.addWidget(voigt_button_add)
        layout_setvoi.addWidget(voigt_button_sub)
        ## specify number of lines
        line_label = QLabel(self)
        line_label.setText('Lines:')
        line_label.setAlignment(Qt.AlignVCenter)
        line_button_add = QPushButton('', self)
        line_button_add.setIcon(QIcon.fromTheme('list-add'))
        line_button_add.clicked.connect(
            lambda: self.increment('lin', True)
        )
        line_button_add.clicked.connect(self.init_params)
        line_button_sub = QPushButton('', self)
        line_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        line_button_sub.clicked.connect(
            lambda: self.increment('lin', False)
        )
        line_button_sub.clicked.connect(self.init_params)
        layout_setlin.addWidget(line_label)
        layout_setlin.addWidget(line_button_add)
        layout_setlin.addWidget(line_button_sub)

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

        self.init_params()
        self.show()

    def init_model(self):
        # increment() ensures nlin >= 1
        self.model = models.line_mod(self.nlin)
        if self.ngau != 0:
            self.model += models.gauss_mod(self.ngau) 
        if self.nlor != 0:
            self.model += models.lor_mod(self.nlor)
        if self.nvoi != 0:
            self.model += models.voigt_mod(self.nvoi)
        self.statusBar.showMessage(
                "Model updated: " + \
                str([self.ngau, self.nlor, self.nvoi, self.nlin]),
            msg_length
        )

    def init_params(self):
        self.init_model()
        self.params = Parameters()
        for layout in [
            self.gau_layout, self.lor_layout,
            self.voi_layout, self.lin_layout
        ]:
            self.clear_layout(layout)
        self.usr_entry = {}
        labels = {}
        # !!! right now it's impossible to run this w/o fitting first
        # I'd like to change this behavior...
        for comp in self.model.components:
            if comp.prefix.find('gau') != -1 or \
                    comp.prefix.find('lor') != -1 or \
                    comp.prefix.find('voi') != -1:

                c = comp.prefix + 'center'
                cval = self.data.iloc[:,self.xcol_idx].mean()
                cmin = self.data.iloc[:,self.xcol_idx].min()
                cmax = self.data.iloc[:,self.xcol_idx].max()
                self.params.add(c, cval, True, cmin, cmax)

                labels[c] = QLabel()
                self.usr_entry[c+'_val'] = QLineEdit()
                self.usr_entry[c+'_min'] = QLineEdit()
                self.usr_entry[c+'_max'] = QLineEdit()
                labels[c].setText(c)
                self.usr_entry[c+'_val'].setPlaceholderText(str(round(cval,5)))
                self.usr_entry[c+'_min'].setPlaceholderText(str(round(cmin,5)))
                self.usr_entry[c+'_max'].setPlaceholderText(str(round(cmax,5)))

                a = comp.prefix + 'amplitude'
                aval = self.data.iloc[:,self.ycol_idx].mean()
                amin = self.data.iloc[:,self.ycol_idx].min()
                amax = self.data.iloc[:,self.ycol_idx].max()
                self.params.add(a, aval, True, amin, amax)
                labels[a] = QLabel()
                self.usr_entry[a+'_val'] = QLineEdit()
                self.usr_entry[a+'_min'] = QLineEdit()
                self.usr_entry[a+'_max'] = QLineEdit()
                labels[a].setText(a)
                self.usr_entry[a+'_val'].setPlaceholderText(str(round(aval,5)))
                self.usr_entry[a+'_min'].setPlaceholderText(str(round(amin,5)))
                self.usr_entry[a+'_max'].setPlaceholderText(str(round(amax,5)))

                s = comp.prefix + 'sigma'
                sval = self.data.iloc[:,self.xcol_idx].std()
                smin = 0
                smax = None
                self.params.add(s, sval, True)            
                labels[s] = QLabel()
                self.usr_entry[s+'_val'] = QLineEdit()
                self.usr_entry[s+'_min'] = QLineEdit()
                self.usr_entry[s+'_max'] = QLineEdit()
                labels[s].setText(s)
                self.usr_entry[s+'_val'].setPlaceholderText(str(round(sval,5)))
                self.usr_entry[s+'_min'].setPlaceholderText(str(round(smin,5)))
                self.usr_entry[s+'_max'].setPlaceholderText('')

                # set up connections
                # note: connect() expects a callable func, hence the lambda
                for item in ['_val', '_min', '_max']:
                    self.usr_entry[c+item].returnPressed.connect(
                        lambda: self.update_usr_params(self.usr_entry)
                    )
                    self.usr_entry[a+item].returnPressed.connect(
                        lambda: self.update_usr_params(self.usr_entry)
                    )
                    self.usr_entry[s+item].returnPressed.connect(
                        lambda: self.update_usr_params(self.usr_entry)
                    )

                # add widgets to respective layouts
                if comp.prefix.find('gau') != -1:
                    for p in [c, a, s]:
                        sublayout = QHBoxLayout()
                        sublayout.addWidget(labels[p])
                        sublayout.addWidget(self.usr_entry[p+'_val'])
                        sublayout.addWidget(self.usr_entry[p+'_min'])
                        sublayout.addWidget(self.usr_entry[p+'_max'])
                        self.gau_layout.addLayout(sublayout)
                if comp.prefix.find('lor') != -1:
                    for p in [c, a, s]:
                        sublayout = QHBoxLayout()
                        sublayout.addWidget(labels[p])
                        sublayout.addWidget(self.usr_entry[p+'_val'])
                        sublayout.addWidget(self.usr_entry[p+'_min'])
                        sublayout.addWidget(self.usr_entry[p+'_max'])
                        self.lor_layout.addLayout(sublayout)
                # voigt needs an additional param (fraction)
                if comp.prefix.find('voi') != -1:
                    f = comp.prefix + 'fraction'
                    fval = 0.5
                    fmin = 0
                    fmax = 1
                    self.params.add(f, fval, True)
                    labels[f] = QLabel()
                    self.usr_entry[f+'_val'] = QLineEdit()
                    self.usr_entry[f+'_min'] = QLineEdit()
                    self.usr_entry[f+'_max'] = QLineEdit()
                    labels[f].setText(f)
                    self.usr_entry[f+'_val'].setPlaceholderText(str(round(fval,5)))
                    self.usr_entry[f+'_min'].setPlaceholderText(str(round(fmin,5)))
                    self.usr_entry[f+'_max'].setPlaceholderText(str(round(fmax,5)))

                    # set up connections
                    for item in ['_val', '_min', '_max']:
                        self.usr_entry[f+item].returnPressed.connect(
                            lambda: self.update_usr_params(self.usr_entry)
                        )
                    # add voigt widgets
                    for p in [c, a, s, f]:
                        sublayout = QHBoxLayout()
                        sublayout.addWidget(labels[p])
                        sublayout.addWidget(self.usr_entry[p+'_val'])
                        sublayout.addWidget(self.usr_entry[p+'_min'])
                        sublayout.addWidget(self.usr_entry[p+'_max'])
                        self.voi_layout.addLayout(sublayout)
            else:
                # line model
                slope = comp.prefix + 'slope'
                slopeval = self.data.iloc[:,self.ycol_idx].mean()
                self.params.add(slope, slopeval, True)
                labels[slope] = QLabel()
                self.usr_entry[slope] = QLineEdit()
                labels[slope].setText(slope)
                self.usr_entry[slope].setPlaceholderText(str(round(slopeval,5)))
                self.usr_entry[slope].returnPressed.connect(
                    lambda: self.update_usr_params(self.usr_entry)
                )
                intc = comp.prefix + 'intercept'
                intcval = self.data.iloc[:,self.ycol_idx].mean()
                self.params.add(intc, intcval, True)
                labels[intc] = QLabel()
                self.usr_entry[intc] = QLineEdit()
                labels[intc].setText(intc)
                self.usr_entry[intc].setPlaceholderText(str(round(intcval,5)))
                self.usr_entry[intc].returnPressed.connect(
                    lambda: self.update_usr_params(self.usr_entry)
                )
                # add line widgets
                for p in [slope, intc]:
                    sublayout = QHBoxLayout()
                    sublayout.addWidget(labels[p])
                    sublayout.addWidget(self.usr_entry[p])
                    self.lin_layout.addLayout(sublayout)
                    # self.sublayout.setAlignment(Qt.AlignLeft)

        # Resize all of the LineEntry widgets
        self.gau_layout.setAlignment(Qt.AlignTop)
        self.gau_layout.setAlignment(Qt.AlignTop)
        self.gau_layout.setAlignment(Qt.AlignTop)
        self.gau_layout.setAlignment(Qt.AlignTop)
        for label, widget in self.usr_entry.items():
            pass
            # widget.setMaxLength(10)
            #widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def update_usr_params(self, entry):
        print('\nUpdated parameters:')
        for param, entry_widget in self.usr_entry.items():
            try:
                self.params[param].value = float(entry_widget.text())
            except:
                pass
            print(param + ' (after): ' + str(self.params[param].value))
        self.fit()

    def fit(self):
        self.init_model()
        self.init_params()
        self.result = self.model.fit(
            data=self.data.iloc[:,self.ycol_idx],
            params=self.params,
            x=self.data.iloc[:,self.xcol_idx]
        )
        print(self.result.fit_report())
        self.plot()

    def xset_click(self):
        try:
            idx = int(self.xLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.xcol_idx = idx
        self.init_params()
        self.result = None
        self.plot()
        self.statusBar.showMessage(
            'ColumnIndex(X) = ' + str(idx), msg_length
        )

    def yset_click(self):
        try:
            idx = int(self.yLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.ycol_idx = idx
        self.init_params()
        self.result = None
        self.plot()
        self.statusBar.showMessage(
            'ColumnIndex(Y) = ' + str(idx), msg_length
        )

    def close_app(self):
        sys.exit()

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

    def clear_layout(self, layout):
        if layout:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else :
                    self.clear_layout(item.layout())
                layout.removeItem(item)

    @pyqtSlot()
    def increment(self, val, add):
        if add:
            if val == 'gau':
                self.ngau += 1
            if val == 'lor':
                self.nlor += 1
            if val == 'voi':
                self.nvoi += 1
            if val == 'lin':
                self.nlin += 1
        if not add:
            if val == 'gau':
                self.ngau -= 1
            if val == 'lor':
                self.nlor -= 1
            if val == 'voi':
                self.nvoi -= 1
            if val == 'lin':
                self.nlin -= 1

        # make sure value doesn't go below zero
        if self.ngau < 0:
            self.ngau = 0
        if self.nlor < 0:
            self.nlor = 0
        if self.nvoi < 0:
            self.nvoi = 0
        if self.nlin < 1:
            self.nlin = 1
        

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
