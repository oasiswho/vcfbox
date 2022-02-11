# VCFbox

Welcome to VCFbox! This box contains some tools for VCF. Version: 1.0



Requirement: 

* Python 3.x+
* Python module: vcf
* Python module: Bio



# List of Tools

<a href="#ExtractSNPfromVCF">ExtractSNPfromVCF</a>





# Tools

## <span name = "ExtractSNPfromVCF">ExtractSNPfromVCF</span>

### Introduction

This script can be applied to extract SNPs from a VCF file by using a single-copy genes ID list and a GFF file into individual fasta file and phy file.



### Quick install & start

```
#Install
git clone https://github.com/oasiswho/vcfbox
cd vcfbox

#Python 3.x+
pip install vcf
pip install Bio

#Start
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list -phy -snp 1 empty -keep
```



### Usage

```
usage: main.py [-h] [-input VCF_file] [-gff GFF_file] [-scg SCG_file]
               [-snp snp_number] [-E Exclude_Gene] [-e Exclude_Sample] [-phy]
               {empty} ...
        
Input
  Input vcf file, gff file, single-copy genes list
-input VCF_file  input VCF file
  -gff GFF_file    input GFF file
  -scg SCG_file    input scg file

Exclude
  Exlude genes or samples
  -E Exclude_Gene    Exclude genes with >= value -E missing samples
  -e Exclude_Sample  Exclude genes with >= value -E missing data
SNP
  does not output genes with the number of SNPs less than was set
  -snp snp_number  does not output genes with the number of SNPs less than was set

Output
  options for outputting format phy, the default parameter will output fasta
  -phy             output sequence with relaxed-phylip format and fasta format

Empty
  Keep the gene or discard the gene
  -keep       Keep the gene if codon1-2 or codon3 is empty
  -discard    Discard the gene if codon1-2 or codon3 is empty

```



### Inputs

Example files are from this paper:

> He L, Jia KH, Zhang RG, Wang Y, Shi TL, Li ZC, Zeng SW, Cai XJ, Wagner ND, Hörandl E, Muyle A, Yang K, Charlesworth D, Mao JF. Chromosome-scale assembly of the genome of Salix dunnii reveals a male-heterogametic sex determination system on chromosome 7. Mol Ecol Resour. 2021 Aug;21(6):1966-1982. doi: 10.1111/1755-0998.13362



1. Chromosome level GFF file, only have longest transcript. (One gene, one mRNA)

![chromosome_level_gff.png](images/ExtractedSNPfromVCF/chromosome_level_gff.png)



2. Target VCF file

![VCF](images/ExtractedSNPfromVCF/VCF.png)



3. Single-copy genes ID list, this list should correspond to GFF file. 

   

   ![single-copy_genes_list](images/ExtractedSNPfromVCF/single-copy_genes_list.png)

You can use such as [OrthoFinder](https://github.com/davidemms/OrthoFinder) to get an Orthogroups directory. And then use this command to get a single-copy genes ID list.

**The VCF file should have as same number of chromosome as (or less) GFF file and Single-copy gene file.**

**And all of them should have same order.**

```shell
grep -Fwf Orthogroups_SingleCopyOrthologues.txt Orthogroups.txt > full.SingleCopyGenesIDS.txt
```



### Run

Run with default parameters:

```
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list empty -keep
```

Output format phy and fasta

```
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list -phy empty -keep
```

Does not output genes with the number of SNPs less than was set

```
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list -snp 1 empty -keep
```

 Discard the gene if codon1-2 or codon3 is empty

```
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list empty -discard
```

Exclude gene when missing_samples >= 10%, exclude samples when miss_snps >=10%

```
python ExtractSNPfromVCF.py -input samples.vcf -gff samples.gff -scg singlecopygenes.list -E 0.1 -e 0.1 empty -keep
```

Outputs:

```shell
codon1_2/
├── Sadunf07G0052900.1.fasta
├── Sadunf07G0052900.1.phy
├── Sadunf07G0054000.1.fasta
├── Sadunf07G0054000.1.phy
├── Sadunf07G0054100.1.fasta
├── Sadunf07G0054100.1.phy
├── Sadunf07G0054500.1.fasta
├── Sadunf07G0054500.1.phy
├── Sadunf07G0054600.1.fasta
├── Sadunf07G0054600.1.phy
├── Sadunf07G0054700.1.fasta
├── Sadunf07G0054700.1.phy
……
codon3
├── Sadunf07G0052900.1.fasta
├── Sadunf07G0052900.1.phy
├── Sadunf07G0054000.1.fasta
├── Sadunf07G0054000.1.phy
├── Sadunf07G0054100.1.fasta
├── Sadunf07G0054100.1.phy
├── Sadunf07G0054500.1.fasta
├── Sadunf07G0054500.1.phy
├── Sadunf07G0054600.1.fasta
├── Sadunf07G0054600.1.phy
├── Sadunf07G0054700.1.fasta
├── Sadunf07G0054700.1.phy
……
fullCDS/
├── Sadunf07G0052900.1.fasta
├── Sadunf07G0052900.1.phy
├── Sadunf07G0054000.1.fasta
├── Sadunf07G0054000.1.phy
├── Sadunf07G0054100.1.fasta
├── Sadunf07G0054100.1.phy
├── Sadunf07G0054500.1.fasta
├── Sadunf07G0054500.1.phy
├── Sadunf07G0054600.1.fasta
├── Sadunf07G0054600.1.phy
├── Sadunf07G0054700.1.fasta
├── Sadunf07G0054700.1.phy
……
```



### Custom modification

If gff file which only have 'mRNA'  instead of  'gene'  is used,  the code should be changed. e.g.

```python
if chr_id ==seq_id:
            #change type to mRNA .Modify the script to meet your demand.
			if type == 'mRNA':
				geneID = attributes.split(';')[0].split('=')[1]
				if geneID_flag != geneID and CDS_flag == 'true' :
					# SingleCopyID have '.1' in suffix, but gff don't , so I add up it.
					CDS_dict[geneID_flag] = CDS_list
					CDS_list = []
					CDS_flag='false'
					geneID_flag = geneID
				else:
					geneID_flag = geneID
```

 

## Citation

If the script works, please cite

For ExtractSNPfromVCF

> Sergey Gulyaev, Xin-Jie Cai, Fei-Yi Guo, Satoshi Kikuchi, Wendy L Applequist, Zhi-Xiang Zhang, Elvira Hörandl, Li He* , The phylogeny of Salix revealed by whole genome re-sequencing suggests different sex-determination systems in major groups of the genus, Annals of Botany, 2022, mcac012, https://doi.org/10.1093/aob/mcac012



## Update logs

V1.2 update python script ExtractSNPfromVCF_V1.9

V1.1 update python script ExtractSNPfromVCF_V1.8

V1.0 added python script ExtractSNPfromVCF_V1.6



## Acknowledges

We appreciate [Mingcheng Wang](https://orcid.org/0000-0002-3631-9174) for his generous help for providing ideas for python script ExtractSNPfromVCF. 

We thank Sergey and [Hongpu Chen](https://hongpu-chen.github.io/) for their guidance and suggestions for this project.

