# fm-staff-analysis

### Usage

1. Import custom view file (`./views/All.fmf`) into the 'Staff Search' page while in FM
2. Copy all view data (ctrl-A, ctrl-P) and save data as a text file to `./input/All.rtf`
3. Use `./staff-search.py` to analyze coaches and print top canidates


### Options

	-i, --input
		specify the name of the input file; e.g., ./staff-search.py -i [filename] 
	-n, --number
		specify number of top canidates to print; e.g., ./staff-search.py -n [number]
	-o. --overall
		sort coaches by sum of all attributes
	-c. --coaching
		sort coaches by their max coaching aptitude
	-gk, --coaching
		sort coaches by their total goalkeeper coaching aptitude
	-f, --fitness-coaching
		sort coaches by their fitness coaching aptitude
	-yd, --head-youth-dev
		sort coaches by their aptitude as a head of youth development
	-h, --help
		print this message