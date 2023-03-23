from math import log
from math import sqrt
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer

class VectorSearchModel:

    def __init__(self, dictionary, postings_file):
        print('Initiating Vectore Space Model...')
        self.dictionary = dictionary
        self.postings_file = postings_file
        self.doc_lengths = self.get_doc_lens()

    '''
    In the searching step, you will need to rank documents by cosine similarity based on tf×idf. 
    
    In terms of SMART notation of ddd.qqq, you will need to implement the lnc.ltc ranking scheme (i.e., log tf and idf with cosine normalization for queries documents, and log tf, cosine normalization but no idf for documents.) 
    
    Compute cosine similarity between the query and each document, with the weights follow the tf×idf calculation, where term freq = 1 + log(tf) and inverse document frequency idf = log(N/df) (for queries). That is,
    '''
    def cosine_score(self, query):
        print('Beginning cosine calculation')
        scores= {} # Should contain all documents

        # Split the query into individual terms
        terms = query.split()

        # Tokenise the terms
        stemmer = PorterStemmer()
        for i, t in enumerate(terms):
            word_token = sent_tokenize(t)
            word_token = word_tokenize(word_token[0])
            word_token = stemmer.stem(word_token[0]).lower()
            terms[i] = word_token

        # Calculate normalised query vectors: w_tq
        normalised_query_vectors = self.get_normalised_query_vectors(terms)

        # For each term in the query
        for term in normalised_query_vectors:
            # 1. Fetch w_tq 
            w_tq = normalised_query_vectors[term]
            
            try: 
                # Fetch postings list of term (as tuples)
                postings = self.get_postings(term)

                # 2. For each pair (d, w_td) in postings list:
                for doc in postings: 
                    # Retrieve normalised w_td
                    doc_id = doc[0]
                    w_td = doc[1] 

                    # Calculate the cosine similarity between w_t,q and w_t,d
                    # Add result to scores {}
                    if doc_id not in scores: 
                        scores[doc_id] = w_tq * w_td
                    else:
                        scores[doc_id] += w_tq * w_td
            except:
                pass
 
        # Normalise scores
        for doc_id in scores:
            scores[doc_id] = scores[doc_id] / self.doc_lengths[doc_id]

        # Return top K components of the scores
        sorted_scores = sorted(scores.items(), key=lambda x: (-x[1], x[0]))

        top_10_keys = [key for key, value in sorted_scores][:10]
        return top_10_keys
            

    '''
    Function to get the length of doc vectors from document.txt
    Return: dictionary with doc ids as keys, and N as values
    '''
    def get_doc_lens(self):
        f = open('document.txt', 'r')
        docs_as_string = f.readline().strip()
        docs = docs_as_string.split()
        docs = docs[1:]

        # Convert to tuples (docID, doc_len)
        docs_as_tuples = [(str(s[0]), float(s[1])) for s in [s.strip('()').split(',') for s in docs]]

        # Return as dictionary
        doc_lengths = {}
        for doc in docs_as_tuples:
            doc_id = doc[0]
            N = doc[1]
            doc_lengths[doc_id] = N

        return doc_lengths


    '''
    Return postings as a list of tuples

    Format: (docID,w_td), ...
    e.g. (135,1.0) (411,1.0) ... (10268,1.3010...)
    '''
    def get_postings(self, term):
        # Locate term postings list 
        pointer = self.dictionary[term][1]
        f = open(self.postings_file, 'r')
        f.seek(pointer, 0)
        postings_as_string = f.readline().strip()

        # Put postings into a list 
        elements = postings_as_string.split()
        postings = elements[1:]

        # Convert to tuples
        postings_as_tuples = [(str(s[0]), float(s[1])) for s in [s.strip('()').split(',') for s in postings]]

        return postings_as_tuples

    '''
    Calculate the weight of term query

    Returns a dictionary of terms, with their corresponding normalised w_tq. 
    '''
    def get_normalised_query_vectors(self, terms):

        sum_of_squares = 0
        weight_of_terms = {} 
        normalised_weight_of_terms = {}

        all_doc_ids_file = open('all_doc_ids.txt', 'r')
        ids = all_doc_ids_file.readline()
        N = len(ids.split())

        # Add w_t to weight_of_terms
        for t in terms: 
            if t not in weight_of_terms: 
                # 1. Calculate tf_weight
                term_freq = terms.count(t)
                tf_weight = 1 + log(term_freq, 10)

                # 2. Calculate idf_weight
                if t in self.dictionary:
                    doc_freq = self.dictionary[t][0]
                    idf_weight = log(N/doc_freq, 10)
                else: 
                    idf_weight = 0

                # 3. Calculate tf.idf weighting
                w_tq = tf_weight * idf_weight
                sum_of_squares += w_tq * w_tq
                weight_of_terms[t] = w_tq

        length_of_query_vector = sqrt(sum_of_squares)
        
        # Normalise the vectors 
        for t in weight_of_terms:
            normalised_w_tq = weight_of_terms[t] / length_of_query_vector
            normalised_weight_of_terms[t] = normalised_w_tq

        # Return the dictionary of normalised terms
        return normalised_weight_of_terms
    