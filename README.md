# USPTO
 JMP code


RPM (requests per minute),
RPD (requests per day),
TPM (tokens per minute), 1,000,000 
TPD (tokens per day), and 
IPM (images per minute)

  text-embedding-3-large	500	-	1,000,000
  500 rpm ? or 5000 rpm? chekc the limit with code in parallel. Also: 
  links : https://platform.openai.com/docs/guides/rate-limits/usage-tiers?context=tier-two
  links: https://platform.openai.com/account/limits


33 calls... so it does not matter that much... you should call 33 per min 
this could take forever... but you only gotta do it once... 

Priority. Do it safely. You only wanna do it once. 
Maybe better to do one call at a time. 


## DATASETS

This is the list of datasets that are contained here: 



1) The USPTO Patents View data, which
includes detailed information on both granted patents and patent applications. 
https://www.uspto.gov/ip-policy/economic-research/research-datasets/patent-examination-research-dataset-public-pair


2) The Patent Claims Research Dataset (Marco et al., 2019) from which I obtain detailed information on the
number of claims per patent, claim text, and the change in the claims between application
to granting for granted patents; 

http://www.uspto.gov/economics

3) “Google Patents Research Data” from which I pull the
abstract and description text of each patent application; 

4) Examiners’ roster, pay scale, and
education levels from Frakes and Wasserman (2017) Freedom of Information Act request;

5) Kogan et al. (2017) patent market value data, which run event studies to estimate the
excess stock market return realized on the grant date of patents assigned to publicly traded
6Utility patents are granted for the “invention of a new and useful process, machine, manufacture, or
composition of matter” (USPTO 2010).
7Since the American Inventors Protection Act of 1999, almost all the USPTO patent applications filed
after November 29th, 2000 were published online, regardless of whether they are granted or not.
11
firms; 

6) USPTO Office Action Rejection, which documents the grounds of rejections for all
rejected patent applications from 2008 to 2017. For additional information about the patent
data, see Appendix Sectio