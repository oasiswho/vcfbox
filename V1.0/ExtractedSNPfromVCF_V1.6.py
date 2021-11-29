#import modules
from __future__ import print_function
from Bio import SeqIO

import argparse
import sys
import os
import vcf
import copy
import datetime

#Introduction
#Please use python3 to run this script
#the script can extract SNP from singlecopy gene ID and GFF into individual fasta files by using VCF file

#2021/08/25 created by oasiswho

#Thanks for generous help from Mingcheng Wang, who unselfishly provided ideas for this script

#v1.6 fixed some problem when gff is not match with vcf 2021/10/25
#v1.5 added some notice. 2021/09/29
#v1.4 added new function of different ways to keep genes without codons 2021/09/26
#v1.3 added new function of screen gene by SNPs 2021/09/21
#v1.2 added new function of output relaxed-phylip format 2021/09/18
#v1.1 The algorithm is improved and the running time is reduced greatly 2021/09/09
#v1.0 script can output fasta files. 2021/09/08

#record the time
starttime = datetime.datetime.now()
print("The scripts start at "+str(starttime))

def errprint(*args, **kwargs):
	''' print to stderr not stdout'''
	print(*args, file=sys.stderr, **kwargs)


#Help
parser = argparse.ArgumentParser(description='This script can extract SNPs from singlecopy geneID and GFF into individual fasta files by using VCF file')
subparsers = parser.add_subparsers()

parser.add_argument("-input",metavar = 'VCF_file',help="input VCF file ")
parser.add_argument("-gff",metavar = 'GFF_file',help="input GFF file ")
parser.add_argument("-scg",metavar = 'SCG_file',help="input scg file ")
parser.add_argument("-snp",metavar = 'snp_number',type = int ,required= False,help="screen genes under the snp number")


#phy = subparsers.add_parser('phy',help='output phylip format')

parser.add_argument('-phy',action='store_true',help='output sequence with relaxed-phylip format')

#parser.add_argument('-phy',required = False, help = 'output sequence with format phy')

#handle empty gene
#exception handling
def sub_empty_gene(arguments):

	if arguments.keep and arguments.discard:
		print('Error!You can only choose one or other from keep or discard')
		sys.exit()
	if arguments.keep:
		print('You choose to keep the gene')
	if arguments.discard:
		print('You choose to discard the gene')
	if not arguments.keep and not arguments.discard:
		print("You should assign a command for \'keep\' or \'discard\'")
		sys.exit()

empty_gene =subparsers.add_parser('empty', help="Keep the gene with empty codon1-2,codon3, or discard it. Use\'empty -h\' for help")

empty_gene.add_argument('-keep',action='store_true',help='Keep the gene if codon1-2 or codon3 is empty')
empty_gene.add_argument('-discard',action='store_true',help='Discard the gene with empty codon1-2 or codon3')


empty_gene.set_defaults(func=sub_empty_gene)
args = parser.parse_args()

if not hasattr(args, 'func'):
	print('You should use the command \'empty\'. Use \'empty -h\' for help!')
	args = parser.parse_args(['-h'])

args.func(args)

degenerate_base = {
				"AA":"A","AT":"W", "AC":"M", "AG":"R",
				"TT":"T","TA":"W", "TC":"Y", "TG":"K",
				"CC":"C","CA":"M", "CT":"Y", "CG":"S",
				"GG":"G","GA":"R", "GT":"K", "GC":"S"
               }

#mkdir

def mkdir(path):

	folder = os.path.exists(path)

	if not folder:
		os.makedirs(path)
		print('Create folder '+path)

	else:
		print("There has a folder named "+path)

#judge if the snp is degenerate_base
def isDegenerateBase(site):
	if site.gt_bases is None:
		snp_site='N'
		#print('here is an N in site ' + site.sample)
		return 'N'
	else:
		bases=site.gt_bases[0]+site.gt_bases[2]
		snp_site=degenerate_base[bases]
		return snp_site

#open the VCF file by using module vcf
input_vcf=vcf.Reader(fsock=None, filename=args.input,  prepend_chr=False, strict_whitespace=False)
input_first=vcf.Reader(fsock=None, filename=args.input,  prepend_chr=False, strict_whitespace=False)


#####singlecopygene#####
def getSCG():
	scg_list=[]
	input_scg = open(args.scg, 'r')
	for scg_id in input_scg:
		scg_id=scg_id.strip()
		scg_list.append(scg_id)
	input_scg.close()
	return scg_list
#####gff##############
def getGFF():
	input_gff = open(args.gff, 'r')
	chr_dict={}
	CDS_dict={}
	CDS_list=[]


	first='true'
	for line in input_gff:
		line = line.strip().split('\t')
		seq_id, source, type, start, end, score, strand, phrase, attributes = line
		if first =='true':
			chr_id=seq_id
			geneID_flag = attributes.split(';')[0].split('=')[1]+'.1'
			first ='false'
			CDS_flag='false'

		if chr_id ==seq_id:
			if type == 'gene':
				geneID = attributes.split(';')[0].split('=')[1] + '.1'
				if geneID_flag != geneID and CDS_flag == 'true' :
					# SingleCopyID have '.1' in suffix, but gff don't , so I add up it.
					CDS_dict[geneID_flag] = CDS_list
					CDS_list = []
					CDS_flag='false'
					geneID_flag = geneID
				else:
					geneID_flag = geneID

			elif type == 'CDS':
				CDS=[start,end,strand]
				CDS_list.append(CDS)
				CDS_flag='true'
		else :
			if CDS_flag == 'true':
				CDS_dict[geneID_flag] = CDS_list
				CDS_flag = 'false'
				CDS_list = []
			geneID = attributes.split(';')[0].split('=')[1] + '.1'
			geneID_flag = geneID
			chr_dict[chr_id]=CDS_dict
			CDS_dict={}
			chr_id=seq_id
	#when the file ends
	if CDS_flag == 'true':
		CDS_dict[geneID_flag] = CDS_list
		CDS_flag = 'false'
		CDS_list = []
	chr_dict[seq_id]=CDS_dict

	input_gff.close()
	return chr_dict
###################################

#####matchSCGfromGFF####
def matchSCGfromGFF():
	gff_dict = getGFF()
	scg_list=getSCG()
	matchSCG_dict={}
	matchChr_dict={}

	for chr_key in gff_dict:
		for scg in scg_list:
			if scg in gff_dict[chr_key]:
				matchSCG_dict[scg]=gff_dict[chr_key][scg]
		if matchSCG_dict:
			matchChr_dict[chr_key]=matchSCG_dict
			matchSCG_dict={}


	return matchChr_dict
#################################





####vcf position###

def getPosition(sampleID,matchSNP,position,snp_site,chrID,order,matchSCG):
	snplist=[]
	for geneID in list(matchSCG[chrID])[order:]:
		for get in matchSCG[chrID][geneID]:
			if get[2] == '+':
				if position >= int(get[0]) and position <= int(get[1]):
					codon=( position - int(get[0]) +1 ) % 3
					snplist=[snp_site,codon]
					matchSNP[chrID][geneID][sampleID].append(snplist)
					order=list(matchSCG[chrID]).index(geneID)
					return matchSNP,order
				else:
					continue
			elif get[2] == '-':
				if position >= int(get[0]) and position <= int(get[1]):
					codon = (int(get[1]) - position +1) % 3
					snplist=[snp_site,codon]
					matchSNP[chrID][geneID][sampleID].append(snplist)
					order = list(matchSCG[chrID]).index(geneID)
					return matchSNP,order
				else:
					continue

		#del the gene when the snp is matched in this gene, to reduce the computing time
		#del matchSCG[chrID][geneID]
	#if snp not in genes
	return matchSNP,order


#delete empty funciton
def delEmpty(matchSNP):
	delthegene='false'
	for d_chr in matchSNP:
		for d_gene in list(matchSNP[d_chr].keys()):
			for d_snp in matchSNP[d_chr][d_gene]:
				if matchSNP[d_chr][d_gene][d_snp] == []:
					#matchSNP[d_chr][d_gene][d_snp] = 'remove'
					delthegene='true'
					break
				elif args.snp is not None:
					if len(matchSNP[d_chr][d_gene][d_snp])< args.snp:
						delthegene = 'true'
						print("Delete gene " + d_gene + " because its snps number < " + str(args.snp))
						break
					else:
						break
				# if none, just skip the gene
				else:
					break
			if delthegene=='true':
				del matchSNP[d_chr][d_gene]
				delthegene='false'

	return matchSNP

#output function

def outputSNP(matchSNP):
	for chrID in matchSNP:
		for gene in matchSNP[chrID]:
			codon1_2_flag='False'
			codon3_flag='False'
			codon1_2=open("./codon1_2/"+gene+".fasta","w+")
			codon3=open("./codon3/"+gene+".fasta","w+")
			FullCDS=open("./fullCDS/"+gene+".fasta","w+")
			for sampleID in matchSNP[chrID][gene]:
				codon1_2.write('>'+sampleID+'\n')
				codon3.write('>'+sampleID+'\n')
				FullCDS.write('>' + sampleID + '\n')
				for snp in matchSNP[chrID][gene][sampleID]:
					if snp[1]==0:
						codon3.write(snp[0])
						codon3_flag='True'
					elif snp[1]==1 or snp[1]==2:
						codon1_2.write(snp[0])
						codon1_2_flag='True'
					FullCDS.write(snp[0])

				codon1_2.write('\n')
				codon3.write('\n')
				FullCDS.write('\n')

			#save & close
			codon1_2.close()
			codon3.close()
			FullCDS.close()

			#keep gene
			if args.keep:
				if codon1_2_flag == 'True' and codon3_flag == 'True':
					if args.phy:
						phy("codon1_2", gene)
						phy("codon3", gene)
						phy("fullCDS", gene)
				if codon1_2_flag == 'True' and codon3_flag == 'False':
					#delete codon3 gene
					print('Deleted codon3 gene '+ gene + ' because it is empty!')
					os.remove("./codon3/" + gene + ".fasta")
					if args.phy:
						phy("codon1_2", gene)
						phy("fullCDS", gene)
				if codon1_2_flag == 'False' and codon3_flag == 'True':
					#delete codon1_2 gene
					print('Deleted codon1_2 gene ' + gene + ' because it is empty!')
					os.remove("./codon1_2/" + gene + ".fasta")
					if args.phy:
						phy("codon3", gene)
						phy("fullCDS", gene)

			#discard gene
			if args.discard:
				if codon1_2_flag == 'True' and codon3_flag == 'True':
					if args.phy:
						phy("codon1_2", gene)
						phy("codon3", gene)
						phy("fullCDS", gene)
				if codon1_2_flag == 'False' or codon3_flag == 'False':
					#delete all codons gene
					print('Deleted codon1_2/3/fullCDS gene ' + gene + ' because one of them are empty!')
					os.remove("./codon1_2/" + gene + ".fasta")
					os.remove("./codon3/" + gene + ".fasta")
					os.remove("./fullCDS/" + gene + ".fasta")


#relaxed-phylip format output function

def phy(codon,gene):
	codon_records_phy=SeqIO.parse("./"+codon+"/"+gene+".fasta", "fasta")
	codon_count_phy =SeqIO.write(codon_records_phy, "./"+codon+"/"+gene+".phy", "phylip-relaxed")

#main
def main():
	#init
	sample_dict = {}
	matchSCG = matchSCGfromGFF()
	oldchr='old'
	mkdir('codon1_2')
	mkdir('codon3')
	mkdir('fullCDS')

	print('Initializing dict')


	#get sampleID
	for sample in input_first:
		for ID in sample.samples:
			sample_dict[ID.sample] = []
		break

	matchSNP = copy.deepcopy(matchSCG)
	for chr in matchSNP:
		for gene in matchSNP[chr]:
			matchSNP[chr][gene]=copy.deepcopy(sample_dict)

	print('Initializing completed!')
	a=0
	for record in input_vcf:
		#get position
		#debug
		#a+=1
		position = record.POS
		chrID = record.CHROM
		if oldchr != chrID:
			oldchr = chrID
			order=0
		for site in record.samples:
			#get sampleID
			sampleID=site.sample

			#judge
			snp_site=isDegenerateBase(site)

			#match

			matchSNP,order=getPosition(sampleID,matchSNP,position,snp_site,chrID,order,matchSCG)


	#delete empty gene from matchSNP
	matchSNP=delEmpty(matchSNP)

	# output
	outputSNP(matchSNP)

	#phy



	# running time
	endtime = datetime.datetime.now()
	print("The scripts end at " + str(starttime))
	print("The running time is ", end='')
	print((endtime - starttime).seconds, end='')
	print(" seconds")

	sys.exit()

main()
