Nob

Each afternoon the secretaries get a printed list of the next day's lists.
They make new entries for each procedure into endobase for each patient in the SCHEDULER page.
Endobase aleady has the ptients details from Blue Chip in the PATIENT LIST file.

Proposed workflow.

- Enter Doctor (only need initials, can use a dictionary as in the sample code to get the full name)

- for each patient enter mrn and shortcut for procedures that are planned eg p, c, pc, sc, psc

- when all patients for that doctor are entered, start pyautogui (described in last chapter of the book and that will dump the data in endobase)

- pyautogui will basically tab through the fields and dump the data, Once the mrn is in endobase it will automatically pull in the name

- there are keyboard shortcuts that pyautogui can use to open and close each procedure

- move on to the next doctor
