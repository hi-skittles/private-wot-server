This directory is the default location for secondary database files. Secondary
database files have a ".db" suffix and exists while the system is running. 
They will be deleted when the system is shutdown and the data consolidation 
process completes successfully. 

If there are secondary database files in this directory, then it indicates that 
the system is running or it did not shut down cleanly. BigWorld can recover
from most crashes so addition action is usually not required to clean up the
files. 

Secondary database files are SQLite database files. You can examine them using
standard SQLite tools.
