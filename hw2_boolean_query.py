'''
Parent class for the 3 boolean queries. 
'''
class BooleanQuery:
    def __init__(self, dictionary, postings_file):
        self.dictionary = dictionary
        self.postings_file = postings_file

    '''
    Returns a list of docIDs as strings, e.g. ["1", "5|3", "7" ...]
    '''
    def term_to_doc_ids(self, postings):
        # If postings is a term, retrieve postings list
        if (not isinstance(postings, list)):    
            
            # Locate term in the dictionary --> WHAT IF IT'S NOT INSIDE? NEED TO CATCH RIGHT? 
            doc_frq = self.dictionary[postings][0]
            pointer = self.dictionary[postings][1]

            # Retrieve postings list
            f = open(self.postings_file, 'r')
            f.seek(pointer, 0)
            postings_as_string = f.readline().strip()

            # Put the postings into a list 
            doc_ids = postings_as_string.split()
            postings = doc_ids[1:]

        # Return as a list of strings
        return postings
    
    '''
    Checks if string "2" has skip pointer
    '''
    def has_skip_pointer(self, s):
        if "|" in s:
            return True
        return False
    
    '''
    Takes a string such as "5|3" and returns a tuple of both as ints 
    '''
    def process_doc_id_with_skip(self, s):
        parts = s.split("|")
        doc_id = int(parts[0])
        doc_skip = int(parts[1])
        return (doc_id, doc_skip)

'''
Inherits from the BooleanQuery class.
'''
class AndQuery(BooleanQuery):

    '''
    Calls the intersect method
    '''    
    def eval(self, postings1, postings2):
        # print('Parsing AND query...')

        # The variables postings1 and postings2 could be terms or a list of numbers
        # postings1 = self.term_to_doc_ids(postings1)
        # postings2 = self.term_to_doc_ids(postings2)

        common_documents = self.intersect(postings1, postings2)
        return common_documents
       
    def get_doc_id(self, doc_id_with_skip):
        doc_id = 0
        doc_skip = 0

        if "|" in doc_id_with_skip: 
            parts = doc_id_with_skip.split("|")
            doc_id = int(parts[0])
            doc_skip = int(parts[1])
        
        else: 
            doc_id = int(doc_id_with_skip)

        return (doc_id, doc_skip)

    '''
    Takes in two lists of doc ids and returns a list of common docs.
    IMPLEMENT SKIP POINTERS HERE!!! 
    '''   
    def intersect(self, p1_doc_ids, p2_doc_ids):
        common_documents = []
        # print("Intersecting these two: ", p1_doc_ids)
        # print("Intersecting these two: ", p2_doc_ids)
        i = j = 0
        len1 = len(p1_doc_ids)
        len2 = len(p2_doc_ids)

        doc1_id = None # integer
        doc2_id = None # integer
        doc1_skip = 0 # integer
        doc2_skip = 0 # integer
        # p1_doc_ids has the structure ["1", "5|3", "7" ...] as STRINGS

        while (i < len1 and j < len2): 

            # Process the string in the postings list
            if self.has_skip_pointer(p1_doc_ids[i]): 
                tuple = self.process_doc_id_with_skip(p1_doc_ids[i])
                doc1_id = tuple[0]
                doc1_skip = tuple[1]
            else:
                doc1_id = int(p1_doc_ids[i])
                doc1_skip = 0

            if self.has_skip_pointer(p2_doc_ids[j]): 
                tuple = self.process_doc_id_with_skip(p2_doc_ids[j])
                doc2_id = tuple[0]
                doc2_skip = tuple[1]
            else:
                doc2_id = int(p2_doc_ids[j])
                doc2_skip = 0

            # Matched postings
            if doc1_id == doc2_id:
                common_documents.append(str(doc1_id))
                i += 1
                j += 1

            elif doc1_id < doc2_id:
                # If there is a skip, and the skipped to element is smaller than doc2, take it 
                # print(self.get_doc_id(p1_doc_ids[i + doc1_skip])[0])
                if (self.has_skip_pointer(p1_doc_ids[i]) and i + doc1_skip < len1 and
                    self.get_doc_id(p1_doc_ids[i + doc1_skip])[0] <= doc2_id):

                    # While there is a skip pointer, take it 
                    while (self.has_skip_pointer(p1_doc_ids[i]) and i + doc1_skip < len1 and
                        self.get_doc_id(p1_doc_ids[i + doc1_skip])[0] <= doc2_id):
                        i = i + doc1_skip

                else: # Else, don't take skip pointer
                    i += 1
                    # print('no skip taken')

            else:
                # If there is a skip, and the skipped to element is smaller than doc2, take it 
                if (self.has_skip_pointer(p2_doc_ids[j]) and j + doc2_skip < len2 and
                    self.get_doc_id(p2_doc_ids[j + doc2_skip])[0] <= doc1_id):

                    # While there is a skip pointer, take it 
                    while (self.has_skip_pointer(p2_doc_ids[j]) and j + doc2_skip < len2 and
                        self.get_doc_id(p2_doc_ids[j + doc2_skip])[0] <= doc1_id):
                        j = j + doc2_skip

                else: # Else, don't take skip pointer
                    j += 1

        return common_documents  


'''
Inherits from the BooleanQuery class.
'''
class OrQuery(BooleanQuery):

    ''' 
    Calls the merge method
    '''
    def eval(self, postings1, postings2):
        # print('Parsing OR query...')

        # The variables postings1 and postings2 could be terms or a list of numbers
        # postings1 = self.term_to_doc_ids(postings1)
        # postings2 = self.term_to_doc_ids(postings2)

        common_documents = self.merge(postings1, postings2)
        return common_documents

    '''
    Merge the two postings, the result is a list of documents in ascending order e.g. ['1', '3', '5']
    '''
    def merge(self, p1_doc_ids, p2_doc_ids): 
        common_documents =[]
        i = 0
        j = 0

        doc1_id = None
        doc2_id = None

        # print("Merging these two: ", p1_doc_ids, p2_doc_ids)

        while i < len(p1_doc_ids) and j < len(p2_doc_ids):

            # Strip the doc_id string
            if self.has_skip_pointer(p1_doc_ids[i]):
                tuple = self.process_doc_id_with_skip(p1_doc_ids[i])
                doc1_id = tuple[0]
            else:
                doc1_id = int(p1_doc_ids[i])

            if self.has_skip_pointer(p2_doc_ids[j]):
                tuple = self.process_doc_id_with_skip(p2_doc_ids[j])
                doc2_id = tuple[0]
            else:
                doc2_id = int(p2_doc_ids[j])


            # Merge
            if doc1_id < doc2_id:
                common_documents.append(str(doc1_id))
                i += 1

            elif doc1_id > doc2_id:
                common_documents.append(str(doc2_id))
                j += 1

            elif doc1_id == doc2_id:
                i += 1
                j += 1
            
        common_documents.extend(id.split("|")[0] for id in p1_doc_ids[i:])
        common_documents.extend(id.split("|")[0] for id in p2_doc_ids[j:])
        return common_documents

'''
Inherits from the BooleanQuery class.
'''
class NotQuery(BooleanQuery):

    ''' 
    Calls the get_complement method
    '''
    def eval(self, postings):
        # print('Parsing NOT query...')

        # The variables postings could be a term or list of numbers
        # postings = self.term_to_doc_ids(postings)
        
        # Get all doc ids
        f = open("all_doc_ids.txt", 'r')
        all_docs_in_string = f.readline().strip()

        # Put the docs into a list 
        all_docs = all_docs_in_string.split()
        # all_docs = list(map(int, all_docs)) ---> leave as strings

        complemented_documents = self.get_complement(postings, all_docs)
        return complemented_documents


    ''' 
    Merge the two postings, the result is a list of documents in ascending order e.g. ['1', '3', '5']
    '''
    def get_complement(self, postings, all_docs): 
        complement_documents = []
        i = 0
        j = 0
        doc_id = 0
        # print("Complementing this ", postings)

        while i < len(postings):

            # print(postings[i])

            if self.has_skip_pointer(postings[i]): 
                doc_id = self.process_doc_id_with_skip(postings[i])[0]
                # print(doc_id, all_docs[j])

            else: 
                doc_id = int(postings[i])

            # Only one conditional is needed as the doc ids in postings will always be a subset of all the docs. 
            if doc_id > int(all_docs[j]):
                complement_documents.append(all_docs[j])
                j += 1

            # Discard this document
            if doc_id == int(all_docs[j]):
                i += 1
                j += 1

        # Add the rest of the complemented documents
        complement_documents.extend(all_docs[j:])

        return complement_documents


