# Development Notes and TO-DOs

## Notes


## TO-DOs

### Smaller Tasks

- Make the param_layout have four columns -- one for each peak types
    - The layout itself should have a fixed height
        - i.e. not eat up space from the plot widget when there are a bunch of params
        - Something should fill this space before the first fit
    - And each column should be individually scrollable
- Add lineEntry widgets for min() and max() parmeters as well...
- ~~Round off the placeholder text in entry widgets~~
    - done, but should really do something more robust in cases of values on the order of $10^{-6}$ or smaller
- ~~Am I using pyqtSlot() correctly?~~
    - https://stackoverflow.com/questions/39210500/how-do-i-connect-a-pyqt5-slot-to-a-signal-function-in-a-class
    - seems like I can probably delete them all...
        - yup

### Larger Tasks

- Think more carefully about when/why things *actually* need to be class attributes of App()
- **How will we get user entry from the param widgets if they are dynamic?**
    - Status:
        - I can connect them up to slots, and all entry widgets can produce a signal
        - Need to direct those to the param values..
