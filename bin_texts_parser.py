#!/usr/bin/env python2.7
# (c) flatz

import string
import sys, os
import argparse
import distutils.dir_util

#
# #
# # #
# # # # bin texts parser
# # #
# #
#

controls = (
	[
		'\a'# - Bell (speaker beeps)
        , '\b'# - Backspace (non-erase)
        , '\f'# - Form feed/clear screen
        , '\n'# - New line
        , '\r'# - Carriage Return
        , '\t'# - Tab
        , '\v'# - Vertical tab
	]
)

spaces = (
    [
        ' '
    ]
)

symbols = (
    [
        '!'
        , '"'
        , '#'
        , '$'
        , '%'
        , '&'
        , '\''
        , '('
        , ')'
        , '*'
        , '+'
        , ','
        , '-'
        , '.'
        , '/'
        , ':'
        , ';'
        , '<'
        , '='
        , '>'
        , '?'
        , '@'
        , '['
        , '\\'
        , ']'
        , '^'
        , '_'
        , '`'
        , '{'
        , '|'
        , '}'
        , '~'
    ]
)

numbers = (
    [
        '0'
        , '1'
        , '2'
        , '3'
        , '4'
        , '5'
        , '6'
        , '7'
        , '8'
        , '9'
    ]
)

uppers = (
    [
        'A'
        , 'B'
        , 'C'
        , 'D'
        , 'E'
        , 'F'
        , 'G'
        , 'H'
        , 'I'
        , 'J'
        , 'K'
        , 'L'
        , 'M'
        , 'N'
        , 'O'
        , 'P'
        , 'Q'
        , 'R'
        , 'S'
        , 'T'
        , 'U'
        , 'V'
        , 'W'
        , 'X'
        , 'Y'
        , 'Z'
    ]
)

lowers = (
    [
        'a'
        , 'b'
        , 'c'
        , 'd'
        , 'e'
        , 'f'
        , 'g'
        , 'h'
        , 'i'
        , 'j'
        , 'k'
        , 'l'
        , 'm'
        , 'n'
        , 'o'
        , 'p'
        , 'q'
        , 'r'
        , 's'
        , 't'
        , 'u'
        , 'v'
        , 'w'
        , 'x'
        , 'y'
        , 'z'
    ]
)

class MyParser(argparse.ArgumentParser):
	def error(self, message):
		self.print_help()
		sys.stderr.write('\nerror: {0}\n'.format(message))
		sys.exit(2)


def CheckHexText(source, length, add_0x):  # returns the hex text
    source_hex = str(hex(source)[2:])
    source_hex_length = len(source_hex)
    source_hex_index = None
    source_hex_cell = None

    for source_hex_index in range(0, source_hex_length):
        source_hex_cell = source_hex[source_hex_index]

        if (source_hex_cell in string.hexdigits) is False:
            source_hex = source_hex[:source_hex_index]

            break

    result = str(source_hex.zfill(length))

    if add_0x is True:
        result = "0x" + result

    return result

def check_ranges():
	global numbers

	global args

	global ranges

	global ranges_text

	result = None

	ranges_texts = args.ranges.split(',')
	ranges_texts_fixed = []
	ranges_texts_fixed_amount = 0

	for range_text in ranges_texts:
		min_text = ""
		min_text_length = 0
		min = 0

		max_text = ""
		max_text_length = 0
		max = 0

		range_text_splitted = filter(None, range_text.split('-'))
		range_text_splitted_length = len(range_text_splitted)

		if range_text_splitted_length > 0:
			range_text_splitted_min = range_text_splitted[0]

			for range_text_splitted_min_cell in range_text_splitted_min:
				if range_text_splitted_min_cell in numbers:
					min_text += range_text_splitted_min_cell
					min_text_length += 1
					
			if min_text_length > 0:
				min = int(min_text, 10)
				
				if range_text_splitted_length > 1:
					range_text_splitted_max = range_text_splitted[1]

					for range_text_splitted_max_cell in range_text_splitted_max:
						if range_text_splitted_max_cell in numbers:
							max_text += range_text_splitted_max_cell
							max_text_length += 1
				else:
					max_text = min_text
					max_text_length = min_text_length
					
				if max_text_length > 0:
					max = int(max_text, 10)

					range = []

					range.append(min)
					range.append(max)

					ranges.append(range)

	for range in ranges:
		ranges_texts_fixed.append(str(range[0]) + "-" + str(range[1]))
		ranges_texts_fixed_amount += 1

	if ranges_texts_fixed_amount > 0:
		ranges_text = ", ".join(ranges_texts_fixed)

		result = True
	else:
		result = False

	return result

def add_text(location, source_text, source_text_length):
	result = [location, source_text_length, "".join(source_text)]

	return result


def print_ranges_help():
	print("ranges instructions:")
	print(
		"each range is min and max amounts of characters in a single text"
		+ ", set max as 0 for infinite max, the format is \"minA-maxA, minB-maxB...\""
		+ ", if its just 1 range then \"minA-maxA\" would work as well (or without any spaces)"
		+ ", you can also use a range as a single number, for example \"5, 6-13\""
		+ ", in this example we have 2 ranges, the first range is 5-5 (exactly 5 characters), and in the second range it's 6-13"
	)

Debug = False

parser = MyParser(description='bin texts parser')

# note :
# if requiring 2 groups of characters they work together in an "or" statement
# for example if requiring both lowers and uppers, then require a text to at least have 1 lower or upper letter in order for it to get added
		
if Debug is False:
	parser.add_argument('--input', required=False, type=str, help='bin file')
	parser.add_argument('--output', required=False, default="", type=str, help='new text file')
	parser.add_argument('--dry-run', required=False, default=False, action='store_true', help='if inserted then nothing will be written to the output file')
	parser.add_argument('--verbose', required=False, default=False, action='store_true', help='detailed printing')
	parser.add_argument('--ranges', required=False, default="0-0", type=str, help=("use --ranges-help in order to see usage"))
	parser.add_argument('--ranges-help', required=False, default=False, action='store_true')
	parser.add_argument('--not-controls', required=False, default=False, action='store_true', help='do not define controls as text')
	parser.add_argument('--not-spaces', required=False, default=False, action='store_true', help='do not define spaces as text')
	parser.add_argument('--not-symbols', required=False, default=False, action='store_true', help='do not define symbols as text')
	parser.add_argument('--not-numbers', required=False, default=False, action='store_true', help='do not define numbers as text')
	parser.add_argument('--not-uppers', required=False, default=False, action='store_true', help='do not define uppers as text')
	parser.add_argument('--not-lowers', required=False, default=False, action='store_true', help='do not define lowers as text')
	parser.add_argument('--require-controls', required=False, default=False, action='store_true', help='require controls in every text')
	parser.add_argument('--require-spaces', required=False, default=False, action='store_true', help='require spaces in every text')
	parser.add_argument('--require-symbols', required=False, default=False, action='store_true', help='require symbols in every text')
	parser.add_argument('--require-numbers', required=False, default=False, action='store_true', help='require numbers in every text')
	parser.add_argument('--require-uppers', required=False, default=False, action='store_true', help='require uppers in every text')
	parser.add_argument('--require-lowers', required=False, default=False, action='store_true', help='require lowers in every text')

	if len(sys.argv) == 1:
		parser.print_usage()
		sys.exit(1)
else:
	parser.add_argument('--input', required=False, default="C:/somefolder/somefile.bin", type=str, help='bin file')
	parser.add_argument('--output', required=False, default="", type=str, help='new text file')
	parser.add_argument('--dry-run', required=False, default=False, action='store_true', help='if inserted then nothing will be written to the output file')
	parser.add_argument('--verbose', required=False, default=False, action='store_true', help='detailed printing')
	parser.add_argument('--ranges', required=False, default="0-0", type=str, help=("use --ranges-help in order to see usage"))
	parser.add_argument('--ranges-help', required=False, default=False, action='store_true')
	parser.add_argument('--not-controls', required=False, default=False, action='store_true', help='do not define controls as text')
	parser.add_argument('--not-spaces', required=False, default=False, action='store_true', help='do not define spaces as text')
	parser.add_argument('--not-symbols', required=False, default=False, action='store_true', help='do not define symbols as text')
	parser.add_argument('--not-numbers', required=False, default=False, action='store_true', help='do not define numbers as text')
	parser.add_argument('--not-uppers', required=False, default=False, action='store_true', help='do not define uppers as text')
	parser.add_argument('--not-lowers', required=False, default=False, action='store_true', help='do not define lowers as text')
	parser.add_argument('--require-controls', required=False, default=False, action='store_true', help='require controls in every text')
	parser.add_argument('--require-spaces', required=False, default=False, action='store_true', help='require spaces in every text')
	parser.add_argument('--require-symbols', required=False, default=False, action='store_true', help='require symbols in every text')
	parser.add_argument('--require-numbers', required=False, default=False, action='store_true', help='require numbers in every text')
	parser.add_argument('--require-uppers', required=False, default=False, action='store_true', help='require uppers in every text')
	parser.add_argument('--require-lowers', required=False, default=False, action='store_true', help='require lowers in every text')

args = parser.parse_args()

if args.ranges_help is True:
	print_ranges_help()
	sys.exit(1)

ranges = []

ranges_text = ""

if check_ranges() is False:
	print("failed to detect the inputted ranges")
	sys.exit(1)

def main():
	global controls
	global spaces
	global symbols
	global numbers
	global uppers
	global lowers

	global parser

	global args

	global ranges

	global ranges_text

	input_file_path = os.path.abspath(args.input).replace('\\','/')

	if not os.path.isfile(input_file_path):
		parser.error('invalid input file: {0}'.format(input_file_path))

	input_file_size = os.path.getsize(input_file_path)

	input_folder_path = os.path.dirname(input_file_path).replace('\\','/')

	if input_folder_path[len(input_folder_path) - 1] == '/':
		input_folder_path = input_folder_path[:-1]

	if args.output == "":
		input_file_name = os.path.basename(input_file_path)
		input_file_name_length = len(input_file_name)
		input_file_name_splitted = input_file_name.split(".")
		input_file_name_splitted_amount = len(input_file_name_splitted)
		input_file_name_extension = input_file_name_splitted[input_file_name_splitted_amount - 1]
		input_file_name_extension_length = len(input_file_name_extension)
		input_file_name_without_extension = input_file_name[:input_file_name_length - input_file_name_extension_length - 1]

		output_file_name_extension = "txt"
		output_file_name_without_extension = input_file_name_without_extension + '-' + "text"

		output_file_name = output_file_name_without_extension + '.' + output_file_name_extension

		output_folder_path = input_folder_path

		output_file_path = output_folder_path + "/" + output_file_name
	else:
		output_file_path = os.path.abspath(args.output).replace('\\','/')

		output_folder_path = os.path.dirname(output_file_path).replace('\\','/')
	
	if args.dry_run is False:
		distutils.dir_util.mkpath(output_folder_path)
	
	if os.path.exists(output_file_path) and not os.path.isfile(output_file_path):
		parser.error('invalid output file: {0}'.format(output_file_path))
	
	print(
		"Input File:" + ' ' + input_file_path + "\n"
		+ "Output:" + ' ' + output_file_path + "\n"
		+ "Dry Run:" + ' ' + ("True" if args.dry_run is True else "False") + "\n"
		+ "Verbose:" + ' ' + ("True" if args.verbose is True else "False") + "\n"
		+ "Ranges:" + ' ' + ranges_text + "\n"
		+ "Ranges Help:" + ' ' + ("True" if args.ranges_help is True else "False") + "\n"
		+ "Include Controls:"+ ' ' + ("False" if args.not_controls is True else "True") + "\n"
		+ "Include Spaces:"+ ' ' + ("False" if args.not_spaces is True else "True") + "\n"
		+ "Include Symbols:"+ ' ' + ("False" if args.not_symbols is True else "True") + "\n"
		+ "Include Numbers:"+ ' ' + ("False" if args.not_numbers is True else "True") + "\n"
		+ "Include Uppers:"+ ' ' + ("False" if args.not_uppers is True else "True") + "\n"
		+ "Include Lowers:"+ ' ' + ("False" if args.not_lowers is True else "True")
		+ "Require Controls:"+ ' ' + ("True" if args.require_controls is True else "False") + "\n"
		+ "Require Spaces:"+ ' ' + ("True" if args.require_spaces is True else "False") + "\n"
		+ "Require Symbols:"+ ' ' + ("True" if args.require_symbols is True else "False") + "\n"
		+ "Require Numbers:"+ ' ' + ("True" if args.require_numbers is True else "False") + "\n"
		+ "Require Uppers:"+ ' ' + ("True" if args.require_uppers is True else "False") + "\n"
		+ "Require Lowers:"+ ' ' + ("True" if args.require_lowers is True else "False")
	)

	print("")
	print('processing text file: {0}'.format(output_file_path))

	Headers = None
	Fields = None
	Field = None

	AddressesLength = 8#16
	SizeLength = 8#16

	input_file_data = None
	input_file_data_size = None
	input_file_data_cell = None

	output_file_data_list = None
	output_file_data_list_amount = 0
	output_file_data_list_cell = None
	output_file_data = None

	texts = []
	texts_amount = 0
	text = None

	buffer_size = 512
	buffer_index = None

	location = 0

	current_text_list = []
	current_text_length = 0

	found_controls = False
	found_spaces = False
	found_symbols = False
	found_numbers = False
	found_uppers = False
	found_lowers = False
	
	with open(input_file_path, 'rb') as inpf:
		while location < input_file_size:
			if location + buffer_size > input_file_size:
				input_file_data = inpf.read(input_file_size - location)
				input_file_data_size = input_file_size - location
			else:
				input_file_data = inpf.read(buffer_size)
				input_file_data_size = buffer_size

			buffer_index = 0

			while buffer_index < buffer_size:
				if buffer_index < input_file_data_size:
					input_file_data_cell = input_file_data[buffer_index]
				else:
					input_file_data_cell = None

				if (
					args.not_controls is False and input_file_data_cell in controls
					or args.not_spaces is False and input_file_data_cell in spaces
					or args.not_symbols is False and input_file_data_cell in symbols
					or args.not_numbers is False and input_file_data_cell in numbers
					or args.not_uppers is False and input_file_data_cell in uppers
					or args.not_lowers is False and input_file_data_cell in lowers
					):
					for range in ranges:
						min = range[0]
						max = range[1]

						if current_text_length < max or max == 0:
							if input_file_data_cell in controls:
								found_controls = True
							elif input_file_data_cell in spaces:
								found_spaces = True
							elif input_file_data_cell in symbols:
								found_symbols = True
							elif input_file_data_cell in numbers:
								found_numbers = True
							elif input_file_data_cell in uppers:
								found_uppers = True
							elif input_file_data_cell in lowers:
								found_lowers = True

							if input_file_data_cell in controls and input_file_data_cell != '\t':# allow only the '\t' control to get added as a character
								current_text_list.append(' ')
							else:
								current_text_list.append(input_file_data_cell)

							current_text_length += 1

							break
				else:
					if current_text_length > 0:
						if (
							args.require_controls is False
							and args.require_spaces is False
							and args.require_symbols is False
							and args.require_numbers is False
							and args.require_uppers is False
							and args.require_lowers is False
							or (
								(args.require_controls is True and found_controls is True)
								or (args.require_spaces is True and found_spaces is True)
								or (args.require_symbols is True and found_symbols is True)
								or (args.require_numbers is True and found_numbers is True)
								or (args.require_uppers is True and found_uppers is True)
								or (args.require_lowers is True and found_lowers is True)
								)
							):
							for range in ranges:
								min = range[0]
								max = range[1]

								if current_text_length >= min and (current_text_length <= max or max == 0):
									text = (
										add_text(
											location
											, current_text_list
											, current_text_length
										)
									)

									texts.append(text)
									texts_amount += 1

									break

						current_text_list = []
						current_text_length = 0

						found_controls = False
						found_spaces = False
						found_symbols = False
						found_numbers = False
						found_uppers = False
						found_lowers = False

				location += 1

				buffer_index += 1

		if current_text_length > 0:
			if (
				args.require_controls is False
				and args.require_spaces is False
				and args.require_symbols is False
				and args.require_numbers is False
				and args.require_uppers is False
				and args.require_lowers is False
				or (
					(args.require_controls is True and found_controls is True)
					or (args.require_spaces is True and found_spaces is True)
					or (args.require_symbols is True and found_symbols is True)
					or (args.require_numbers is True and found_numbers is True)
					or (args.require_uppers is True and found_uppers is True)
					or (args.require_lowers is True and found_lowers is True)
					)
				):
				for range in ranges:
					min = range[0]
					max = range[1]

					if current_text_length >= min and (current_text_length <= max or max == 0):
						text = (
							add_text(
								location
								, current_text_list
								, current_text_length
							)
						)

						texts.append(text)
						texts_amount += 1

						break

			current_text_list = []
			current_text_length = 0

			found_controls = False
			found_spaces = False
			found_symbols = False
			found_numbers = False
			found_uppers = False
			found_lowers = False

	if texts_amount > 0:
		print("")
		print("Found" + ' ' + str(texts_amount) + ' ' + "texts")

		output_file_data_list = []

		Headers = []
								
		Headers.append("Input File Path")
		Headers.append("Output File Path")

		Fields = []

		Fields.append(Headers[0] + ':' + ' ' + input_file_path)
		Fields.append(Headers[1] + ':' + ' ' + output_file_path)

		for Field in Fields:
			output_file_data_list.append(Field)

		output_file_data_list.append("")

		Headers = []
								
		Headers.append("Found texts")

		Fields = []

		Fields.append(Headers[0] + ':' + ' ' + str(texts_amount))

		for Field in Fields:
			output_file_data_list.append(Field)

		output_file_data_list.append("")

		Headers = []
								
		Headers.append("Location")
		Headers.append("Size")
		Headers.append("Text")

		Fields = []

		Fields.append(None)
		Fields.append(None)
		Fields.append(None)

		for text in texts:
			Fields[0] = Headers[0] + ':' + ' ' + CheckHexText(text[0], AddressesLength, True)
			Fields[1] = Headers[1] + ':' + ' ' + CheckHexText(text[1], SizeLength, True)
			Fields[2] = Headers[2] + ':' + ' ' + text[2]

			output_file_data_list_cell = '\t'.join(Fields)
			output_file_data_list.append(output_file_data_list_cell)
			output_file_data_list_amount += 1

			if args.verbose is True:
				print(output_file_data_list_cell)
	else:
		print("")
		print("Didn't find any texts")

	if output_file_data_list_amount > 0:
		output_file_data = "\r\n".join(output_file_data_list)

		if args.dry_run is False:
			with open(output_file_path, 'w') as tf:
				tf.write(output_file_data)
	else:
		print("")
		print("Not writing to the output file, as no texts have been found")
		
	print("")
	print('finished processing:' + ' ' + output_file_path)

main()
