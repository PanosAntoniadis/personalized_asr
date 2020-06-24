import os
import argparse

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for creating IDs file of a speech dataset in Sphinx format.
    ''')

    required = parser.add_argument_group('required arguments')

    required.add_argument(
        '--name', help="Basename of the sound files", required=True)
    required.add_argument(
        '--total', help="Total number of files", required=True, type=int)
    required.add_argument(
        '--output', help="Output directory", required=True)

    args = parser.parse_args()
    name = args.name
    total = args.total
    output_dir = args.output

    total_str = str(total - 1)
    with open(os.path.join(output_dir, "fileids"), 'w') as f:
        for i in range(total):
            i_zeroed = str(i).rjust(len(total_str), '0')
            f.write(name + '_' + str(i_zeroed) + '\n')
