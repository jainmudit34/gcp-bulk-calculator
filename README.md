# gcp-bulk-calculator




pip3 install pandas openpyxl xlrd

pip install pandas openpyxl xlrd

1. command sample:

#python3 pricing-scipting-n1-v2.py -i 'path/pricing-input.xlsx'  -o '/path/pricing-output.csv' -s '/path/gcp-sku-pricing.xlsx'

#python pricing-scipting-n1-v2.py -i 'path/pricing-input.xlsx'  -o '/path/pricing-output.csv' -s '/path/gcp-sku-pricing.xlsx'


#python3 pricing-scipting-n2.py -i 'path/pricing-input.xlsx'  -o '/path/pricing-output.csv' -s '/path/gcp-sku-pricing.xlsx'

#python pricing-scipting-n2.py -i 'path/pricing-input.xlsx'  -o '/path/pricing-output.csv' -s '/path/gcp-sku-pricing.xlsx'


2. There is a sample sheet in the input file for reference.

3. Don't change any sheet names or column names in input or SKU files.


checkout:
https://mudit-jain.medium.com/how-to-do-gcp-sizing-for-100s-of-vms-in-15-seconds-695afd9189c3
https://youtu.be/VyT6Zkb52l4

**Notes:**
**Please note the core count and memory should be intigers.** 
**Make sure there are no leading or trailing spaces in the OS names.**
**Please use Required CPU	Required Memory![image](https://user-images.githubusercontent.com/22167244/134287526-a38cda3d-abfe-4671-96da-3183cee8601f.png) instead of letting tool calculate it, there is some bug**
