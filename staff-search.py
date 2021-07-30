#!/usr/bin/env python3
import io, sys
import pandas as pd
# import matplotlib.pyplot as plt

# Input file should be stored in ./input/ as 'All.rtf'
INPUT_FILENAME = './input/All.rtf'

# Use view './views/All.fmf' in order to create input file
VIEW_FILENAME = './views/All.fmf'

ATTRIBUTES = ['Ada', 'Att', 'Def', 'Det', 'Fit', 'GkD', 'GkH', 'GkS', 'Judge A', 'Jud PD', 'Judge P', 'Jud SA', 'Jud TD', 'Dis', 'Man', 'Men', 'Mot', 'Negotiating', 'Phy', 'Prs D', 'SpS', 'TCo', 'Tac Knw', 'Tec', 'Youth']

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

def coach_analysis(df):
	
	df['mental_sum'] = df['Mot'] + df['Det'] + df['Dis']
	df['area_max'] = df[['Att','Def','Men']].max(axis=1)
	df['style_max'] = df[['Tec','TCo']].max(axis=1)

	df['simple_sum'] = df['mental_sum'] + df['area_max'] + df['style_max']

	df['mental_mean'] = df['mental_sum'] / 3
	df['coaching_mean'] = (df['area_max'] + df['style_max']) / 2

	df = df.sort_values(by='coaching_mean', ascending=False)
	
	return df

def overall_analysis(df):

	df['sum_all_attributes'] = sum(df[attribute] for attribute in ATTRIBUTES)

	df = df.sort_values(by='sum_all_attributes', ascending=False)

	return df

if __name__ == '__main__':

	all_staff_df = load_all_staff()
	# all_staff_df = coach_analysis(all_staff_df)

	all_staff_df = overall_analysis(all_staff_df)

	print(all_staff_df[ATTRIBUTES + ['sum_all_attributes', 'Name']])




