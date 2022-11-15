# read_filtering
Scripts for cleaning of raw read files, human read filtering etc.


### Usage:

##If you just want to run read-scrubber on a batch of reads use:
 
*source activate env_sra-human-scrubber*
*python3 batch_sra-human-scrubber.py -i input_fastq_dir -o output_fastq_dir*
 
It uses the same regex for read detection as bifrost so should match all the correct names.
 
 
##If you need to upload data to ENA:
 
*source activate env_sra-human-scrubber*
*python3 batch_sra-human-scrubber.py -i [input_fastq_dir] -o [output_fastq_dir] --rename_for_ENA --species [Species name] --taxid [TaxID] -m ENA_metadata.csv*


Files will be renamed to match format used in ena_submission.py and ENA_metadata.csv can be used as data file.
