# Development Notes and TO-DOs

## Notes

- Will need to implement QThreads for both fitting and import processes so the GUI doesn't freeze up
    - Ex:
        - https://www.learnpyqt.com/courses/concurrent-execution/multithreading-pyqt-applications-qthreadpool/
    - Will work on this once the program is decently usable aside from the freezing on long fits
- Regardless of whether I implement threading, it is probably best I do a better job of isolating the GUI stuff from the actual fitting process

## TO-DOs

### High Priority

* I think finishing the below high-priority tasks will get the app to a place where it's decently user friendly

- [ ] Need much better error handling
- [ ] Add button(s) to save fit details and results
- [x] Need a more robust file import import dialog
    - still needs work, but will do for now
- [x] Let user choose b/w grabbing x/y coords with edit_mode button
    - Behavior should be:
        1. Edit mode off
        2. Edit mode on, grab x-value
        3. Edit mode on, grab y-value
    -  Will need to either make a custom class or mess with the style sheets
        - the former option would be better
    - Going to use checkboxes instead
- [ ] Reconcile amp/height, sigma/fwhm AND/OR define peaks for user
    - would be better if user specifies height and fwhm
    - this will just be an interface thing, fits will still use amp/height
        - will need to convert whenever we show the user a param (e.g. setPlaceholderText)
    - I'm leaving this as is for now

### Medium Priority

- Some sort of progress bar
    - this will require threading
- Still need to figure of the issue of having to initialize model with something 
    - Don't want to always have to use a line in the model
- Removing user entry from text box doesn't reset value to guess
    - is this resolved?
- Need to show warning when user tries to enter value above/below the parameter bounds
- Continue to clean up messy code

### Low Priority

- Would be useful to have the app "learn" from previous fits
    - this would just involve keeping the results, for example, for gau1 and using those in the next fit, even if other models are added
- Think more carefully about when/why things *actually* need to be class attributes of App()

### Done

- [x] Fix the syntax
- [x] Fit fails due to NaN error after importing new dataset
    - getting the syntax right fixed this, must have been a typo somewhere
- The params widget interface still isn't very user friendly
    - Why is the box holding the line lineEntry boxes fixed?
        - or why does it have a min_width and the others don't?
        - Rough fix -- set a max width on the line entry scroll area
- Edit mode is not functional yet
    - Figure out why doing an edit mode entry always fills the **last** param entry widget, rather than the one that is clicked
    - In general, need to clean up how edit mode works, it's pretty sloppy
    - Resolved -- now edit mode just copies to clipboard
- Would be cool for user to be able to click on the graph to choose param values (e.g. click at peak center to set lor1_center(val,min,max)
    - ~~not sure how to implement this yet~~
    - currently working on an "edit mode" that implements this
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

