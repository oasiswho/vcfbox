#import modules
from __future__ import print_function

import argparse
import sys

import vcf

#introduction
#Please use python3 to run this scripts
#the scripts can convert vcf to structure,and output diploid and tetraploid only
#this python scripts is adapted from Ludovic Dutoit
#	https://github.com/ldutoit

#2020/12/14 adapted by oasiswho
#Thanks for kind help from Chen'ao Weng
#	https://github.com/oasiswho

#v1.4 add new genotype 2021/05/08

def errprint(*args, **kwargs):
	''' print to stderr not stdout'''
	print(*args, file=sys.stderr, **kwargs)

#Help
parser = argparse.ArgumentParser()
parser.add_argument("input",help="input VCF file")
parser.add_argument("output",help="output STRUCTURE DATA file")

args = parser.parse_args()

dict_alleles = {"0/0": {0:"0",1:"0",2:"-9",3:"-9"},"0|0": {0:"0",1:"0",2:"-9",3:"-9"},"0/1": {0:"0",1:"1",2:"-9",3:"-9"},"0|1":{0:"0",1:"1",2:"-9",3:"-9"},"1/0":{0:"1",1:"0",2:"-9",3:"-9"},"1|0":{0:"1",1:"0",2:"-9",3:"-9"},"1/1":{0:"1",1:"1",2:"-9",3:"-9"},"1|1":{0:"1",1:"1",2:"-9",3:"-9"},"1/0/0/0":{0:"1",1:"0",2:"0",3:"0"},"0/1/0/0":{0:"0",1:"1",2:"0",3:"0"},"0/0/1/0":{0:"0",1:"0",2:"1",3:"0"},"0/0/0/0":{0:"0",1:"0",2:"0",3:"0"},"0/0/0/1":{0:"0",1:"0",2:"0",3:"1"},"0/0/1/1":{0:"0",1:"0",2:"1",3:"1"},"0/1/1/1":{0:"0",1:"1",2:"1",3:"1"},"1/1/1/1":{0:"1",1:"1",2:"1",3:"1"},"1/1/0/1":{0:"1",1:"1",2:"0",3:"1"},"1/0/1/1":{0:"1",1:"0",2:"1",3:"1"},"1/1/1/0":{0:"1",1:"1",2:"1",3:"0"},"0/1/1/0":{0:"0",1:"1",2:"1",3:"0"},"1/0/0/1":{0:"1",1:"0",2:"0",3:"1"},"1/1/0/0":{0:"1",1:"1",2:"0",3:"0"},"1/0/1/0":{0:"1",1:"0",2:"1",3:"0"},"0/1/0/1":{0:"0",1:"1",2:"0",3:"1"},"./.":{0:"-9",1:"-9",2:"-9",3:"-9"},".|.":{0:"-9",1:"-9",2:"-9",3:"-9"},'./././.':{0:"-9",1:"-9",2:"-9",3:"-9"}}
dict_diploid ={"0/0": {0:"0",1:"0",2:"-9",3:"-9"},"0|0": {0:"0",1:"0",2:"-9",3:"-9"},"0/1": {0:"0",1:"1",2:"-9",3:"-9"},"0|1":{0:"0",1:"1",2:"-9",3:"-9"},"1/0":{0:"1",1:"0",2:"-9",3:"-9"},"1|0":{0:"1",1:"0",2:"-9",3:"-9"},"1/1":{0:"1",1:"1",2:"-9",3:"-9"},"1|1":{0:"1",1:"1",2:"-9",3:"-9"},"./.":{0:"-9",1:"-9",2:"-9",3:"-9"},".|.":{0:"-9",1:"-9",2:"-9",3:"-9"}}
dict_tetraploid ={"1/0/0/0":{0:1,1:0,2:0,3:0},"0/1/0/0":{0:0,1:1,2:0,3:0},"0/0/1/0":{0:0,1:0,2:1,3:0},"0/0/0/0":{0:0,1:0,2:0,3:0},"0/0/0/1":{0:0,1:0,2:0,3:1},"0/0/1/1":{0:0,1:0,2:1,3:1},"0/1/1/1":{0:0,1:1,2:1,3:1},"1/1/1/1":{0:1,1:1,2:1,3:1},"1/1/0/1":{0:1,1:1,2:0,3:1},"1/0/1/1":{0:1,1:0,2:1,3:1},"1/1/1/0":{0:1,1:1,2:1,3:0},"0/1/1/0":{0:0,1:1,2:1,3:0},"1/0/0/1":{0:1,1:0,2:0,3:1},"1/1/0/0":{0:1,1:1,2:0,3:0},"1/0/1/0":{0:1,1:0,2:1,3:0},"0/1/0/1":{0:0,1:1,2:0,3:1},'./././.':{0:-9,1:-9,2:-9,3:-9}}

#open the VCF file by using module vcf
input_vcf=vcf.Reader(fsock=None, filename=args.input,  prepend_chr="False", strict_whitespace=False)

list_snps = []

gen_dict = {ind:[] for ind in input_vcf.samples }
diploid_dict = {dip:[] for dip in input_vcf.samples}
tetraploid_dict = {ter:[] for ter in input_vcf.samples}

vcf_count=0

#create genotype
for site in input_vcf:
	list_snps.append( site.CHROM+"_"+str(site.POS)) # chr_pos
	#count SNPs
	vcf_count += 1
	for i in range(len(gen_dict.keys())):
		#for diploid
		if site.samples[i]["GT"] in dict_diploid:
			gen_dict[site.samples[i].sample].append([dict_alleles[site.samples[i]["GT"]]])
			diploid_dict[site.samples[i].sample].append([dict_alleles[site.samples[i]["GT"]]])

		#for teraploid
		if site.samples[i]["GT"] in dict_tetraploid:
			gen_dict[site.samples[i].sample].append([dict_alleles[site.samples[i]["GT"]]])
			tetraploid_dict[site.samples[i].sample].append([dict_alleles[site.samples[i]["GT"]]])

for key in list(diploid_dict.keys()):
	if not diploid_dict.get(key):
		del diploid_dict[key]

for key in list(tetraploid_dict.keys()):
	if not tetraploid_dict.get(key):
		del tetraploid_dict[key]

output = open(args.output,"w")
#output.write("Samples\t"+"\t".join(list_snps)+"\n")

#output to structure
for ind in gen_dict.keys():

	for count in [0, 1, 2, 3]:
		output.write(ind)
		for num in range(len(gen_dict[ind])):
			output.write('\t'+gen_dict[ind][num][0][count])
		output.write('\n')
#print diploid.txt
diploidtxt =open("dipoid.txt", "w")
for diploid in diploid_dict.keys():

	for count in [0, 1, 2, 3]:
		diploidtxt.write(diploid)
		for num in range(len(diploid_dict[diploid])):
			diploidtxt.write('\t'+diploid_dict[diploid][num][0][count])
		diploidtxt.write('\n')
tetraploidtxt =open("tetraploid.txt", "w")
for tetraploid in tetraploid_dict.keys():

	for count in [0, 1, 2, 3]:
		tetraploidtxt.write(tetraploid)
		for num in range(len(tetraploid_dict[tetraploid])):
			tetraploidtxt.write('\t'+tetraploid_dict[tetraploid][num][0][count])
		tetraploidtxt.write('\n')


output.close()
diploidtxt.close()
tetraploidtxt.close()

#print the number of individuals.

print("The number of individuals is "+ str(len(gen_dict)))
#print the number of SNPs.

print("The number of SNPs is " + str(vcf_count))


#Done
sys.exit()