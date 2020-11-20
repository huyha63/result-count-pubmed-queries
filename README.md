**What to do before starting** 

1) a shebang is used to run the file. If you prefer not to use the shebang, please delete lines 1 and 2. Otherwise, change the filepath of the .py file to run the shebang
2) specify the input data file path in line 79 as a string
3) specify the output location folder in line 80 as a string
4) specify the disease of interest in line 81 as a string
5) specify the disease that will be used as a comparator to the disease of interest in line 82 as a string

**Exact format of input data**

1) .csv file with column name: target_ID and the chEMBL target IDs of interest. A sample input file named: sample_input_file.csv has been uploaded for reference

**What is the output format that’s expected?**

1) .csv file called query_results_[date and time of the time the script was used].csv with the following column names and descriptions
    - 'target_ID' (target ID queried into the script)
    - 'mesh_term' (mesh term associated with the target ID)
    - 'number_of_results_[user inputted disease of interest]' (number of results from a query with the target ID's mesh term and the user inputted disease of interest)
    - 'number_of_results_[user inputted disease used as a comparator to the disease of interest]' (number of results from a query with the target ID's mesh term and the user inputted disease used as a comparator to the disease of interest)

2) .json file called total_mesh_data.json of each target ID queried and its: 
    - associated preferred name as listed on chEMBL
    - associated electronic term name as listed on chEMBL that has more than 1 MeSH term associated with it
    - the mesh term associated with the target ID
    - whether there was a mesh term associated with the target ID (listed as true or false).

3) .json file called mesh_edge_cases.json of the target IDs and their associated electronic term(s) that have more than 1 MeSH term associated with them

4) .json file called mesh_terms_to_be_queried.json of the target IDs with only 1 MeSH term associated with them that can be queried

**What are the required packages needed to run this?**

python = 3.8.2
beautiful soup = 4.8.2

**What is the estimated run time?**

for about 300 chEMBL target IDs, 3-4 hours

**What still needs to be done?**

1. Using Icite, an article evaluator made by pubmed, determine the best article to be read to get more insight on how well associated the chembl ID is with tauopathies. Also, separate from articles published w/in last 1-2 yrs (perhaps focus on Review category?)
2. Resolve edge cases resulting from the SPARQL queries.
3. Current script has been written not been written concisely. It also includes specific links to my computer that should somehow be modified to allow anyone to use it (ex. Line 47 includes a file path to a specific folder I wanted a csv to be written to).
