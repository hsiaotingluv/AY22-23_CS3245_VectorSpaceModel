This is the README file for A0222182R's and A0222371R's submission
Email(s): e0559714@u.nus.edu and e0559903@u.nus.edu

== Python Version ==

We're using Python Version <3.10.9> for this assignment.

== General Notes about this assignment ==

###Description
This program implements indexing and searching techniques for Ranked Retrieval Model from a set of training data given to it. It is capable of finding the top 10 most relevant (less if there are fewer than ten documents that have matching stems to the query) docIDs in response to the query. 

These documents are ordered by relevance, with the first document being most relevant. For documents with the same relevance, they are further sorted by the increasing order of the docIDs. 

###How to use
To build the indexing script, index.py, run:
$ python3 index.py -i directory-of-documents -d dictionary-file -p postings-file
which will store your dictionary into dictionary-file and postings into postings-file. 
Two other files, all_doc_ids.txt and document.txt will also be generated. 

To run the searching script, search.py, run:
$ python3 search.py -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results
which will store the queries results into output-file-of-results.

###About Indexing
We created a VectorSpaceModel class that helps with the indexing of all documents from directory-of-documents. The dictionary-file contains information written in the form of [term doc_freq posting_ref]. The postings-file contains information written in the form of [term (docID, w-tf) (docID, w-tf) ...], where weighted term frequency w-tf = (1 + log(tf)), and tf is the term frequency of the term t in docID. 

Additionally, two new files, namely all_doc_ids.txt and document.txt will also be generated after the indexing. The all_doc_ids.txt is an output file containing the ID of all documents, separated by a single space. While document.txt is an output file written in the form of [total_num_of_doc (docID, len_of_doc) (docID, len_of_doc) ...], where len_of_doc is the length of the document with docID in the vector space. 

###About construct
####Tokenisation
First, we obtain a sorted list of all document IDs. Then, we construct the index by looping through each document ID and tokenising every term in each document. The tokenisation of term is done using the NLTK tokenizers, nltk.sent_tokenize() and nltk.word_tokenize(). We then use NLTK Porter stemmer (class nltk.stem.porter) to do stemming. Lastly, we did case-folding to reduce all words to lower case.  

Unlike HW2, we did not make use of techniques such as removing punctuation and digits. We also did not remove numbers. This is so that users can still be able to query using numbers. 

####Doc and Term Frequency
In construct, we also count the number of document frequency of each term, as well as the term frequency of each document. These are later stored in term_doc_freq = { term : doc_freq } and postings = { term : {docID : term_freq, docID : term_freq ...} }.

###About get_log_term_freq_weighted
The method updates the term frequnecy (tf) in postings to the weighted term frequency (w-tf). This is done using the formula, w-tf = 1 + log(tf), where log is base 10 logarithm. 

The method also calculates the document length doc_len of each document in the vector space. The length of document in the vector space can be calculated by summing the squares of all w-tf of the terms presented in the document, and taking the sqaure root of the summation result. 

The method then returns doc_len and an updated postings.

###About write_to_disk
The method prepares and writes the dictionary, postings and document length into dictionary-file, postings-file and documents.txt respectively. Using a sorted list of terms, this method constructs the dictionary and posting lists in an increasing alphanumeric order. While the content in the documents.txt is sorted in increasing docID order.

###About Querying
####Search 
At the initial phase of running the search command, we read the dictionary file into memory and pass it to the VectorSearchModel instance from the vector_search.py file. This class is the main class which contains the methods for the vector space ranking.

####Vector Space ranking
In the searching step, we rank documents by cosine score similarity based on tfxidf. The algorithm we use is the optimised version that we have seen in the lecture where we only compute non-zero dimensions. We implement the lnc.ltc ranking scheme (i.e., log tf and idf with cosine normalization for queries documents, and log tf, cosine normalization but no idf for documents.) 

The cosine_score method tokenises the terms, following which it calls the get_normalised_query_vectors method to get the normalised wt of the terms in the query. This is akin to representing the query as a weighted tf-idf vector, but in an optimised way. For each term in the query, we calculate the tf weight and idf weight, and normalise them by dividing them by the query length. 

Then, in the cosine_score method, for each term in the dictionary of normalised query vectors, we fetch the postings list using the get_postings method to retrieve tuples, then calculate the cosine similarity between w_tq and w_td by multiplying the normalised vectors. 

Finally, we normalise the scores by dividing the scores of the docs with their lengths. The results are then sorted and we return the top 10 results. 

== Files included with this submission ==

1. README.txt - a summary write up about the program, how to run and how it works
2. index.py - the main program to run the indexing, which calls vector_space_model.py
3. vector_space_model.py - contains the methods to index the terms and writes the results into dictionary-file, postings-file, all_doc_ids.txt and document.txt.
4. search.py - the main program to run the searching, which calls vector_search.py
5. vector_search.py - contains the methods to process queries and carry out the vector space ranking algorithm using tf-idf
6. dictionary.txt - a dictionary text file containing [term doc_freq posting_ref]
7. postings.txt - a posting text file containing [term (docID, w-tf) (docID, w-tf) ...], where w-tf = (1 + log(tf)), and tf is the term frequency of the term t in docID
8. all_doc_ids.txt - a text file containing all the document IDs
9. document.txt - a text file containing [total_num_of_doc (docID, len_of_doc) (docID, len_of_doc) ...], where len_of_doc is the length of the document in vector space

== Statement of individual work ==

Please put a "x" (without the double quotes) into the bracket of the appropriate statement.

[x] I/We, A0222182R and A0222371R, certify that I/we have followed the CS 3245 Information
Retrieval class guidelines for homework assignments.  In particular, I/we
expressly vow that I/we have followed the Facebook rule in discussing
with others in doing the assignment and did not take notes (digital or
printed) from the discussions.  

[ ] I/We, A0000000X, did not follow the class rules regarding homework
assignment, because of the following reason:

<Please fill in>

We suggest that we should be graded as follows:

<Please fill in>

== References ==

<Please list any websites and/or people you consulted with for this
assignment and state their role>
