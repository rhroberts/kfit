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
from matplotlib.widgets import Cursor

idx_error_msg = "Error: Can't convert index to integer!"
msg_length = 2000

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'kfit'
        self.left = 400
        self.top = 150
        self.width = 2400
        self.height = 1600
        self.file_name = ''
        self.xcol_idx = 0
        self.ycol_idx = 1
        self.ngau = 0
        self.nlor = 0
        self.nvoi = 0
        self.nlin = 1
        self.model = None
        self.result = None
        self.edit_mode = False
        # empty Parameters to hold parameter guesses/constraints
        self.params = Parameters()
        self.guesses = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.usr_vals = {
            'value': {},
            'min': {},
            'max': {}
        }
        self.usr_entry_widgets = {}
        self.cid = None

        # temporary data 
        x = np.linspace(0,10,500)
        y = models.gauss(x, 0.5, 4, 0.4) + \
                models.gauss(x, 0.8, 5, 0.2) + \
                models.gauss(x, 0.4, 6, 0.3) + 0.2
        # set data
        self.data = pd.DataFrame([x,y]).T
        self.data.columns = ['x', 'y']
        self.x = self.data['x']
        self.y = self.data['y']
        self.xmin = self.data['x'].min()
        self.xmax = self.data['x'].max()

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
        self.importButton = QPushButton('Import', self)
        self.importButton.setMaximumWidth(150)
        self.importButton.clicked.connect(self.get_data)
        # fit button
        self.fitButton = QPushButton('Fit', self)
        self.fitButton.setMaximumWidth(150)
        self.fitButton.clicked.connect(self.fit)
        # progress bar
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(200)
        self.progressBar.hide()
        # get column header for x
        self.xLabel = QLabel(self)
        self.xLabel.setText('ColumnIndex(X):')
        self.xLabel.setMaximumWidth(220)
        self.xLabel.setAlignment(Qt.AlignCenter)
        self.xLineEntry = QLineEdit(self)
        self.xLineEntry.setPlaceholderText('0')
        self.xLineEntry.setAlignment(Qt.AlignCenter)
        self.xLineEntry.setMaximumWidth(100)
        self.xLineEntry.returnPressed.connect(self.xset_click)
        # get column header for y
        self.yLabel = QLabel(self)
        self.yLabel.setText('ColumnIndex(Y):')
        self.yLabel.setMaximumWidth(220)
        self.yLabel.setAlignment(Qt.AlignVCenter)
        self.yLineEntry = QLineEdit(self)
        self.yLineEntry.setPlaceholderText('1')
        self.yLineEntry.setAlignment(Qt.AlignCenter)
        self.yLineEntry.setMaximumWidth(100)
        self.yLineEntry.returnPressed.connect(self.yset_click)
        # add topbar widgets to layout
        self.topbar_layout.addWidget(self.xLabel)
        self.topbar_layout.addWidget(self.xLineEntry)
        self.topbar_layout.addSpacing(25)
        self.topbar_layout.addWidget(self.yLabel)
        self.topbar_layout.addWidget(self.yLineEntry)
        self.topbar_layout.addSpacing(75)
        self.topbar_layout.addWidget(self.fitButton)
        self.topbar_layout.addWidget(self.importButton)
        self.topbar_layout.addWidget(self.progressBar)
        self.topbar_layout.setAlignment(Qt.AlignRight)
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
        self.gau_layout = QVBoxLayout()
        self.gau_widget = QWidget()
        self.gau_widget.setLayout(self.gau_layout)
        self.gau_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.gau_scroll = QScrollArea()
        self.gau_scroll.setWidget(self.gau_widget)
        self.gau_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.gau_scroll.setWidgetResizable(True)
        self.lor_widget = QWidget()
        self.lor_layout = QVBoxLayout()
        self.lor_widget.setLayout(self.lor_layout)
        self.lor_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lor_scroll = QScrollArea()
        self.lor_scroll.setWidget(self.lor_widget)
        self.lor_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lor_scroll.setWidgetResizable(True)
        self.voi_widget = QWidget()
        self.voi_layout = QVBoxLayout()
        self.voi_widget.setLayout(self.voi_layout)
        self.voi_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.voi_scroll = QScrollArea()
        self.voi_scroll.setWidget(self.voi_widget)
        self.voi_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.voi_scroll.setWidgetResizable(True)
        self.lin_widget = QWidget()
        self.lin_layout = QVBoxLayout()
        self.lin_widget.setLayout(self.lin_layout)
        self.lin_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.lin_scroll = QScrollArea()
        self.lin_scroll.setWidget(self.lin_widget)
        self.lin_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.lin_scroll.setWidgetResizable(True)
        self.params_layout.addWidget(self.gau_scroll, 0, 1)
        self.params_layout.addWidget(self.lor_scroll, 0, 2)
        self.params_layout.addWidget(self.voi_scroll, 0, 3)
        self.params_layout.addWidget(self.lin_scroll, 0, 4)
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
        self.tab1.figure = Figure(figsize=(8,6), dpi=110)
        self.tab1.canvas = FigureCanvas(self.tab1.figure)
        self.tab1.canvas.setMinimumHeight(800)
        self.tab1.toolbar =  NavigationToolbar(self.tab1.canvas, self)
        # "click-to-set"/edit  button
        self.edit_button = QPushButton()
        self.edit_button.setIcon(QIcon.fromTheme('stock_edit'))
        self.edit_button.setMaximumWidth(50)
        self.edit_button.setCheckable(True)
        self.edit_button.clicked.connect(self.toggle_edit_mode)
        self.edit_button.setStyleSheet('background-color: white')
        # need to see if the below setting looks ok on
        # lower res displays
        self.tab1.toolbar.setIconSize(QSize(36,36))
        self.tab1.toolbar.addWidget(self.edit_button)
        # self.tab1.toolbar.setAlignment(Qt.AlignCenter)
        graph_layout = QVBoxLayout()
        graph_layout.addWidget(self.tab1.toolbar)
        graph_layout.addWidget(self.tab1.canvas)

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
        gauss_button_add.clicked.connect(self.init_param_widgets)
        gauss_button_sub = QPushButton('', self)
        gauss_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        gauss_button_sub.clicked.connect(
            lambda: self.increment('gau', False)
        )
        gauss_button_sub.clicked.connect(self.init_param_widgets)
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
        lorentz_button_add.clicked.connect(self.init_param_widgets)
        lorentz_button_sub = QPushButton('', self)
        lorentz_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        lorentz_button_sub.clicked.connect(
            lambda: self.increment('lor', False)
        )
        lorentz_button_sub.clicked.connect(self.init_param_widgets)
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
        voigt_button_add.clicked.connect(self.init_param_widgets)
        voigt_button_sub = QPushButton('', self)
        voigt_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        voigt_button_sub.clicked.connect(
            lambda: self.increment('voi', False)
        )
        voigt_button_sub.clicked.connect(self.init_param_widgets)
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
        line_button_add.clicked.connect(self.init_param_widgets)
        line_button_sub = QPushButton('', self)
        line_button_sub.setIcon(QIcon.fromTheme('list-remove'))
        line_button_sub.clicked.connect(
            lambda: self.increment('lin', False)
        )
        line_button_sub.clicked.connect(self.init_param_widgets)
        layout_setlin.addWidget(line_label)
        layout_setlin.addWidget(line_button_add)
        layout_setlin.addWidget(line_button_sub)

        graph_layout.addLayout(model_layout)
        self.tab1.setLayout(graph_layout)
        self.plot()

        # Tab 2 - Data Table
        self.table_model = PandasModel(self.data)
        self.tab2.setModel(self.table_model)
        self.tab2.resizeColumnsToContents()

        # Tab 3 - Output
        self.tab3_widget = QPlainTextEdit()
        tab3_layout = QVBoxLayout()
        tab3_layout.addWidget(self.tab3_widget)
        self.tab3.setLayout(tab3_layout)

        self.init_param_widgets()
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

    def init_param_widgets(self):
        self.init_model()
        self.usr_entry_widgets = {
            'value': {},
            'min': {},
            'max': {}
        }
        labels = {}
        rnd = 3  # decimals to round to in placeholder text
        for layout in [
            self.gau_layout, self.lor_layout,
            self.voi_layout, self.lin_layout
        ]:
            self.clear_layout(layout)

        for param_name in self.model.param_names:
            # set param label text
            labels[param_name] = QLabel()
            labels[param_name].setText(param_name)

            # make qlineedit widgets
            for key in self.usr_entry_widgets:
                self.usr_entry_widgets[key][param_name] = QLineEdit()
                if param_name in self.usr_vals[key]:
                    self.usr_entry_widgets[key][param_name]\
                        .setPlaceholderText(
                            str(round(self.usr_vals[key][param_name], rnd))
                        )
                else:
                    self.usr_entry_widgets[key][param_name]\
                        .setPlaceholderText(key)
                # set up connections
                # connect() expects a callable func, hence the lambda
                # edit_mode_set only seems to work for the last param...
                # I see.. these just overwrite themselves. or do they?
                self.usr_entry_widgets[key][param_name].returnPressed.connect(
                    lambda: self.edit_mode_set(key, param_name)
                )
                self.usr_entry_widgets[key][param_name].returnPressed.connect(
                    lambda: self.update_usr_vals(self.usr_entry_widgets)
                )

            # add widgets to respective layouts
            sublayout1 = QVBoxLayout()
            sublayout2 = QHBoxLayout()
            sublayout1.addWidget(labels[param_name])
            for key in self.usr_entry_widgets:
                sublayout2.addWidget(
                    self.usr_entry_widgets[key][param_name]
                )
            if param_name.find('gau') != -1:
                self.gau_layout.addLayout(sublayout1)
                self.gau_layout.addLayout(sublayout2)
            if param_name.find('lor') != -1:
                self.lor_layout.addLayout(sublayout1)
                self.lor_layout.addLayout(sublayout2)
            if param_name.find('voi') != -1:
                self.voi_layout.addLayout(sublayout1)
                self.voi_layout.addLayout(sublayout2)
            if param_name.find('lin') != -1:
                self.lin_layout.addLayout(sublayout1)
                self.lin_layout.addLayout(sublayout2)

        # Resize all of the LineEntry widgets
        for key in self.usr_entry_widgets:
            for param, widget in self.usr_entry_widgets[key].items():
                widget.setMaximumWidth(150)

        if self.result is not None:
            self.set_params()
            self.update_param_widgets()

    def edit_mode_set(self, value_type, param_name):
        if self.edit_mode is True:
            self.usr_entry_widgets[value_type][param_name].setText(
                str(round(self.y_edit, 3))
            )
            print('Set ' + param_name + '(' + value_type + \
                    ') to: ' + str(self.y_edit))

    def update_param_widgets(self):
        rnd = 3
        # the 'value' placeholder text is the result for that param
        # taken from self.result
        # the 'min' and 'max' text is from either the self.guesses
        # or from self.usr_vals
        for param in self.params:
            if param in self.result.best_values:
                self.usr_entry_widgets['value'][param].setPlaceholderText(
                    str(round(self.result.best_values[param], rnd))
                )
                self.usr_entry_widgets['min'][param].setPlaceholderText(
                    str(round(self.params[param].min, rnd))
                )
                self.usr_entry_widgets['max'][param].setPlaceholderText(
                    str(round(self.params[param].max, rnd))
                )

    def guess_params(self):
        for comp in self.model.components:
            if comp.prefix.find('gau') != -1 or \
                    comp.prefix.find('lor') != -1 or \
                    comp.prefix.find('voi') != -1:

                # need to define explicitly to make proper guesses
                c = comp.prefix + 'center'
                a = comp.prefix + 'amplitude'
                s = comp.prefix + 'sigma'
                f = comp.prefix + 'fraction'

                self.guesses['value'][c] = \
                        self.data.iloc[:,self.xcol_idx].mean()
                self.guesses['value'][a] = \
                        self.data.iloc[:,self.ycol_idx].mean()
                self.guesses['value'][s] = \
                        self.data.iloc[:,self.xcol_idx].std()
                self.guesses['min'][c] = None
                self.guesses['min'][a] = 0
                self.guesses['min'][s] = 0
                self.guesses['max'][c] = None
                self.guesses['max'][a] = None
                self.guesses['max'][s] = None

                if comp.prefix.find('voi') != -1:
                    self.guesses['value'][f] = 0.5
                    self.guesses['min'][f] = 0
                    self.guesses['max'][f] = 1
            else:
                slope = comp.prefix + 'slope'
                intc = comp.prefix + 'intercept'
                for p in [slope, intc]:
                    self.guesses['value'][p] = \
                        self.data.iloc[:,self.ycol_idx].mean()
                    self.guesses['min'][p] = None
                    self.guesses['max'][p] = None

    def update_usr_vals(self, entry):
        # get text input from each usr_entry_widget
        for val_type, param_dict in self.usr_entry_widgets.items():
            for param, param_widget in param_dict.items():
                try:
                    self.usr_vals[val_type][param] = \
                        float(param_widget.text())
                except:
                    pass

    def set_params(self):
        self.params = Parameters()
        self.guess_params()
        self.update_usr_vals(self.usr_entry_widgets)
        vals = {}

        # fill params with any user-entered values
        # fill in blanks with guesses
        for param_name in self.model.param_names:
            for val_type in ['value', 'min', 'max']:
                if param_name in self.usr_vals[val_type]:
                    vals[val_type] = self.usr_vals[val_type][param_name]
                    # print('param: ' + param_name + ', type: ' +\
                    #         val_type + ', set_by: user')
                        
                else:
                    vals[val_type] = self.guesses[val_type][param_name]
                    # print('param: ' + param_name + ', type: ' +\
                    #         val_type + ', set_by: guess')
            self.params.add(
                name=param_name, value=vals['value'], vary=True,
                min=vals['min'], max=vals['max']
            )

    def set_xy_range(self):
        self.x = self.data.iloc[:,self.xcol_idx]
        self.y = self.data.iloc[:,self.ycol_idx]
        self.xmin, self.xmax = self.ax.get_xlim()
        range_bool = (self.x >= self.xmin) & (self.x <= self.xmax)
        self.x = self.x[range_bool].values
        self.y = self.y[range_bool].values

    def reset_xy_range(self):
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)

    def fit(self):
        self.edit_button.setChecked(False)
        self.edit_unchecked_attr()
        self.set_xy_range()
        self.set_params()
        self.result = self.model.fit(
            data=self.y, params=self.params, x=self.x,
            method='least_squares'
        )
        self.tab3_widget.clear()
        self.tab3_widget.insertPlainText(self.result.fit_report())
        self.plot()
        # overwrite widgets to clear input (not ideal method..)
        self.init_param_widgets()
        # update widgets with new placeholder text
        self.update_param_widgets()

    def xset_click(self):
        try:
            idx = int(self.xLineEntry.text())
        except:
            self.statusBar.showMessage(idx_error_msg, msg_length)
            return
        self.xcol_idx = idx
        self.result = None
        self.x = self.data.iloc[:,self.xcol_idx]
        self.y = self.data.iloc[:,self.ycol_idx]
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)
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
        self.result = None
        self.x = self.data.iloc[:,self.xcol_idx]
        self.y = self.data.iloc[:,self.ycol_idx]
        self.xmin = np.min(self.x)
        self.xmax = np.max(self.x)
        self.plot()
        self.statusBar.showMessage(
            'ColumnIndex(Y) = ' + str(idx), msg_length
        )
    
    def toggle_edit_mode(self):
        if self.edit_button.isChecked():
            self.edit_mode = True
            self.edit_checked_attr()
        else:
            self.edit_mode = False
            self.edit_unchecked_attr()

    def get_coord_click(self, event):
        self.x_edit, self.y_edit = event.xdata, event.ydata
        print([self.x_edit, self.y_edit])

    def edit_checked_attr(self):
        self.mpl_cursor = Cursor(
            self.ax, lw=1, c='red', linestyle='--'
        )
        self.edit_button.setStyleSheet('background-color: red')
        self.cid = self.tab1.canvas.mpl_connect(
            'button_press_event', self.get_coord_click
        )

    def edit_unchecked_attr(self):
        self.mpl_cursor = None
        self.tab1.canvas.mpl_disconnect(self.cid)
        self.edit_button.setStyleSheet('background-color: white')

    def close_app(self):
        sys.exit()

    def get_data(self):
        self.edit_button.setChecked(False)
        self.edit_unchecked_attr()
        # reset column indices
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
        # clear any previous fit result
        self.result = None
        # reset x, y, and xlim
        self.x = self.data.iloc[:,self.xcol_idx].values
        self.y = self.data.iloc[:,self.ycol_idx].values
        self.xmin = self.data.iloc[:,self.xcol_idx].min()
        self.xmax = self.data.iloc[:,self.xcol_idx].max()
        self.plot()
        self.statusBar.showMessage(
            'Import finished.', msg_length
        )


    def plot(self):
        self.tab1.figure.clear()
        self.ax = self.tab1.figure.add_subplot(111, label=self.file_name)
        self.ax.scatter(
            self.x, self.y, s=200, c='None',
            edgecolors='black', linewidth=2,
            label='data'
        )
        if self.result != None:
            yfit = self.result.best_fit
            self.ax.plot(self.x, yfit, c='r', linewidth=2.5)
            cmap = cm.get_cmap('gnuplot')
            components = self.result.eval_components()
            for i, comp in enumerate(components):
                self.ax.plot(
                    self.x, components[comp],
                    linewidth=2.5, linestyle='--',
                    c=cmap(i/len(components)),
                    label=comp[:comp.find('_')]
                )
        self.ax.set_xlabel(self.data.columns[self.xcol_idx], labelpad=15)
        self.ax.set_ylabel(self.data.columns[self.ycol_idx], labelpad=15)
        self.ax.set_xlim([self.xmin, self.xmax])
        self.ax.legend(loc='upper right')
        self.tab1.figure.subplots_adjust(bottom=0.15, left=0.06, right=0.94)
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