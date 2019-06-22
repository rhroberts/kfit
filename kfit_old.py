#!/usr/bin/env python
# coding: utf-8

# # *kfit* -- an interactive fitting program built on bokeh
# 
# **To Do:**
# -  Add multi-row tables (for multi-peak models)
#     -  need to associate slider names with parameters in table
# -  Show components of fits for multi-peak models
# -  Option for fitting several similar datasets (e.g. polarized Raman/PL)
# -  Button for exporting `.csv` of fit results
# -  Show more advanced fit statistics such as error and correlation
# -  Fix the issue of negative starting guesses w/sliders
#     -  Perhaps the best solutions is to use fill-in boxes instead of sliders
# -  Find a more clever way to format the slider list so it isn't just one column
# 

# In[1]:


# imports from Bokeh
from bokeh.io import show, output_notebook
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import RangeSlider, Button, DataTable, TableColumn
from bokeh.layouts import gridplot, widgetbox
from bokeh.application.handlers import FunctionHandler
from bokeh.application import Application
# other standard imports
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import sys
import re
# importing my stuff
# insert custom directory for my custom imports
sys.path.insert(0, 'D:\\Box Sync\\programming\\custom_functions\\')
import kspace as ks
import custom_models


# In[2]:


# importing data and giving an initial fit


def initial_fit(x, y, model, usr_params=None):
    
    if usr_params == None:
        # fit the data, get initial parameters
        result = model.fit(y, x=x)
        params = result.params  # LMFIT Parameters() object
    else:
        # fit the data, get initial parameters
        result = model.fit(y, usr_params, x=x)
        params = result.params  # LMFIT Parameters() object

    # dictionary of parameters and values (used for table)
    param_dict = {
        key: value for key, value in params.valuesdict().items()
    }

    # params for sliders (i.e. only the params that can be constrained)
    slider_params = result.best_values
    
    return(result, params, param_dict, slider_params)

    
# prompt user for model name and data file to fit
usr_input = input("Specify model to use from custom_models.py : ")
root = tk.Tk() # give the tk instance a name
# prompt user to select file
file_path = filedialog.askopenfilename()
root.withdraw() # make the tk window go away after file selection

# get data from file
x0, y0 = ks.wire2array(file_path)

# pass the input for fit_model to custom_models
model_func = getattr(custom_models, usr_input)
model = model_func()

# initialize the fit
result, params, param_dict, slider_params = initial_fit(x0, y0, model)


# In[13]:


# Create the document application
def modify_doc(doc):
    
    
    # create the main plot
    def create_figure(fit_source, comps_sources):
        # plot fit results
        plot = figure(x_axis_label='x-axis', y_axis_label='y-axis', width=900, height=400)
        plot.circle(x0, y0, fill_color=None, line_color="black", size=10)
        plot.line("x", "y", source=fit_source, color="red", line_width=4)
        for header, comp_source in comps_sources.items():
            plot.line("x", "y", source=comp_source, color="lime", line_width=2) 
        return(plot)
    
    
    # make a table that will show the fit results
    def create_table(param_dict):
        
        pre_list = []
        parameter_list = []
        clustered_dict = {}

        for header in param_dict:
            pre_list.append(header[:header.find("_")])
            parameter_list.append(header[header.find("_")+1:])

        pre_list = set(pre_list)
        parameter_list = set(parameter_list)

        for parameter in parameter_list:
            cluster = []
            for prefix in pre_list:
                header = prefix + "_" + parameter
                cluster.append(param_dict[header])
            clustered_dict[parameter] = cluster

        table_data_df = pd.DataFrame(data=clustered_dict, columns=parameter_list, index=pre_list)
        
        table_source = ColumnDataSource(data=table_data_df)
        table_columns = [TableColumn(field=key, title=key) for key, value in clustered_dict.items()]
        return(table_source, table_columns, clustered_dict)
    
    
    # define the callback function for updating fit based on slider values
    def update_fit():
        global slider_params
        
        # update params with fitting constraints based on slider values
        for key, val in slider_params.items():
            params[key].set(
                min=constraint_sliders[key].value[0],
                max=constraint_sliders[key].value[1]
            )
            
        # update fit with new params
        new_result, new_params, new_param_dict, new_slider_params = initial_fit(x0, y0, model, usr_params=params)
        new_fit_data = {}
        new_fit_data["x"] = x0
        new_fit_data["y"] = new_result.best_fit
        fit_source.data = new_fit_data
        # define data sources for individual fit components
        new_comps = new_result.eval_components()
        for header, data in new_comps.items():
            new_comps_data = {}
            new_comps_data["x"] = x0
            new_comps_data["y"] = data
            comps_sources[header].data = new_comps_data
        
        # update table
        dummy1, dummy2, table_data_dict = create_table(new_param_dict)
        table_source.data = table_data_dict


    # define the callback function for resetting fit and parameters
    def reset_fit():
        global result, params, param_dict, slider_params
        
        # update params and fit
        result, params, param_dict, slider_params = initial_fit(x0, y0, model)
        fit_data = {}
        fit_data["x"] = x0
        fit_data["y"] = result.best_fit
        fit_source.data = fit_data
        # define data sources for individual fit components
        comps = result.eval_components()
        for header, data in comps.items():
            comps_data = {}
            comps_data["x"] = x0
            comps_data["y"] = data
            comps_sources[header].data = comps_data
        
        # update table
        dummy1, dummy2, table_data_dict = create_table(param_dict)
        table_source.data = table_data_dict
        
        # reset constraint sliders back to initial values
        for parameter, slider in constraint_sliders.items():
            slider.value = init_slider_values[parameter]


            
    # define data source for overall fit
    fit_source = ColumnDataSource(data=dict(x=x0, y=result.best_fit))
    # define data sources for individual fit components
    comps = result.eval_components()
    comps_sources = {key: ColumnDataSource(data=dict(x=x0, y=val)) for key, val in comps.items()}
    
    # making the slider widgets
    slider_range = 0.5
    slider_step = 0.001
    # add number of sliders based on params in param_dict
    constraint_sliders = {
        key: RangeSlider(
            title=key,
            start=params[key] - params[key]*slider_range,
            end=params[key] + params[key]*slider_range,
            value=(
                params[key] - params[key]*slider_range,
                params[key] + params[key]*slider_range
            ),
            step=slider_step,
            format="0[.]000"
        ) for key in slider_params
    }
    
    # get initial slider state to use later
    init_slider_values = {parameter: slider.value for parameter, slider in constraint_sliders.items()}

    # put slider in list to be accessed later by widgetbox()
    # note: widgetbox() can't take constraint_sliders.values()
    slider_list = [slider for slider in constraint_sliders.values()]

    # make button that will update the fit
    fit_button = Button(label="Fit", button_type="success")
    # make a button to reset the fit
    reset_button = Button(label="Reset", button_type="success")
    
    # make a list of widgets to pass to the document
    widget_list = slider_list
    widget_list.insert(0, fit_button)  # put the fit button at the top of widget list
    widget_list.append(reset_button)  # put the reset button at the bottom of widget list
    widgets = widgetbox(widget_list)
    
    # make the table for displaying fitting results
    table_source, table_columns, table_data_dict = create_table(param_dict)
    table_widget = widgetbox(
        DataTable(
            source=table_source, columns=table_columns, index_header="peak", width=600
        )
    )

    # Define conditions for callback functions to be initiated
    fit_button.on_click(update_fit)
    reset_button.on_click(reset_fit)

    # set up the page layout
    plot = create_figure(fit_source, comps_sources)
    layout = gridplot([[plot], [widgets, table_widget]])
    doc.add_root(layout)
    
    
# set up the application
handler = FunctionHandler(modify_doc)
app = Application(handler)  


# In[14]:


# create the document (not strictly necessary, but helps with debugging)
doc = app.create_document()


# In[15]:


# run the application
# make sure the URL matches your Jupyter instance
output_notebook()
show(app, notebook_url="localhost:8888")

