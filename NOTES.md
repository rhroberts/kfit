# Development Notes and TO-DOs

## Notes

- Getting the balance of good user experience and also good fitting guesses is tough
    - Don't want to be too restrictive with initial bounds, but it does help in certain easier fitting cases
    - I think implementing an "edit mode" will be a good way to tackle this
- Will need to implement QThreads for both fitting and import processes so the GUI doesn't freeze up
    - this will help:
        - https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/
    - Still over my head at the moment...
    - Work on this once the program is decently usable aside from the freezing on long fits
- Regardless of whether I implement threading, it is probably best I do a better job of isolating the GUI stuff from the actual fitting process

## TO-DOs

### High Priority

- Edit mode is not functional yet
    - Figure out why doing an edit mode entry always fills the **last** param entry widget, rather than the one that is clicked
    - In general, need to clean up how edit mode works, it's pretty sloppy
- Reconcile amp/height, sigma/fwhm
    - would be better if user specifies height and fwhm

- The params widget interface still isn't very user friendly
    - Why is the box holding the line lineEntry boxes fixed?
        - or why does it have a min_width and the others don't?

### Medium Priority

- Need a more robust file import import dialog
- Some sort of progress bar
- Still need to figure of the issue of having to initialize model with something 
    - Don't want to always have to use a line in the model
- Removing user entry from text box doesn't reset value to guess
    - is this resolved?
- Need to show warning when user tries to enter value above/below the parameter bounds
- Continue to clean up messy code

### Low Priority

- Not at all necessary, but would be a good learning experience to rewrite with gtk and compare
- Would be interesting to have the app "learn" from previous fits
    - this would just be keeping the results, for example, for gau1 and using those in the next fit, even if other models are added
- Would be cool for user to be able to click on the graph to choose param values (e.g. click at peak center to set lor1_center(val,min,max)
    - ~~not sure how to implement this yet~~
    - currently working on an "edit mode" that implements this
- Think more carefully about when/why things *actually* need to be class attributes of App()

### Done

- App crashes when loading new data set *after* fitting initial one
    - fixed
- Allow user to select fitting range
    - Solution: only zoomed region of pyplot is fit
    - Hitting <enter> in either columnindex box will reset range
- Make pyplot toolbar icons larger
    - This is likely just an issue with the HiDPI screen, see NavigationToolbar2QT() in:
        - https://github.com/matplotlib/matplotlib/blob/master/lib/matplotlib/backends/backend_qt5.py
    - I reset their QIcon size to (36,36) from the original (24,24)
        - Looks much better on my xps13 display, but need to check on a lower res display (might be gigantic)
- Showing the current values next to the param user inputs will be essential, and will also help me with debugging
    - my solution is to have the current vals be the placeholder text in the "value" box, "max" and "min" show the max and min set in self.params
- Parameter Widgets
    - These should be added by buttons (Gaussians [+], etc..) for each parameter columns
    - Should not erase all widgets and start over when one is added
        - This forgets user input values
        - My solution still rewrites the widgets, but it's working at least
- Connect usr_input with fitting process
    - Placeholder text needs to be updated after user entry
        - When you removes the text they added after updating the params, the default value used in the model is the previous user entry, but the placeholder text show the initial guess by the program
    - Now usr text stays after fitting but **not when peaks are added to the model**
        - This is because init_params() is called on [+/-] click, which wipes the layout
        - Though to be fair the usr input does remain as placeholder text
    - still some weird stuff like after fitting the value placeholder text doesn't change
- The layout itself should have a fixed height
    - i.e. not eat up space from the plot widget when there are a bunch of params
    - Something should fill this space before the first fit
- And each column should be individually scrollable
- Need a better data structure for usr_entry
    - dealing with val, min, and max
    - solution: nested dict
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
    - Solution:
        - Just needed to keep the line entry widgets in a dictionary, all good now
