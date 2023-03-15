import os
from sys import platform

import math
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer

class VectorSpaceModel:
    """
    Class that construct and write data from in_dir into out_dict and out_postings. 
    Using SPIMI-Invert method, we construct dictionary and postings in blocks, then use n-way merging to merge the blocks in order.
    """
    def __init__(self, in_dir, out_dict, out_postings):
        """
        Initialise input directory and output files
        """
        print("initialising index...")

        self.in_dir = in_dir
        self.out_dict = out_dict
        self.out_postings = out_postings
    
    def get_all_doc_ids(self):
        """
        Get and and write all sorted doc ids into all_doc_ids.txt

            Returns:
                A list of sorted doc ids
        """
        total_docs = 0
        max_docs = 100

        all_doc_ids = []
        for doc_id in os.listdir(self.in_dir):
            if (total_docs == max_docs):
                break
            all_doc_ids.append(int(doc_id))
            total_docs += 1
        all_doc_ids.sort()
        final_content = all_doc_ids.copy()
        final_content.insert(0, len(final_content)) # total_num_docs doc_id doc_id ...

        # Write to a txt file for search to access all doc_ids 
        with open("all_doc_ids.txt", "w") as file:
            file.write(" ".join(map(str, final_content)))

        return all_doc_ids
    
    def reset_files(self):
        """
        Method to delete all block, dictionary and posting files generated from the previous indexing, and create a new block directory 
        """
        print("deleting previous test files...")
        if os.path.exists(self.out_postings):
            os.remove(self.out_postings)

        if os.path.exists(self.out_dict):
            os.remove(self.out_dict)

        if os.path.exists("all_doc_ids.txt"):
            os.remove("all_doc_ids.txt")
    
    def construct(self):
        """
        Construct the indexing of all terms and their postings
        """
        self.reset_files()

        print("constructing index...")
        stemmer = PorterStemmer()
        all_doc_ids = self.get_all_doc_ids()
        terms = list() # a list of terms
        term_docFreq = {} # key: string, value: int { term : docFreq }
        postings = {} # key: string, value: a dictionary { term : {docID : logTermFreqWeighting, docID : logTermFreqWeighting ...} }

        for doc_id in all_doc_ids:
            doc_id = str(doc_id)
            file = open(os.path.join(self.in_dir, doc_id))
            terms_counted = list() # list of terms counted for doc_id
            for line in file:
                for sentence_token in sent_tokenize(line):
                    for word_token in word_tokenize(sentence_token):
                        # stem and case-folding
                        word_token = stemmer.stem(word_token).lower()

                        # empty strings
                        if len(word_token) == 0:
                            continue

                        # add word_token into list of terms
                        if word_token not in terms:
                            terms.append(word_token)
                            term_docFreq[word_token] = 1 # { term : docFreq }
                            terms_counted.append(word_token)

                        # check if docFreq of word_token is counted for doc_id
                        if word_token not in terms_counted:
                            term_docFreq[word_token] += 1 # { term : docFreq }
                            terms_counted.append(word_token)
                        
                        # add word_token into posting list
                        if word_token not in postings:
                            postings[word_token] = {}
                            postings[word_token][doc_id] = 1 # value as { docID : termFreq ... }
                        else :
                            if doc_id not in postings[word_token]:
                                postings[word_token][doc_id] = 1 # value as { docID : termFreq ... }
                            else:
                                postings[word_token][doc_id] += 1 # value as { docID : termFreq ... }
            # print("==========================================================================")
            # print("term_docFreq: ", term_docFreq) # key: string, value: int { term : docFreq }
            # print("==========================================================================")
            # print("postings: ", postings) # key: string, value: a dictionary { term : {docID : logTermFreqWeighting, docID : logTermFreqWeighting ...} }
            # print("==========================================================================")
            
        # normalise term frequency for each document
        for term in postings: # key: string, value: a dictionary { term : {docID : logTermFreqWeighting, docID : logTermFreqWeighting ...} }
            for doc_id in postings[term]:
                term_freq = int(postings[term][doc_id])
                # print("==========================================================================")
                # print("term: ", term)
                # print("postings[term]: ", postings[term])
                # print("doc_id: ", doc_id)
                # print("term_freq: ", term_freq)
                # print("==========================================================================")
                postings[term][doc_id] = 1 + math.log(term_freq, 10) # value as { docID : logTermFreqWeighting ... }
                            
        terms.sort()
        self.write_to_disk(terms, term_docFreq, postings)
    
    def write_to_disk(self, terms, term_docFreq, postings):
        """
        Method to merge all blocks and write into out_dict and out_postings

            Parameters:
                total_num_blocks: an integer
        """
        print("preapring content for dictionary and postings...")

        final_dictionary = "" # term docFreq reference
        final_postings = "" # term docIDs...
        posting_ref = 0

        for term in terms:
            posting = postings[term] # {docID : logTermFreqWeighting, docID : logTermFreqWeighting ...}
            docFreq = term_docFreq[term]

            for doc_id, log_term_freq_weighting in posting.items():
                content = " (" + str(doc_id) + "," + str(log_term_freq_weighting) + ")" # (docID,logTermFreqWeighting) (docID,logTermFreqWeighting) ...
            new_posting = term + content + "\n" # term (docID,logTermFreqWeighting) (docID,logTermFreqWeighting) ...
            
            final_dictionary += term + " " + str(docFreq) + " " + str(posting_ref) + "\n" # term docFreq posting_ref
            final_postings += new_posting
            posting_ref += len(new_posting)

        # write out into final dictionary and postings
        print("writing to output files...")
        self.write_content(self.out_dict, final_dictionary)
        self.write_content(self.out_postings, final_postings)

    def write_content(self, out_file, content):
        """
        Method to write content into file
        
            Parameters:
                out_file: a file
                content: a string
        """
        f = open(out_file, "a")
        f.write(content)
        f.close()

