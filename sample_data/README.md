# sample_data/

This folder is intentionally empty in the repository.

The dashboard fetches **live data** directly from Yahoo Finance at runtime — no
local sample data files are required to run the project.

If you use the **"Download Cleaned Stock Data"**, **"Download Technical Indicator
Data"**, or **"Download Comparison Summary"** buttons inside the app, the exported
CSV files will land in your browser's default Downloads folder (or you can choose
to save them here for your own reference, e.g. for offline testing).

This folder is `.gitignore`-protected for any `*.csv` files you drop in here, so
exported data won't accidentally get committed to version control.
