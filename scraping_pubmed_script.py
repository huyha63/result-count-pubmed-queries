#!/usr/bin/python3
#python3 ~/Desktop/pubmed_side_project/scraping_pubmed_updated_making_sure_this_works.py

from bs4 import BeautifulSoup
import requests
from datetime import datetime
import csv
import time
import json
import urllib.parse

def pubmedqry(protgt, disease):
	'''
	for running a query using the MeSH terms: tauopathies and a protein target of your choice (protgt). api_key can be requested from pubmed website and inputted to increase from 3 requests a second to 10 requests a second
	'''
	x = make_request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + urllib.parse.quote('(' + disease + '[MeSH Terms] OR ' + disease + ') AND (' + protgt.lower() + '[MeSH Terms] OR ' + protgt.lower() + ')') + '&api_key=553755a82a5a150747840fe412dc009bbe08')
	# x = make_request('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=' + urllib.parse.quote('(tauopathies[MeSH Terms] OR tauopathies) AND (' + protgt.lower() + '[MeSH Terms] OR ' + protgt.lower() + ')') + '&api_key=553755a82a5a150747840fe412dc009bbe08')
	"""
	database (db) must be pubmed if you want to access pubmed. dictionary input for 'term' is the query that you're putting in. python automatically does URL encoding. use parentheses for "tauopathies" to prevent MeSH term explosion. explosion might be helpful for finding other associations for the MeSH term to provide more results.
	"""
	html = BeautifulSoup(x.text, 'lxml')
	list_of_failed_API_qry('pubmedqry', protgt, x)
	return(html.count.text)
	#example xml of pubmed: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term=science%5bjournal%5d+AND+breast+cancer+AND+2008%5bpdat%5d

def get_pname_or_eterm_of(target_id, term_to_fetch):
	'''
	term to fetch = either preferred name (i.e. 'pref_name') or entry term (i.e. 'component_synonym')
	'''
	x = make_request('https://www.ebi.ac.uk/chembl/api/data/target/' + target_id +'.xml')
	html = BeautifulSoup(x.text, 'lxml')
	name_or_term = list(set([entry_names.text for entry_names in html.find_all(term_to_fetch)]))
	list_of_failed_API_qry('chembl', target_id, x)
	return(name_or_term) #will return a list of preferred names or entry terms
	#example xml of ChEMBL: https://www.ebi.ac.uk/chembl/api/data/target/CHEMBL4302.xm
	#rate limit is no more than 1 request/sec

def ban_prevention(toc, tic, max_sec_per_request):
	time_to_finish = toc - tic
	if time_to_finish < max_sec_per_request:
		time.sleep(max_sec_per_request - time_to_finish)

def list_of_failed_API_qry(qry_type, failed_query, request_variable):
	if request_variable.status_code != 200: #need to make a list documenting the queries that do not provide API requests
		print('steven told you so')
		failed_query = {'type of query': str(qry_type), 'query': str(failed_query)}
		with open('/home/huy/Desktop/pubmed_side_project/failed_API_queries.csv', 'a') as csvfile:
			fieldnames = list(failed_query.keys())
			csv_writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
			csv_writer.writerow(failed_query)
			csvfile.close

def make_request(url):
	tries = 0
	while tries < 2:
		if tries > 1:
			print("retrying query: attempt #" + str(tries))
		try:
			return requests.get(url)
		except (ConnectionResetError, ConnectionError) as e:
			print(str(e) + '. Sleeping for 45 seconds')
			time.sleep(60)
		except Exception as e:
			print("generic error...sleeping for 2 minutes")
			print(str(e))
			time.sleep(120)
		tries += 1

'''
Overview: this code has the following order: 
	1) retrieve target IDs of interest
	2) convert them to MeSH terms
	3) query MeSH terms along with the "tauopathies" MeSH term into pubmed and get a CSV with the target name in one column and counts in the other
'''

'''
Step 0. truncate the lists you're about to make
'''
with open('/home/huy/Desktop/pubmed_side_project/failed_API_queries_ecases_only.csv', 'w+') as csvfile:
	fieldnames = ['type_of_query', 'query']
	writer = csv.DictWriter(csvfile, fieldnames = fieldnames)
	writer.writeheader()
	csvfile.close

"""
'''
Step 1. create a list of ChEMBL target IDs (i.e. protgt_ID) that you eventually want to query into pubmed
'''
with open('/home/huy/Desktop/pubmed_side_project/FINAL_GFP-Tau Targets Results.csv', 'r') as csv_file:
	protgt_ID = [row['target_ID'] for row in csv.DictReader(csv_file) if row['Organism'] == 'Homo sapiens']
	print(len(protgt_ID))

# with open('/home/huy/Desktop/pubmed_side_project/edge_cases.json') as json_file:
# 	reader = json.load(json_file)
# 	protgt_ID = [item for item in reader.keys()]
'''
Step 2. convert the ChEMBL target IDs into MeSH terms
'''
mesh_data = {}
for iteration, ID in enumerate(protgt_ID):
	tic = time.perf_counter()
	preferred_name = get_pname_or_eterm_of(ID, 'pref_name')[0]
	mesh_data[ID] = {'preferred_name' : preferred_name}
	print('preferred name (' + str(iteration + 1) + '/' + str(len(protgt_ID)) + '): ' + str(preferred_name))
	x = make_request('https://id.nlm.nih.gov/mesh/sparql?query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+xsd%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0APREFIX+owl%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0APREFIX+meshv%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2Fvocab%23%3E%0D%0APREFIX+mesh%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F%3E%0D%0APREFIX+mesh2015%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2015%2F%3E%0D%0APREFIX+mesh2016%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2016%2F%3E%0D%0APREFIX+mesh2017%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2017%2F%3E%0D%0A++%0D%0A++SELECT+%3Fc+%3FdescriptorName%0D%0A++%0D%0A++FROM+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%3E%0D%0A++%0D%0A++++WHERE+%7B+%0D%0A++++%3Fc+a+meshv%3ADescriptor+.%0D%0A++++%3Fc+rdfs%3Alabel+%3FdescriptorName+.%0D%0A%09FILTER+REGEX%28%3FdescriptorName%2C+%27' + preferred_name + '%27%2C+%27i%27%29+.+%0D%0A++++%7D+%0D%0A+Order+by+%3Fc%0D%0A&format=XML&inference=true&year=current&limit=50&offset=0#lodestart-sparql-results')
	#rate limit is no more than 500 requests per minute per IP address
	html = BeautifulSoup(x.text, 'lxml')
	MeSH_term = list(set([term.text for term in html.find_all('literal')]))
	list_of_failed_API_qry('sparql_preferred_name', preferred_name, x)
	if len(MeSH_term) >1:
		for item in MeSH_term:
			if preferred_name.lower() == item.lower():
				mesh_data[ID]['mesh_term'] = preferred_name
				mesh_data[ID]['no_mesh_term_to_query'] = False
				print(preferred_name[0] + ', came back. Continuing with next targetID')
				print('')
				toc = time.perf_counter()
				ban_prevention(toc, tic, 2)
				break 
		if 'mesh_term' not in mesh_data[ID].keys():
			mesh_data[ID]['pname_complication'] = {}
			mesh_data[ID]['pname_complication'][preferred_name] = MeSH_term
			mesh_data[ID]['no_mesh_term_to_query'] = True
			print('more than 1 Mesh term came back')
			print(MeSH_term)
			print('')
			toc = time.perf_counter()
			ban_prevention(toc, tic, 2) #choosing meshbrowser's rate limit since it is more limiting than the other process's: chembl
	elif len(MeSH_term) ==0:
		print('no mesh terms came back')
		print('')
		toc = time.perf_counter()
		ban_prevention(toc, tic, 2) #choosing meshbrowser's rate limit since it is more limiting than the other process's: chembl
		tic = time.perf_counter()
		list_of_entry_term = get_pname_or_eterm_of(ID, 'component_synonym')
		for i, entry_term in enumerate(list_of_entry_term):
			print('entry term (' + str(i + 1) + '/' + str(len(list_of_entry_term)) + '): ' + str(entry_term))
			if i > 0:
				tic = time.perf_counter()
			x = make_request('https://id.nlm.nih.gov/mesh/sparql?query=PREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+xsd%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2001%2FXMLSchema%23%3E%0D%0APREFIX+owl%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2002%2F07%2Fowl%23%3E%0D%0APREFIX+meshv%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2Fvocab%23%3E%0D%0APREFIX+mesh%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F%3E%0D%0APREFIX+mesh2015%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2015%2F%3E%0D%0APREFIX+mesh2016%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2016%2F%3E%0D%0APREFIX+mesh2017%3A+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%2F2017%2F%3E%0D%0A++%0D%0A++SELECT+%3FdescriptorName%0D%0A++%0D%0A++FROM+%3Chttp%3A%2F%2Fid.nlm.nih.gov%2Fmesh%3E%0D%0A++%0D%0A++++WHERE+%7B+%0D%0A++++%3Fc+a+meshv%3ADescriptor+.%0D%0A++++%3Fc+meshv%3Aconcept%2Fmeshv%3Aterm%2Frdfs%3Alabel+%3FentryTerm+.%0D%0A++++%3Fc+rdfs%3Alabel+%3FdescriptorName+.%0D%0A++++FILTER+contains%28%3FentryTerm%2C+%27' + entry_term + '%27%29+.%0D%0A++++%7D+%0D%0A+%0D%0A&format=XML&inference=true&year=current&limit=50&offset=0#lodestart-sparql-results')
			html = BeautifulSoup(x.text, 'lxml')
			MeSH_term = list(set([term.text for term in html.find_all('literal')]))
			list_of_failed_API_qry('sparql_entry_term', entry_term, x)
			if len(MeSH_term) >1:
				for item in MeSH_term:
					if item.lower() == entry_term.lower():
						print(entry_term + ', came back. Continuing with next targetID')
						print('')
						if ID not in mesh_data:
							mesh_data[ID] = {}
						mesh_data[ID]['mesh_term'] = MeSH_term[0]
						mesh_data[ID]['no_mesh_term_to_query'] = False
						toc = time.perf_counter()
						ban_prevention(toc, tic, 1)
						break
				if 'mesh_term' not in mesh_data[ID].keys():
					if 'eterm_complication' not in mesh_data[ID]:
						mesh_data[ID]['eterm_complication'] = {}
					mesh_data[ID]['eterm_complication'][entry_term] = MeSH_term
					print('> 1 MesH term')
					print(MeSH_term)
					print('')
					toc = time.perf_counter()
					ban_prevention(toc, tic, 1)
			elif len(MeSH_term) == 0:
				print('no MeSH terms')
				print('')
				toc = time.perf_counter()
				ban_prevention(toc, tic, 1)
			else:
				mesh_data[ID]['mesh_term'] = MeSH_term[0]
				mesh_data[ID]['no_mesh_term_to_query'] = False
				print(MeSH_term[0] + ', came back. Continuing with next targetID')
				print('')
				toc = time.perf_counter()
				ban_prevention(toc, tic, 1) 
				break
		if ID in mesh_data:
			if 'mesh_term' not in mesh_data[ID].keys():
				mesh_data[ID]['no_mesh_term_to_query'] = True
			else:
				mesh_data[ID]['no_mesh_term_to_query'] = False
		else:
			mesh_data[ID]['no_mesh_term_to_query'] = True
		toc = time.perf_counter()
		ban_prevention(toc, tic, 2) #choosing the most limiting of the rate limits: meshbrowser's
	else:
		mesh_data[ID]['mesh_term'] = MeSH_term[0]
		mesh_data[ID]['no_mesh_term_to_query'] = False
		print('found one: ' + str(MeSH_term[0]))
		print('')
		toc = time.perf_counter()
		ban_prevention(toc, tic, 2) #choose the more limiting of the rate limits. in this case, it's the chembl query at 1 request/sec comapred to meshbrowser's 8.33 requests/sec
	with open('/home/huy/Desktop/pubmed_side_project/query_results/mesh_data_092420_' + str(iteration) + '.json', 'w+') as outfile:
		json.dump(mesh_data, outfile)
		print('dumping into file: ' + str(iteration))
		outfile.close()
"""
'''
Step 3. run the protein target MeSH terms + the disease state MeSH term you're interested in
'''
### current code but may contain remnants that you don't need
with open('/home/huy/Desktop/pubmed_side_project/query_results/mesh_data_092420_328.json') as jsonfile:
	reader = json.load(jsonfile)
	print('length of mesh_data file is: ' + str(len(reader)))
	# mesh_name = [value['mesh_term'] for value in reader.values() if 'mesh_term' in value.keys()]
	mesh_name = {key:value['mesh_term'] for (key,value) in reader.items() if 'mesh_term' in value.keys()}
	edge_cases = {}
	for key, value in reader.items():
		if 'mesh_term' not in value.keys():
			edge_cases[key] = value
	print('number of edge cases is: ' + str(len(edge_cases)))
	print('number of mesh names file is: ' + str(len(mesh_name)))
	jsonfile.close()

with open('/home/huy/Desktop/pubmed_side_project/edge_cases_092420.json', 'w+') as outfile:
	json.dump(edge_cases, outfile)
	outfile.close()

with open('/home/huy/Desktop/pubmed_side_project/mesh_terms_092420.json', 'w+') as outfile:
	json.dump(mesh_name, outfile)
	outfile.close()

total_results = []
for num, (key, term) in enumerate(mesh_name.items()):
	with open('/home/huy/Desktop/pubmed_side_project/query_results//pubmed_queries/query_results_' + datetime.now().strftime("%m_%d_%y_%H:%M") + '.csv', 'w') as new_file:
		print('working on query ' + str(num + 1) + ' of ' + str(len(mesh_name)))
		tic = time.perf_counter()
		fieldnames = ['target_ID', 'mesh_term', 'number_of_results_tauopathies', 'number_of_results_T2DM']
		total_results += [(str(key), str(term), pubmedqry(term, 'tauopathies'), pubmedqry(term, 'diabetes mellitus, type 2'))]
		csv_writer = csv.writer(new_file)
		csv_writer.writerow(fieldnames)
		csv_writer.writerows(total_results)
		new_file.close
		toc = time.perf_counter()
		ban_prevention(toc, tic, 0.1)

