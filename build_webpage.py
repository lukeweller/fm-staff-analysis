#!/usr/bin/env python3
def build_table(df):

	table_head = '<thead><tr style="text-align: right;">'

	for column in df.columns:
		table_head += '<th>{}</th>'.format(column)

	table_head += '</tr></thread>\n'

	table_body = '<tbody>'

	for index, row in df.iterrows():
		table_body += '<tr>'
		for column in df.columns:
			table_body += '<td>{}</td>'.format(row[column]) 
		table_body += '</tr>'

	table_body += '</tbody>'

	return '<table border="1" cellpadding="5px" class="table table-striped">' + table_head + table_body + '</table>'

if __name__ == '__main__':

	print('hello')