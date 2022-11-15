#!/usr/bin/env python3

import os
import sys
import re
import argparse

parser = argparse.ArgumentParser(description='Run sra-human-scrubber to remove human reads on all raw read files in a folder. Legal file formats are fastq and fastq.gz')
parser.add_argument('-i', dest="input", metavar='input', type=str,
                    help='Input folder with read files in fastq or fastq.gz format')
parser.add_argument('-o', dest="output", metavar='Output folder', type=str,
                    help='Output folder containing reads scrubbed from human reads')
parser.add_argument('-p', dest="partition", metavar='partition',type=str, default = "project", help='Partition to run jobs on. Default \"project\"')
parser.add_argument("-r", "--rename_for_ENA",dest='rename_for_ENA',help="Also rename output reads to match name format required by ENA upload script",action='store_true',required=False,default=False)
parser.add_argument('-s', dest="species", metavar='species',type=str, default = "SPECIES_PLACEHOLDER", help='Species name for creating ENA upload data sheet',required=False)
parser.add_argument('-t', dest="taxid", metavar='taxid',type=str, default = "TAXID_PLACEHOLDER", help='TaxID for creating ENA upload data sheet',required=False)
parser.add_argument('-m', dest="metadata", metavar='metadata',type=str, default = "ENA_data_sheet.csv", help='File name for ENA data upload sheet',required=False)
args = parser.parse_args()


scratch_dir = "/scratch"

fastq_gz_regex = "(?P<sample_name>.+?)(?P<sample_number>(_S[0-9]+)?)(?P<lane>(_L[0-9]+)?)_(?P<paired_read_number>R[1|2])(?P<set_number>(_[0-9]+)?)(?P<file_extension>\.fastq.gz)"
fastq_regex = "(?P<sample_name>.+?)(?P<sample_number>(_S[0-9]+)?)(?P<lane>(_L[0-9]+)?)_(?P<paired_read_number>R[1|2])(?P<set_number>(_[0-9]+)?)(?P<file_extension>\.fastq)"


input_files = os.listdir(args.input)

r1_files = []
r2_files = []
for f in input_files:
	input_file = os.path.join(args.input,f)
	scratch_file = os.path.join(scratch_dir,f)
	fastq_match = re.search(fastq_regex, f)
	fastq_gz_match = re.search(fastq_gz_regex, f)
	if f.endswith('.fastq.gz') and fastq_gz_match:
		if args.rename_for_ENA:
			output_file = os.path.join(args.output,fastq_gz_match.group('sample_name')+'.'+fastq_gz_match.group('paired_read_number')+'.fastq.gz')
			if fastq_gz_match.group('paired_read_number') == "R1":
				r1_files.append(fastq_gz_match.group('sample_name'))
			if fastq_gz_match.group('paired_read_number') == "R2":
				r2_files.append(fastq_gz_match.group('sample_name'))
		else:
			output_file = os.path.join(args.output,f)
		cmd = "zcat " + input_file+" | scrub.sh -o - | gzip > " + scratch_file + "; mv " + scratch_file + " " + output_file
		sbatch_cmd = "sbatch -D . -c 8 --mem=16G --time=4:00:00 -J \"sra-human-scrubber\" -p "+args.partition+" --wrap=\""+cmd+"\""
		os.system(sbatch_cmd)
	elif f.endswith('.fastq') and re.search(fastq_regex, f):
		if args.rename_for_ENA:
			output_file = os.path.join(args.output,fastq_gz_match.group('sample_name')+'.'+fastq_gz_match.group('paired_read_number')+'.fastq.gz')
			if fastq_gz_match.group('paired_read_number') == "R1":
				r1_files.append(fastq_gz_match.group('sample_name'))
			if fastq_gz_match.group('paired_read_number') == "R2":
				r2_files.append(fastq_gz_match.group('sample_name'))
		else:
			output_file = os.path.join(args.output,f)
		cmd = "scrub.sh -i " + input_file +  " -o - | gzip > " + scratch_file + "; mv " + scratch_file + " " + output_file
		sbatch_cmd = "sbatch -D . -c 8 --mem=16G --time=4:00:00 -J \"sra-human-scrubber\" -p "+args.partition+" --wrap=\""+cmd+"\""
		os.system(sbatch_cmd)
	else:
		print("Ignoring file " + f + " because file name does not match file name regex for read files")

if args.rename_for_ENA:
	if args.species and args.taxid and args.metadata:
		species = args.species.replace("_"," ")
		metadata_lines = ["SAMPLE,TAXON_ID,SCIENTIFIC_NAME,DESCRIPTION"]
		for r1 in r1_files:
			if r1 in r2_files:
				metadata_lines.append(r1+","+args.taxid+","+species+",")
		o = open(args.metadata,'w')
		o.write("\n".join(metadata_lines))
		o.close()
		print("Found "+str(len(r1_files))+" R1 files")
		print("Found "+str(len(r2_files))+" R2 files")
		print("Printed metadata for "+str(len(metadata_lines)-1)+" isolates with both R1 and R2 files")
	else:
		print("Missing information on species (--species), taxid (--taxid) or name of metadata output file (--metadata). No metadata printed")
	


