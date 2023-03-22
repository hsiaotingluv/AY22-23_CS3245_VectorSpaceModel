#!/usr/bin/python3
import re
import nltk
import sys
import getopt

from vector_search import VectorSearchModel

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

def run_search(dict_file, postings_file, queries_file, results_file):
    """
    using the given dictionary file and postings file,
    perform searching on the given queries file and output the results to a file
    """
    print('running search on the queries...')
    # This is an empty method
    # Pls implement your code in below

    # Read dictionary into memory
    dictionary = {}

    # Get term, doc frequncy and postings list pointer from Dictionary
    f = open(dict_file, 'r')
    for dictionary_entry in f:
        elements = dictionary_entry.split()
        term = elements[0]
        doc_freq = elements[1]
        pointer = int(elements[2])
        dictionary[term] = (int(doc_freq), pointer)

    # Calculate cosine difference and return top scores
    search_vector_model = VectorSearchModel(dictionary, postings_file)

    # Go through each query
    with open(queries_file, 'r') as file:

        is_first_line = True

        for query in file:
            try: 
                top_k_results = search_vector_model.cosine_score(query)
                top_k_results = ' '.join(top_k_results)

            except:
                top_k_results = "INVALID QUERY (something went wrong...)"

            if is_first_line:
                with open(results_file, "w") as f:
                    f.write(top_k_results)
                    f.close()
                    is_first_line = False
            else: 
                with open(results_file, "a") as f:
                    f.write("\n" + top_k_results)
                    f.close()



dictionary_file = postings_file = file_of_queries = output_file_of_results = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except getopt.GetoptError:
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)

run_search(dictionary_file, postings_file, file_of_queries, file_of_output)
