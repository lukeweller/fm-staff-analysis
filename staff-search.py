#!/usr/bin/env python3
import io, sys
import pandas as pd
# import matplotlib.pyplot as plt

# Input file should be stored in ./input/ as 'All.rtf'
INPUT_FILENAME = './input/All.rtf'

# Use view './views/All.fmf' in order to create input file
VIEW_FILENAME = './views/All.fmf'

ATTRIBUTES = ['Ada', 'Att', 'Def', 'Det', 'Fit', 'GkD', 'GkH', 'GkS', 'Judge A', 'Jud PD', 'Judge P', 'Jud SA', 'Jud TD', 'Dis', 'Man', 'Men', 'Mot', 'Negotiating', 'Phy', 'Prs D', 'SpS', 'TCo', 'Tac Knw', 'Tec', 'Youth']
COACHING_ATTRIBUTES = ['Att', 'Def', 'Men', 'Tec', 'TCo', 'Det', 'Dis', 'Mot']
COACHING_APTITUDES = ['Att-Tec', 'Att-TCo', 'Def-Tec', 'Def-TCo', 'Men-Tec', 'Men-TCo']

def load_all_staff():

	try:
		with open(INPUT_FILENAME) as input_file:
			raw_input = input_file.read()
	except:
		print('Error: failed to open input file: \'./input/All.rtf\'')
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

def coaching_analysis(df):
	
	df['mental_sum'] = + df['Det'] + df['Dis'] + df['Mot']

	for coaching_area in ['Att', 'Def', 'Men']:
		for coaching_style in ['Tec', 'TCo']:
			df[coaching_area + '-' + coaching_style] = df['mental_sum'] + df[coaching_area] + df[coaching_style]

	df['max_coaching_aptitude'] = df[COACHING_APTITUDES].max(axis=1)
	df['total_coaching_aptitude'] = sum(df[_] for _ in COACHING_APTITUDES)

	df = df.sort_values(by='max_coaching_aptitude', ascending=False)
	
	return df

def overall_analysis(df):

	df['sum_all_attributes'] = sum(df[attribute] for attribute in ATTRIBUTES)

	df = df.sort_values(by='sum_all_attributes', ascending=False)

	return df

def print_top_candidates(df, no_candidates, metrics):
	# Overrides the default table break for pandas
	pd.set_option('display.max_columns', None)

	print(df[['Name'] + metrics].head(no_candidates))

if __name__ == '__main__':

	df = load_all_staff()
	df = coaching_analysis(df)
	# df = overall_analysis(df)

	print_top_candidates(df, 10, COACHING_APTITUDES + ['max_coaching_aptitude', 'total_coaching_aptitude'])
