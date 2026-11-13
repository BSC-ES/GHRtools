# README
Dependencies:
- Python installed in the machine
- R installed in the machine
- \_Pandoc: gives "required and not found" if ran in a machine without it
	- Fix: `sudo apt update && sudo apt install pandoc`
- `data4health` package needs to be installed in order for its renders to function.
	- You need to download the `data4health` tarball and can then run the following R script to install it:
```R
	  install.packages(c('readxl', 'writexl', 'shinyAce')) # data4health dependencies
	  install.packages("./data4health-v0.1.1.tar.gz", repos = NULL, type="source")
```
## Step-by-step
0. Before starting, make sure you have python and R installed in your machine and you have solved the dependencies:
	1. run `sudo apt update && sudo apt install pandoc` in a command line
	2. The script will install the latest versions of the GHRTools packages, but you might need to install some dependencies first. Run `R`  then:
		1. `install.packages(c('readxl', 'writexl', 'shinyAce'))` 
		2. (OR) Run `R -e "install.packages(c('readxl', 'writexl', 'shinyAce'))"
		3. `install.packages("./data4health-v0.1.1.tar.gz", repos = NULL, type="source")`
1. Place the `generate_md.R` and `generate_docs.py` scripts in the `scripts` folder of the github pages repo: `/GHRtools/scripts/generate_md.R` and `/GHRtools/scripts/generate_docs.py`
	1. Important: the python script contains the relative paths where the script will download, extract, and use the packages from. They specified at the top of the file, under the imports: `DATA_DIRECTORY = "../../downloaded_data/"`. 
2. In the `/scripts/` directory, run `python generate_docs.py -p all` to run the generator for all four packages currently available (see below). Alternatively, you can specify each target package by its name. The arguments accepted by the script are as follow:
	1. `-p` (also ` --packages`) is the parameter to specify which packages you want to generate the docs for. It accepts:
		1. `ghrmodel` (aliases: `model`)
		2. `ghrexplore` (aliases: `explore`)
		3. `data4health` (aliases: `data`, `d4h`)
		4. `clim4health` (aliases: `clim`, `c4h`)
	2.  `-v` (also ` --verbose`) is a flag you can use to have the script print more information that it would by default. This includes a repetition of the given arguments, and logs for when each step is taking place.
	3. `-k` (also `--keep-data`) is a flag that specifies you want to keep the downloaded data after the script is done.