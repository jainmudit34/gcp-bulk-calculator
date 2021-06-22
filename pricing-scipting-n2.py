#!/usr/bin/env python
# coding: utf-8

# In[44]:


#conda install numpy as np


# In[2]:


import pandas as pd


# In[ ]:


import sys, getopt

def main(argv):
   inputfile = ''
   outputcsv = ''
   skufile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:s:",["ifile=","ocsv=","sfile="])
   except getopt.GetoptError:
      print ('python3 n2pricing.py -i <inputfile> -o <outputcsv> -sku <skufile>')
      print('here')
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print ('python3 n2pricing.py -i <inputfile> -o <outputcsv> -sku <skufile>' )
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputcsv = arg
      elif opt in ("-s", "--sfile"):
         skufile = arg
#   print ('Input file is "', inputfile)
#   print ('Output file is "', outputcsv)
#   print ('sku file is "', skufile)
   return(inputfile,outputcsv,skufile)
#if __name__ == "__main__":
response = main(sys.argv[1:])
inputfile=response[0]
outputcsv=response[1]
skufile=response[2]
print(outputcsv)
#print('here')
# In[192]:


pricing=pd.read_excel(inputfile,sheet_name="Server List").dropna(subset=["Server Name", "Region", "Operating System"], how='any')
pricing = pricing.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
source_pricing=pd.read_excel(skufile,sheet_name="SOT-N2")
source_license_pricing=pd.read_excel(skufile,sheet_name="global license pricing")

source_pricing = source_pricing.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
source_pricing = source_pricing.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)
source_license_pricing = source_license_pricing.apply(lambda x: x.str.lower() if(x.dtype == 'object') else x)


# In[193]:



pricing["calculated req vCPU"]=(pricing["Number of CPUs"]*pricing["Core Count"]*pricing["CPU Utilisation % preferably P95"]*0.016).round()
pricing.dropna(subset=["calculated req vCPU","Required CPU"], how='all',inplace=True)
pricing


# In[59]:


pricing["calculated req Memory"]=(pricing["Memory GiB"]*pricing["Memory Utilisation % preferably P95"]*0.016).round()
pricing.dropna(subset=["calculated req Memory","Required Memory"], how='all',inplace=True)


# In[60]:


pricing["Required Memory"] = pricing["Required Memory"].fillna(pricing["calculated req Memory"])
pricing["Required CPU"] = pricing["Required CPU"].fillna(pricing["calculated req vCPU"])


pricing["Required Memory"]=round(pricing["Required CPU"])
pricing["Required Memory"]=round(pricing["Required Memory"])

pricing['normalised CPU'] = pricing['Required CPU'].apply(lambda x: (x+1) if ((x%2!=0.0) & (x!=1.0) &(x<=7.0)) else x)
pricing['Required CPU'] = pricing['Required CPU'].apply(lambda x: (x-1) if ((x%2!=0.0) & (x!=1.0) &(x>=9.0)) else x)
pricing['Recommended VM family'] = pricing.apply(lambda _: 'n2', axis=1)


# In[61]:


uniq_pricing=pricing[['Region','Operating System','normalised CPU','Required Memory','Recommended VM family']].drop_duplicates().sort_values(by=['normalised CPU','Required Memory'])
uniq_pricing=uniq_pricing[uniq_pricing['Required Memory'] <= 640]
uniq_pricing=uniq_pricing[uniq_pricing['normalised CPU'] <= 80]

#uniq_pricing


# In[62]:


uniq_pricing=uniq_pricing.merge(source_pricing,on=['Region'],how='left')
uniq_pricing=uniq_pricing.merge(source_license_pricing,on=['Operating System'],how='left')


# In[ ]:





# In[63]:


uniq_pricing[['hourly rate','monthly no-SUD no-cud','monthly with SUD','monthly no-SUD 1yr CUD','Monthly_res_1yr','monthly no-SUD 3yr CUD','Monthly_res_3yr']]=0


# In[64]:


uniq_pricing['hourly rate']


# In[65]:


def hourlyrate(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return (wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']+wordcnt['license']))
        elif (wordcnt['Operating System']=="sles"): return (wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['license']
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return (wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return (wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['license']
        elif (wordcnt['Operating System']=="rhel"): return (wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['rhel 6+ cores']
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return (wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']+wordcnt['license']))
        elif (wordcnt['Operating System']=="sles"): return (wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['license']
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return (wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return (wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['license']
        elif (wordcnt['Operating System']=="rhel"): return (wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman']))+wordcnt['rhel 6+ cores']






def sud(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*.8*((wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_on-deman']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))*.8*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))*.8*730
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))*.8*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd no_commit'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))*.8*730+wordcnt['rhel 6+ cores']*730
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*.8*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_on-deman']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return 730*.8*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return 730*.8*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return 730*.8*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return 730*.8*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd no_commit']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_on-deman'])))+wordcnt['rhel 6+ cores']*730

uniq_pricing['hourly rate'] = uniq_pricing.apply(lambda x: hourlyrate(x),axis=1)
uniq_pricing['monthly no-SUD no-cud']=730*uniq_pricing['hourly rate']
uniq_pricing['monthly with SUD'] = uniq_pricing.apply(lambda x: sud(x),axis=1)

#uniq_pricing['monthly with SUD'] = ((uniq_pricing['hourly rate'])*0.8)*730


# In[66]:


uniq_pricing[['hourly rate','monthly no-SUD no-cud','monthly with SUD','monthly no-SUD 1yr CUD','Monthly_res_1yr','monthly no-SUD 3yr CUD','Monthly_res_3yr']]

#uniq_pricing[['Region','Operating System','normalised CPU','Required Memory','hourly rate','monthly with SUD','Monthly_res_1yr','Monthly_res_3yr']] 


# In[67]:



def res1yr(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_1yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['rhel 6+ cores']*730
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_1yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['rhel 6+ cores']*730

def res1yr_no_sud(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_1yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 1 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))*730+wordcnt['rhel 6+ cores']*730
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_1yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 1 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_1yr'])))+wordcnt['rhel 6+ cores']*730


uniq_pricing['Monthly_res_1yr'] = uniq_pricing.apply(lambda x: res1yr(x),axis=1)

uniq_pricing['monthly no-SUD 1yr CUD'] = uniq_pricing.apply(lambda x: res1yr_no_sud(x),axis=1)

def res3yr(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_3yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['rhel 6+ cores']*730
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_3yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd']*.8)+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['rhel 6+ cores']*730

def res3yr_no_sud(wordcnt):
    if (wordcnt['normalised CPU']*8 >= wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_3yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return ((wordcnt['Required Memory']*wordcnt['custom_RAM usd 3 yr'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))*730+wordcnt['rhel 6+ cores']*730
    elif (wordcnt['normalised CPU']*8 < wordcnt['Required Memory']):
        if ((wordcnt['Operating System']=="windows")): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*wordcnt['N2_custom_core_3yr']))+(wordcnt['normalised CPU']*wordcnt['license']*730)
        elif (wordcnt['Operating System']=="sles"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="free: debian, centos, coreos, ubuntu, or other user provided os"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))
        elif ((wordcnt['Operating System']=="rhel") & (wordcnt['normalised CPU']<6)): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['license']*730
        elif (wordcnt['Operating System']=="rhel"): return 730*((wordcnt['normalised CPU']*8*wordcnt['custom_RAM usd 3 yr']) + ((wordcnt['Required Memory']-wordcnt['normalised CPU']*8)*wordcnt['Ext_RAM usd'])+(wordcnt['normalised CPU']*(wordcnt['N2_custom_core_3yr'])))+wordcnt['rhel 6+ cores']*730



uniq_pricing['Monthly_res_3yr'] = uniq_pricing.apply(lambda x: res3yr(x),axis=1)
uniq_pricing['monthly no-SUD 3yr CUD'] = uniq_pricing.apply(lambda x: res3yr_no_sud(x),axis=1)

#((uniq_pricing['Required Memory']*uniq_pricing['custom_RAM usd 3 yr'])+(uniq_pricing['normalised CPU']*(uniq_pricing['N2_custom_core_3yr'])))*730+uniq_pricing['license']*730


# In[68]:


uniq_pricing=uniq_pricing[['Region','Operating System','normalised CPU','Required Memory','hourly rate','monthly no-SUD no-cud','monthly with SUD','monthly no-SUD 1yr CUD','Monthly_res_1yr','monthly no-SUD 3yr CUD','Monthly_res_3yr']] 


# In[69]:


uniq_pricing


# In[70]:


pricing=pricing.merge(uniq_pricing,on=['Region','Operating System','normalised CPU','Required Memory'],how='left')


# In[218]:


#path = inputfile
#writer = pd.ExcelWriter(path, engine = 'xlsxwriter')
#pricing[['Server Name','Region','Operating System','Required Memory','normalised CPU','Recommended VM family','hourly rate','monthly with SUD','Monthly_res_1yr','Monthly_res_3yr']].dropna().to_excel(writer, sheet_name="n2_pricing",index=False)
#writer.save()
#writer.close()


pricing[['Server Name','Region','Operating System','Required Memory','normalised CPU','Recommended VM family','hourly rate','monthly no-SUD no-cud','monthly with SUD','monthly no-SUD 1yr CUD','Monthly_res_1yr','monthly no-SUD 3yr CUD','Monthly_res_3yr']].dropna().to_csv(outputcsv)

# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




