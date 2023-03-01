#!/usr/bin/env python3
import os, sys, time
import pandas as pd
import build_webpage

# Save a default filename for the input
DEFAULT_INPUT_FILENAME = './input/coaching_candidates.rtf'

# Sets default # of top candidates to print
DEFAULT_PRINT_NO = 10

MENTAL_COACHING_ATTRIBUTES  = ['Det', 'Dis', 'Mot']
COACHING_AREA_ATTRIBUTES    = ['Att', 'Def', 'Men']
COACHING_STYLE_ATTRIBUTES   = ['Tec', 'TCo']
GK_COACHING_ATTRIBUTES 		= ['GkD', 'GkH', 'GkS']
FITNESS_COACHING_ATTRIBUTES = ['Fit']
HEAD_YOUTH_DEV_ATTRIBUTES 	= ['Judge A', 'Judge P', 'Youth']
HEAD_COACH_ATTRIBUTES 	    = ['Man', 'Mot', 'Judge A', 'Judge P', 'Tac Knw']

# Duplicate-free list of all possible attributes (columns) for use in preprocessing()
ALL_ATTRIBUTES = list(set(MENTAL_COACHING_ATTRIBUTES +		
						  COACHING_AREA_ATTRIBUTES + 
						  COACHING_STYLE_ATTRIBUTES +
						  GK_COACHING_ATTRIBUTES +
						  FITNESS_COACHING_ATTRIBUTES +
						  HEAD_YOUTH_DEV_ATTRIBUTES +
						  HEAD_COACH_ATTRIBUTES))

COACHING_APTITUDES = ['Att-Tec', 'Att-TCo', 'Def-Tec', 'Def-TCo', 'Men-Tec', 'Men-TCo']

# Helper function for skiprows parameter in pandas.read_csv()
# Returns True for all lines numbers to read & returns False for all line numbers to skip
def skip_rows(x):
	if x < 9 or x % 2 == 0:
		return False
	else:
		return True

# Wrapper function that calls load_staff_rtf() and preprocessing()
def load_staff(input_filename):
	
	df = load_staff_rtf(input_filename)
	df = preprocessing(df)

	return df

def load_staff_rtf(input_filename):

	try:
		df = pd.read_csv(input_filename, sep = '|', skiprows=lambda x: skip_rows(x), skipinitialspace=True)

	except:
		print('Error: failed to load input file \'{}\' into dataframe'.format(input_filename))
		sys.exit(1)

	return df

def preprocessing(df):

	preprocessing_start_time = time.time()

	# In its current state, read_csv() includes two extra, unnamed columns
	# before and after all of the real columns (i.e., at index 0 & -1)
	df = df.iloc[:, 1:-1]

	# Removes whitespace from column headers
	df = df.rename(columns=lambda x: x.strip())

	# Removes whitespace from body (all values)
	df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

	# Drops rows where every feature is NaN
	# It's unclear how/why these rows are being exported (afaik, their aren't any NaN coaches in game)
	# Most exports (*.rtf) do NOT include these rows, but some do
	df = df.dropna(axis = 0, how = 'all')

	# By default, at least in this case, pd.read_csv() reads in all numeric values as floats
	# .astype('int64') converts all float values to ints
	for col in df.columns:
		if col in ALL_ATTRIBUTES:
			df[col] = pd.to_numeric(df[col]).astype('int64')

	print('total preprocessing time: {:.3f}s'.format(time.time() - preprocessing_start_time))

	return df

def coaching_analysis(df, sort_by):
	# From https://www.passion4fm.com/football-manager-coaching-staff-star-rating/:
	# The formula for determining coach aptitude (as seen in Training -> Coaches) is:
	# 6 * [Attack, Defense, Mental] + 3 * [Technical, Tactical] + 2 * [Determination + Discipline + Motivation]
	# The max possible aptitude is 300.  Aptitudes > 270 = 5 stars, aptitudes > 240 < 270 = 4.5 stars, etc.
	for coaching_area in ['Att', 'Def', 'Men']:
		for coaching_style in ['Tec', 'TCo']:
			df[coaching_area + '-' + coaching_style] = 2 * sum(df[_] for _ in MENTAL_COACHING_ATTRIBUTES) + 6 * df[coaching_area] + 3 * df[coaching_style]

	df['max_coaching_aptitude'] = df[COACHING_APTITUDES].max(axis=1)
	df['total_coaching_aptitude'] = sum(df[_] for _ in COACHING_APTITUDES)

	df = df.sort_values(by=sort_by, ascending=False)
	
	return df

def goalkeeper_coaching_analysis(df):

	df['gk_coaching_aptitude'] = sum(df[_] for _ in GK_COACHING_ATTRIBUTES)
	
	df = df.sort_values(by='gk_coaching_aptitude', ascending=False)
	
	return df

def fitness_coaching_analysis(df):
	# From https://www.passion4fm.com/football-manager-coaching-staff-star-rating/:
	# The formula for determining fitness coach aptitude (as seen in Training -> Coaches) is:
	# 9 * Fitness + 2 * [Determination + Discipline + Motivation]
	# The max possible aptitude is 300.  Aptitudes > 270 = 5 stars, aptitudes > 240 < 270 = 4.5 stars, etc.
	df['fitness_coaching_aptitude'] = 9 * sum(df[_] for _ in FITNESS_COACHING_ATTRIBUTES) + 2 * sum(df[_] for _ in MENTAL_COACHING_ATTRIBUTES)
	
	df = df.sort_values(by='fitness_coaching_aptitude', ascending=False)
	
	return df

def head_youth_dev_analysis(df):

	df['head_yth_dev_aptitude'] = sum(df[_] for _ in HEAD_YOUTH_DEV_ATTRIBUTES)
	
	df = df.sort_values(by='head_yth_dev_aptitude', ascending=False)
	
	return df

def head_coach_analysis(df):

	df['head_coach_aptitude'] = sum(df[_] for _ in HEAD_COACH_ATTRIBUTES)
	
	df = df.sort_values(by='head_coach_aptitude', ascending=False)
	
	return df

def print_top_candidates(df, no_candidates, metrics):
	# By default, pandas will truncate columns if the total column width is greater than
	# the width of the of the display (i.e. the terminal)
	# Truncated columns look like this:
	# 	Att-Tec  Att-TCo  ...  total_coaching_aptitude          Name
	#      60.0     52.0  ...                    334.0   Toni Varela
	#      55.5     50.5  ...                    322.0    Jason Oost
	#      58.5     57.5  ...                    334.0     Andy Reid
	# By setting 'max_columns' = None, we are forcing pandas not to truncate columns
	pd.set_option('display.max_columns', None)

	print(df[metrics + ['Name']].head(no_candidates))

def print_help_msg(exit_status):
	print('Usage:\n'
		  '	1. Import custom view file (`./views/All.fmf`) into the \'Staff Search\' page while in FM\n'
		  '	2. Copy all view data (ctrl-A, ctrl-P) and save data as a text file to `./input/All.rtf`\n'
		  '	3. Use `./staff-search.py` to analyze coaches and print top candidates\n'
		  'Options:\n'
		  '	-i, --input\n'
		  '		specify the name of the input file; e.g., ./staff-search.py -i [filename]\n'
		  '	-n, --number\n'
		  '		specify number of top candidates to print; e.g., ./staff-search.py -n [number]\n'
		  ' -s, --sort-by\n'
		  '		specify an attribute to sort by'
		  '	-c, --coaching\n'
		  '		sort coaches by their max coaching aptitude; enabled by default if no analysis type is selected\n'
		  ' -tc, --total-coaching\n'
		  '		sort coaches by their total coaching aptitude\n'
		  '	-gk, --goalkeeper\n'
		  '		sort coaches by their total goalkeeper coaching aptitude\n'
		  '	-f, --fitness-coaching\n'
		  '		sort coaches by their fitness coaching aptitude\n'
		  '	-yd, --head-youth-dev\n'
		  '		sort coaches by their aptitude as a head of youth development\n'
		  '	-h, --help\n'
		  '		print this message')

	sys.exit(exit_status)

if __name__ == '__main__':

	args = sys.argv[1:]

	input_filename = DEFAULT_INPUT_FILENAME
	no_candidates = DEFAULT_PRINT_NO
	staff_role = ''
	sort_by = ''

	# Iterate through args
	while len(args) > 0:
		arg = args.pop(0)
		if arg == '-h' or arg == '--help':
			print_help_msg(0)
		if arg == '-i' or arg == '--input':
			input_filename = args.pop(0)
		elif arg == '-n' or arg == '--number':
			no_candidates = int(args.pop(0))
		elif arg == '-s' or arg == '--sort-by':
			sort_by = args.pop(0)
		elif arg == '-c' or arg =='--coaching':
			staff_role = 'coaching'
			sort_by = 'max_coaching_aptitude'
		elif arg == '-tc' or arg =='--total-coaching':
			staff_role = 'coaching'
			sort_by = 'total_coaching_aptitude'
		elif arg == '-gk' or arg == '--goalkeeper':
			staff_role = 'goalkeeper_coaching'
		elif arg == '-f' or arg == '--fitness':
			staff_role = 'fitness_coaching'
		elif arg == '-yd' or arg == '--youth-dev':
			staff_role = 'head_youth_dev'
		elif arg == '-hc' or arg == '--head-coach':
			staff_role = 'head_coach'
		else:
			print('error: failed to recognize argument \'{}\' while parsing command-line arguments'.format(arg))
			print_help_msg(1)

	df = load_staff(input_filename)

	if staff_role == 'coaching' or staff_role == '':
		df = coaching_analysis(df, sort_by)
		print_top_candidates(df, no_candidates, COACHING_APTITUDES + ['max_coaching_aptitude', 'total_coaching_aptitude'])
	elif staff_role == 'goalkeeper_coaching':
		df = goalkeeper_coaching_analysis(df)
		print_top_candidates(df, no_candidates, GK_COACHING_ATTRIBUTES + ['gk_coaching_aptitude'])
	elif staff_role == 'fitness_coaching':
		df = fitness_coaching_analysis(df)
		print_top_candidates(df, no_candidates, FITNESS_COACHING_ATTRIBUTES + ['fitness_coaching_aptitude'])
	elif staff_role == 'head_youth_dev':
		df = head_youth_dev_analysis(df)
		print_top_candidates(df, no_candidates, HEAD_YOUTH_DEV_ATTRIBUTES + ['Preferred Formation', 'Tactical Style', 'Personality', 'head_yth_dev_aptitude'])
	elif staff_role == 'head_coach':
		df = head_coach_analysis(df)
		print_top_candidates(df, no_candidates, HEAD_COACH_ATTRIBUTES + ['Preferred Formation', 'Tactical Style', 'head_coach_aptitude'])

	# Web Output Testing
	table = build_webpage.build_table(df)
	# result = df.head(no_candidates).to_html()
	# print(table)