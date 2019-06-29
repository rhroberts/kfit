# Development Notes and TO-DOs

## Notes

- Parameter Widgets
    - These should be added by buttons (Gaussians [+], etc..) for each parameter columns
    - Should not erase all widgets and start over when one is added
        - This forgets user input values
    - When a new parameter is added, the fit should use the user guesses for any persistent parameters and then guess at the new one

## TO-DOs

### High Priority

- Need a better data structure for usr_entry
    - dealing with val, min, and max
- App crashes when loading new data set *after* fitting initial one

### Medium Priority

- Need to show warning when user tries to enter value above/below the parameter bounds
- Placeholder text needs to be updated after user entry
    - When you removes the text they added after updating the params, the default value used in the model is the previous user entry, but the placeholder text show the initial guess by the program
- The layout itself should have a fixed height
    - i.e. not eat up space from the plot widget when there are a bunch of params
    - Something should fill this space before the first fit
- And each column should be individually scrollable

### Low Priority

- Think more carefully about when/why things *actually* need to be class attributes of App()

### Done

- Make the param_layout have four columns -- one for each peak types
- Am I using pyqtSlot() correctly?
    - https://stackoverflow.com/questions/39210500/how-do-i-connect-a-pyqt5-slot-to-a-signal-function-in-a-class
    - seems like I can probably delete them all...
        - yup
- Add lineEntry widgets for min() and max() parmeters as well... 
    - Round off the placeholder text in entry widgets
        - done, but should really do something more robust in cases of values on the order of $10^{-6}$ or smaller
            - eh, it's just the placeholder, not the value being used
- Fix the app logic re:
    - When are fit(), update_usr_params(), and guess_params() called
        - Right now it's a clusterfuck and user params get overwritten by guesses when fitting
        - Also, as it stands guess_params doesn't work without a call to fit, but this results in really slow fits w/o user having opportunity to specify params first
- How will we get user entry from the param widgets if they are dynamic?
    - Status:
        - I can connect them up to slots, and all entry widgets can produce a signal
        - Need to direct those to the param values...
        - Can print out the user entered value, but...
            - With multiples of the same peak type (or in family gau/lor/voi), only the last peak can be addressed...
            - The former line entries are overwritten in loop
            - Perhaps need a dictionary?
        - **I think I need to separate the "setting up the model, taking first guesses" and the "user updating of model params" functionality**
        - Done
    - Solution:
        - Just needed to keep the line entry widgets in a dictionary, all good now

