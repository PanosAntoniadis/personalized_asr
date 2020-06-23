import os
import sys
import argparse
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='''
		Tool for creating the language models after clustering
	''')

    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional_arguments')

    required.add_argument(
        '--input', help="Folder that contains the clusters", required=True)
    required.add_argument(
        '--general_lm', help="General language model", required=True)
    required.add_argument(
        '--model_name', help="Name of language models", required=True)
    required.add_argument(
        '--lambda_par', help="Lambda parameter in interpolation", required=True)
    
    args = parser.parse_args()
    input_dir = args.input
    general_lm = args.general_lm
    model_name = args.model_name
    lambda_par = args.lambda_par

    if not input_dir.endswith('/'):
        input_dir = input_dir + '/'

    for cluster in sorted(os.listdir(input_dir)):
        cluster_path = os.path.join(input_dir, cluster)
        if os.path.isdir(cluster_path):
            command = ['ngram-count -interpolate -text', os.path.join(cluster_path, 'corpus'), '-wbdiscount1 -wbdiscount2 -wbdiscount3 -lm', os.path.join(cluster_path, 'adapted.lm')]
            if subprocess.call(" ".join(command), shell=True):
                sys.exit('Error in subprocess')
            command = ['ngram -lm', general_lm, '-mix-lm', os.path.join(cluster_path, 'adapted.lm'), ' -lambda', lambda_par, '-write-lm',  os.path.join(cluster_path, model_name)]
            if subprocess.call(" ".join(command), shell=True):
                sys.exit('Error in subprocess')
