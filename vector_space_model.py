import os

import math
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer

class VectorSpaceModel:
    """
    Class that construct and write data from in_dir into out_dict, out_postings, all_doc_ids.txt and document.txt files. 
    """
    def __init__(self, in_dir, out_dict, out_postings):
        """
        Initialise input directory and output files
        """
        print("initialising vector space model...")

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
        max_docs = 7769

        all_doc_ids = []
        for doc_id in os.listdir(self.in_dir):
            if (total_docs == max_docs):
                break
            all_doc_ids.append(int(doc_id))
            total_docs += 1
        all_doc_ids.sort()

        # Write to a txt file for search to access all doc_ids 
        with open("all_doc_ids.txt", "w") as file:
            file.write(" ".join(map(str, all_doc_ids)))

        return all_doc_ids
    
    def reset_files(self):
        """
        Method to delete all files generated from the previous indexing
        """
        print("deleting previous test files...")
        if os.path.exists(self.out_postings):
            os.remove(self.out_postings)

        if os.path.exists(self.out_dict):
            os.remove(self.out_dict)

        if os.path.exists("all_doc_ids.txt"):
            os.remove("all_doc_ids.txt")

        if os.path.exists("document.txt"):
            os.remove("document.txt")
    
    def construct(self):
        """
        Method to construct the indexing of all terms and their postings
        """
        self.reset_files()

        print("constructing index...")
        stemmer = PorterStemmer()
        all_doc_ids = self.get_all_doc_ids()
        total_num_docs = len(all_doc_ids)
        terms = list() # a list of terms
        term_docFreq = {} # key: string, value: int { term : docFreq }
        postings = {} # key: string, value: a dictionary { term : {docID : term_freq, docID : term_freq ...} }

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
            # print("postings: ", postings) # key: string, value: a dictionary { term : {docID : term_freq, docID : term_freq ...} }
            # print("==========================================================================")
        
        doc_len = self.get_log_term_freq_weighted(postings)[0]
        postings = self.get_log_term_freq_weighted(postings)[1]

        terms.sort()
        self.write_to_disk(terms, term_docFreq, postings, doc_len, total_num_docs)

    def get_log_term_freq_weighted(self, postings):
        """
        Method to calculate weighted = 1 + log(term_frequency)
        Replace term_freq to weighted in postings, and get the length of each document and store in doc_len

            Parameter:
                postings: a dictionary with string as key and dictionary as value, { term : {docID : term_freq, docID : term_freq ...} }
            
            Returns:
                A list of doc_len and updated postings
        """
        doc_len = {} # { docID : doc_len, docID : doc_len ... }
        # normalise term frequency for each document
        for term in postings: # key: string, value: a dictionary { term : {docID : term_freq, docID : term_freq ...} }
            for doc_id in postings[term]:
                term_freq = int(postings[term][doc_id])
                # print("==========================================================================")
                # print("term: ", term)
                # print("postings[term]: ", postings[term])
                # print("doc_id: ", doc_id)
                # print("term_freq: ", term_freq)
                # print("==========================================================================")
                log_term_freq_weighted = 1 + math.log(term_freq, 10)

                if doc_id not in doc_len:
                    doc_len[doc_id] = log_term_freq_weighted * log_term_freq_weighted
                else:
                    doc_len[doc_id] += log_term_freq_weighted * log_term_freq_weighted

                postings[term][doc_id] = log_term_freq_weighted # value as { docID : log_term_freq_weighted ... }
        
        for doc_id in doc_len:
            doc_len[doc_id] = math.sqrt(doc_len[doc_id]) # { docID : doc_len, docID : doc_len ... }
        
        return [doc_len, postings]

    def write_to_disk(self, terms, term_docFreq, postings, doc_len, total_num_docs):
        """
        Method to write into out_dict, out_postings and document.txt

            Parameters:
                terms: a list of string, sorted in ascending alphanumeric order
                term_docFreq: a dictionary with string as key and int as value, { term : docFreq }
                postings: a dictionary with string as key and dictionary as value, { term : {docID : term_freq, docID : term_freq ...} }
                doc_len: a dictionary with string as key and int as value, { docID : doc_len, docID : doc_len ... }
                total_num_docs: an int representing the total number of documents
                
        """
        print("preapring content for dictionary, postings and documents output files...")

        final_dictionary = "" # term docFreq reference
        final_postings = "" # term (docID,term_freq) (docID,term_freq) ...
        final_document = "" # totalNumDocs (docID,lenOfDoc) (docID,lenOfDoc) ...
        posting_ref = 0

        for term in terms:
            posting = postings[term] # {docID : term_freq, docID : term_freq ...}
            docFreq = term_docFreq[term]
            content = ""

            for doc_id, term_freq in posting.items():
                # print("doc_id: ", doc_id)
                # print("term_freq: ", term_freq)
                content += " (" + str(doc_id) + "," + str(term_freq) + ")" # (docID,term_freq) (docID,term_freq) ...
            new_posting = term + content + "\n" # term (docID,term_freq) (docID,term_freq) ...
            
            final_dictionary += term + " " + str(docFreq) + " " + str(posting_ref) + "\n" # term docFreq posting_ref
            final_postings += new_posting
            posting_ref += len(new_posting)
        
        final_document += str(total_num_docs)
        for doc_id in doc_len:
            final_document += " (" + str(doc_id) + "," + str(doc_len[doc_id]) + ")" # (docID,lenOfDoc)

        # write out into final dictionary, postings and document files
        print("writing to output files...")
        self.write_content(self.out_dict, final_dictionary)
        self.write_content(self.out_postings, final_postings)
        self.write_content("document.txt", final_document)

    def write_content(self, out_file, content):
        """
        Method to write content into file
        
            Parameters:
                out_file: a file
                content: a string
        """
        f = open(out_file, "w")
        f.write(content)
        f.close()

