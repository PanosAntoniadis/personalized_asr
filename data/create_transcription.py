import os
import argparse

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='''
        Tool for creating the transcription file of a speech dataset in Sphinx format.
    ''')
    required = parser.add_argument_group('required arguments')
    required.add_argument(
        '--input', help="Folder that contains the messages", required=True)
    required.add_argument(
        '--name', help="Basename of the sound files", required=True)
    required.add_argument(
        '--output', help="Output directory", required=True)

    args = parser.parse_args()
    input_dir = args.input
    name = args.name
    output_dir = args.output

    with open(os.path.join(output_dir, 'transcriptions'), 'w') as w:
        for message in sorted(os.listdir(input_dir)):
            id = message.split(name + '_')[-1]
            with open(os.path.join(input_dir, message), 'r') as f:
                w.write(f.read().replace("\n", " "))
                w.write(' (' + name + '_' + str(id) + ')')
                w.write('\n')
