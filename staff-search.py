#!/usr/bin/env python3
import io, sys
import pandas as pd
# import matplotlib.pyplot as plt

# Input file should be stored in ./input/ as 'All.rtf'
INPUT_FILENAME = './input/All.rtf'

# Use view './views/All.fmf' in order to create input file
# VIEW_FILENAME = './views/All.fmf'

# Sets default # of top canidates to print
NO_CANIDATES = 10

ATTRIBUTES = ['Ada', 'Att', 'Def', 'Det', 'Fit', 'GkD', 'GkH', 'GkS', 'Judge A', 'Jud PD', 'Judge P', 'Jud SA', 'Jud TD', 'Dis', 'Man', 'Men', 'Mot', 'Negotiating', 'Phy', 'Prs D', 'SpS', 'TCo', 'Tac Knw', 'Tec', 'Youth']
COACHING_ATTRIBUTES = ['Att', 'Def', 'Men', 'Tec', 'TCo', 'Det', 'Dis', 'Mot']
GK_COACHING_ATTRIBUTES = ['GkD', 'GkH', 'GkS', 'Det', 'Dis', 'Mot']
FITNESS_COACHING_ATTRIBUTES = ['Fit', 'Det', 'Dis', 'Mot']
HEAD_YOUTH_DEV_ATTRIBUTES = ['Judge A', 'Judge P', 'Youth']
COACHING_APTITUDES = ['Att-Tec', 'Att-TCo', 'Def-Tec', 'Def-TCo', 'Men-Tec', 'Men-TCo']

def load_all_staff(input_filename):

	try:
		with open(input_filename, 'r') as input_file:
			raw_input = input_file.read()
	except:
		print('Error: failed to open input file: {}'.format(input_filename))
		sys.exit(1)

	input_string = ''

	# Converts FM's custom .rtf formatting into .csv so we
	# can get pandas.read_csv() to do all the work for us
	for line in raw_input.split('\n'):
		# FM uses the opening and closing tags of |c:disabled| and |/c| to designate
		# italics when exporting to the .rtf format
		# In order to properly split the line based on the '|' character, those tags must be cleaned
		line = line.replace('|c:disabled|', '').replace('|/c|','')
		line_object = [item.strip() for item in line.split('|')[1:-1]]

		if len(line_object) <= 1:
			# Empty or dashed-only line
			continue
		else:
			for item in line_object:
				# .replace(',', '') strips commas from salary values
				# without this cleaning, pandas can't properly read .csv input
				input_string += item.replace(',', '') + ','
			# Cleans up extra comma left at the end of rows
			input_string = input_string[:-1]
			input_string += '\n'

	# Cleans up extra newline char left at the end of input string
	input_string = input_string[:-1]

	# io.StringIO() allows pandas.read_csv() to read the string input as though
	# it were a filestream
	return pd.read_csv(io.StringIO(input_string)) 

def overall_analysis(df):

	df['sum_all_attributes'] = sum(df[attribute] for attribute in ATTRIBUTES)

	df = df.sort_values(by='sum_all_attributes', ascending=False)

	return df

def coaching_analysis(df):
	
	df['mental_sum'] = df['Det'] + df['Dis'] + df['Mot']

	for coaching_area in ['Att', 'Def', 'Men']:
		for coaching_style in ['Tec', 'TCo']:
			df[coaching_area + '-' + coaching_style] = df['mental_sum'] + df[coaching_area] + df[coaching_style]

	df['max_coaching_aptitude'] = df[COACHING_APTITUDES].max(axis=1)
	df['total_coaching_aptitude'] = sum(df[_] for _ in COACHING_APTITUDES)

	df = df.sort_values(by='max_coaching_aptitude', ascending=False)
	
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

def print_help_msg():
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

if __name__ == '__main__':

	args = sys.argv[1:]

	input_filename = INPUT_FILENAME
	no_candidates = NO_CANIDATES

	# Loads default input file if no input argument is given
	if '-i' not in args and '--input' not in args:
		df = load_all_staff(input_filename)

	# Iterate through args
	while len(args) > 0:
		arg = args.pop(0)
		if arg == '-h' or arg == '--help':
			print_help_msg()
			exit(0)
		if arg == '-i' or arg == '--input':
			input_filename = args.pop(0)
			df = load_all_staff(input_filename)
		elif arg == '-n' or arg == '--number':
			no_candidates = int(args.pop(0))
		elif arg == '-o' or arg == '--overall':
			df = overall_analysis(df)
			print_top_candidates(df, no_candidates, ATTRIBUTES + ['sum_all_attributes'])
		elif arg == '-c' or arg == '--coaching':
			df = coaching_analysis(df)
			print_top_candidates(df, no_candidates, COACHING_APTITUDES + ['max_coaching_aptitude', 'total_coaching_aptitude'])
		elif arg == '-gk' or arg == '--goalkeeper-coaching':
			df = goalkeeper_coaching_analysis(df)
			print_top_candidates(df, no_candidates, GK_COACHING_ATTRIBUTES + ['gk_coaching_aptitude'])
		elif arg == '-f' or arg == '--fitness-coaching':
			df = fitness_coaching_analysis(df)
			print_top_candidates(df, no_candidates, FITNESS_COACHING_ATTRIBUTES + ['fitness_coaching_aptitude'])
		elif arg == '-yd' or arg == '--head-youth-dev':
			df = head_youth_dev_analysis(df)
			print_top_candidates(df, no_candidates, HEAD_YOUTH_DEV_ATTRIBUTES + ['Preferred Formation', 'Tactical Style', 'Personality', 'head_yth_dev_aptitude'])
		else:
			print('error: failed to recognize argument \'{}\' while parsing command-line arguments'.format(arg))
			exit(1)
