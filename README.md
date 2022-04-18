# fm-staff-analysis

### Usage

1. Import custom view file (e.g., `./views/Coach Search.fmf`) into the 'Staff Search' page while in FM
2. Copy all view data (ctrl-A, ctrl-P) and save data as a text file (e.g., `./input/rtf/coaching_candidates.rtf`
3. Use `./staff-search.py` to analyze coaches and print top canidates


### Options

	-i, --input
		specify the name of the input file; e.g., ./staff-search.py -i [filename] 
	-n, --number
		specify number of top canidates to print; e.g., ./staff-search.py -n [number]
	-o. --overall
		sort coaches by sum of all attributes; enabled by default if no analysis type (e.g. coaching) is selected
	-e, --caching
		  enables caching for faster processing times on subsequent runs
	-c, --coaching
		sort coaches by their max coaching aptitude
	-tc, --total-coaching
		sort coaches by their total coaching aptitude
	-gk, --goalkeeper-coaching
		sort coaches by their total goalkeeper coaching aptitude
	-f, --fitness-coaching
		sort coaches by their fitness coaching aptitude
	-yd, --head-youth-dev
		sort coaches by their aptitude as a head of youth development
	-h, --help
		print this message