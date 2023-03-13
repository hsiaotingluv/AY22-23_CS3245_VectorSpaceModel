#!/usr/bin/python3
import re
import nltk
import sys
import getopt

# from boolean_query import QueryParser
from query_parser import QueryParser

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

    # Read dict_file into memory using a python dictionary for O(1) access
    dictionary = {} 

    f = open(dict_file, 'r')
    for dictionary_entry in f:
        elements = dictionary_entry.split() 
        term = elements[0]
        doc_freq = elements[1]
        pointer = int(elements[2])
        dictionary[term] = (doc_freq, pointer)

    # Parse queries
    parser = QueryParser(dictionary, postings_file)

    # Go through each query
    with open(queries_file, 'r') as file:

        is_first_line = True

        for query in file:

            try: 
                # Parse the query
                # print("This is the query: ", query)
                postfix_query = parser.shunting_yard(query)

                # Get the return value
                result_postings = parser.evaluatePostfix(postfix_query)

                # Write the output result
                # print ("Writing result of query to file... \n")
                # print (result_postings)
            except: 
                result_postings = "INVALID QUERY"
                # print(result_postings)


            if is_first_line: 
                # Creating new file
                with open(results_file, "w") as f:
                    f.write(result_postings)
                    f.close()
                    is_first_line = False

            else:
                with open(results_file, "a") as f:
                    f.write("\n" + result_postings)
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
