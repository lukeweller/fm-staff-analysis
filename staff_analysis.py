#!/usr/bin/env python3
import os, sys, time
import pandas as pd

# Save a default filename for the input
DEFAULT_INPUT_FILENAME = './input/rtf/coaching_candidates.rtf'

# Sets default # of top canidates to print
DEFAULT_PRINT_NO = 10

ATTRIBUTES 					= ['Ada', 'Att', 'Def', 'Det', 'Fit', 'GkD', 'GkH', 'GkS', 'Judge A', 'Jud PD', 'Judge P', 'Jud SA', 'Jud TD', 'Dis', 'Man', 'Men', 'Mot', 'Negotiating', 'Phy', 'Prs D', 'SpS', 'TCo', 'Tac Knw', 'Tec', 'Youth']
COACHING_ATTRIBUTES 		= ['Att', 'Def', 'Men', 'Tec', 'TCo', 'Det', 'Dis', 'Mot']
GK_COACHING_ATTRIBUTES 		= ['GkD', 'GkH', 'GkS', 'Det', 'Dis', 'Mot']
FITNESS_COACHING_ATTRIBUTES = ['Fit', 'Det', 'Dis', 'Mot']
HEAD_YOUTH_DEV_ATTRIBUTES 	= ['Judge A', 'Judge P', 'Youth']
COACHING_APTITUDES 			= ['Att-Tec', 'Att-TCo', 'Def-Tec', 'Def-TCo', 'Men-Tec', 'Men-TCo']

# Helper function for skiprows parameter in pandas.read_csv()
# Returns True for all lines numbers to read & returns False for all line numbers to skip
def skip_rows(x):
	if x < 9 or x % 2 == 0:
		return False
	else:
		return True

# Simple wrapper function that calls load_staff_rtf() or load_staff_csv(), depending on state
def load_staff(input_filename, caching):

	cache_filename = './input/csv/' + input_filename[12:-4] + '_cleaned.csv'

	if caching and os.path.exists(cache_filename):
		df = load_staff_csv(cache_filename)
	else:
		df = load_staff_rtf(input_filename)
		df = preprocessing(df)
		if caching:
			write_df_to_csv(df, cache_filename)

	return df

def load_staff_rtf(input_filename):

	try:
		df = pd.read_csv(input_filename, sep = '|', skiprows=lambda x: skip_rows(x), skipinitialspace=True)

	except:
		print('Error: failed to load input file \'{}\' into dataframe'.format(input_filename))
		sys.exit(1)


	return df

def load_staff_csv(input_filename):

	load_csv_start_time = time.time()

	try:
		df = pd.read_csv(input_filename)

		print('time to load \'{}\' into dataframe: {:.3f}s'.format(input_filename, time.time() - load_csv_start_time))
	
	except:
		print('error: failed to load input file \'./{}\' into the df'.format(input_filename))
		
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

	for col in df.columns:
		if col in ATTRIBUTES:
			df[col] = pd.to_numeric(df[col])

	print('total preprocessing time: {:.3f}s'.format(time.time() - preprocessing_start_time))

	return df

def write_df_to_csv(df, cache_filename):

	write_df_to_csv_start_time = time.time()

	df.to_csv(cache_filename, index=False)

	print('time to write cleaned data to file: {:.3f}s'.format(time.time() - write_df_to_csv_start_time))

def overall_analysis(df):

	df['sum_all_attributes'] = sum(df[attribute] for attribute in ATTRIBUTES)

	df = df.sort_values(by='sum_all_attributes', ascending=False)

	return df

def coaching_analysis(df, sort_by='max_coaching_aptitude'):
	
	df['mental_sum'] = df['Det'] + df['Dis'] + df['Mot']

	for coaching_area in ['Att', 'Def', 'Men']:
		for coaching_style in ['Tec', 'TCo']:
			df[coaching_area + '-' + coaching_style] = df['mental_sum'] + df[coaching_area] + df[coaching_style]

	df['max_coaching_aptitude'] = df[COACHING_APTITUDES].max(axis=1)
	df['total_coaching_aptitude'] = sum(df[_] for _ in COACHING_APTITUDES)

	df = df.sort_values(by=sort_by, ascending=False)
	
	return df

def goalkeeper_coaching_analysis(df):

	df['gk_coaching_aptitude'] = sum(df[_] for _ in GK_COACHING_ATTRIBUTES)
	
	df = df.sort_values(by='gk_coaching_aptitude', ascending=False)
	
	return df

def fitness_coaching_analysis(df):

	df['fitness_coaching_aptitude'] = sum(df[_] for _ in FITNESS_COACHING_ATTRIBUTES)
	
	df = df.sort_values(by='fitness_coaching_aptitude', ascending=False)
	
	return df

def head_youth_dev_analysis(df):

	df['head_yth_dev_aptitude'] = sum(df[_] for _ in HEAD_YOUTH_DEV_ATTRIBUTES)
	
	df = df.sort_values(by='head_yth_dev_aptitude', ascending=False)
	
	return df

def print_top_candidates(df, no_candidates, metrics):
	# Overrides the default table break for pandas
	pd.set_option('display.max_columns', None)

	print(df[metrics + ['Name']].head(no_candidates))

def print_help_msg(exit_status):
	print('Usage:\n'
		  '	1. Import custom view file (`./views/All.fmf`) into the \'Staff Search\' page while in FM\n'
		  '	2. Copy all view data (ctrl-A, ctrl-P) and save data as a text file to `./input/All.rtf`\n'
		  '	3. Use `./staff-search.py` to analyze coaches and print top canidates\n'
		  'Options:\n'
		  '	-i, --input\n'
		  '		specify the name of the input file; e.g., ./staff-search.py -i [filename]\n'
		  '	-n, --number\n'
		  '		specify number of top canidates to print; e.g., ./staff-search.py -n [number]\n'
		  '	-o, --overall\n'
		  '		sort coaches by sum of all attributes\n'
		  '	-c. --coaching\n'
		  '		sort coaches by their max coaching aptitude\n'
		  '	-gk, --coaching\n'
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
	caching = False
	staff_role = ''
	sort_by = 'max_coaching_aptitude'

	# Iterate through args
	while len(args) > 0:
		arg = args.pop(0)
		if arg == '-h' or arg == '--help':
			print_help_msg(0)
		if arg == '-i' or arg == '--input':
			input_filename = args.pop(0)
		elif arg == '-n' or arg == '--number':
			no_candidates = int(args.pop(0))
		elif arg == '-e' or arg == '-enable-caching':
			caching = True
		elif arg == '-o' or arg == '--overall':
			staff_role = 'overall'
		elif arg == '-c' or arg =='--coaching':
			staff_role = 'coaching'
		elif arg == '-tc' or arg =='--total-coaching':
			staff_role = 'coaching'
			sort_by = 'total_coaching_aptitude'
		elif arg == '-gk' or arg == '--goalkeeper':
			staff_role = 'goalkeeper_coaching'
		elif arg == '-f' or arg == '--fitness':
			staff_role = 'fitness_coaching'
		elif arg == '-yd' or arg == '--youth-dev':
			staff_role = 'head_youth_dev'
		else:
			print('error: failed to recognize argument \'{}\' while parsing command-line arguments'.format(arg))
			print_help_msg(1)

	df = load_staff(input_filename, caching)

	if staff_role == 'overall' or staff_role == '':
		df = overall_analysis(df)
		print_top_candidates(df, no_candidates, ATTRIBUTES + ['sum_all_attributes'])
	elif staff_role == 'coaching':
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
