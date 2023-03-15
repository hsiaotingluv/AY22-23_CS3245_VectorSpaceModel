import os
from sys import platform
import shutil
import string

from queue import PriorityQueue
from math import sqrt, floor
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.stem.porter import PorterStemmer

class InvertedIndex:
    """
    Class that construct and write data from in_dir into out_dict and out_postings. 
    Using SPIMI-Invert method, we construct dictionary and postings in blocks, then use n-way merging to merge the blocks in order.
    """
    # max 10000 number of terms in memory
    MAX_LINES_IN_MEM = 10000

    def __init__(self, in_dir, out_dict, out_postings):
        """
        Initialise input directory and output files
        """
        print("initialising inverted index...")

        self.in_dir = in_dir
        self.out_dict = out_dict
        self.out_postings = out_postings
    
    def get_all_doc_ids(self):
        """
        Get and and write all sorted doc ids into all_doc_ids.txt

            Returns:
                A list of sorted doc ids
        """
        all_doc_ids = []
        for doc_id in os.listdir(self.in_dir):
            all_doc_ids.append(int(doc_id))
        all_doc_ids.sort()

        # Write to a txt file for search to access all doc_ids 
        with open("all_doc_ids.txt", "w") as file:
            file.write(" ".join(map(str, all_doc_ids)))

        return all_doc_ids
    
    def reset_files(self):
        """
        Method to delete all block, dictionary and posting files generated from the previous indexing, and create a new block directory 
        """
        print("deleting previous test files...")
        if os.path.exists("blocks"):
            # Delete block folder
            shutil.rmtree("blocks")
        os.makedirs("blocks")
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
        # stop_words = set(stopwords.words('english'))
        remove_punctuation = str.maketrans('', '', string.punctuation)
        remove_digit = str.maketrans("", "", string.digits)

        block_index = 0
        mem_line = 0
        all_doc_ids = self.get_all_doc_ids()
        terms = list()
        postings = {} # key: term, value: list of doc_id

        for doc_id in all_doc_ids:
            doc_id = str(doc_id)
            file = open(os.path.join(self.in_dir, doc_id))
            for line in file:
                for sentence_token in sent_tokenize(line):
                    for word_token in word_tokenize(sentence_token):
                        # remove punctuation and digit, stem and case-folding
                        word_token = stemmer.stem(
                            word_token.translate(remove_punctuation).translate(remove_digit)).lower()

                        # remove numbers or empty strings
                        if word_token.isnumeric() or len(word_token) == 0:
                            continue

                        # add word_token into list of terms
                        if word_token not in terms:
                            terms.append(word_token)
                            mem_line += 1

                        # add word_token into posting list
                        if word_token not in postings:
                            postings[word_token] = list()
                            postings[word_token].append(doc_id)
                        else :
                            if doc_id not in postings[word_token]:
                                postings[word_token].append(doc_id)

                        # if max lines in mem reached, write block to disk
                        if mem_line == self.MAX_LINES_IN_MEM:
                            terms.sort()
                            self.write_block_to_disk(block_index, terms, postings)
                            print("Block " + str(block_index) + " created")
                            
                            mem_line = 0
                            block_index += 1
                            terms = list()
                            postings = {} # key: term, value: list of doc_id
    
        if mem_line > 0:
            terms.sort()
            self.write_block_to_disk(block_index, terms, postings)
            self.merge_blocks(block_index + 1)
        else:
            self.merge_blocks(block_index)
        
    def write_block_to_disk(self, block_index, terms, postings):
        """
        Method to write terms and postings into block

            Parameters:
                block_index: an integer
                terms: a list of string
                postings: a dictionary of [term:string : postings:integer[]]
        """
        result = ""
        if terms is not None:
            for term in terms:
                posting = ' '.join(str(i) for i in postings[term])
                result += term + " " + posting + "\n"

            f = open(os.path.join("blocks", "block_" + str(block_index) + ".txt"), "w")
            f.write(result)
            f.close()
    
    def merge_blocks(self, total_num_blocks):
        """
        Method to merge all blocks and write into out_dict and out_postings

            Parameters:
                total_num_blocks: an integer
        """
        print("merging ", total_num_blocks, " numbers of blocks...")
        
        # off set of start line for each block
        start_offset_per_block = [0] * total_num_blocks
        # lines loaded into memory from each block
        line_in_mem_per_block = [0] * total_num_blocks
        # total number of lines to load from each block at each time
        lines_to_read = max(1, floor(self.MAX_LINES_IN_MEM / total_num_blocks))
        # queue item = [term, postings, block_index]
        queue = PriorityQueue() 
        
        # load first set of lines from all blocks and add to queue
        for block_index in range (0, total_num_blocks):
            # read lines_to_read number of lines from block with block_index
            newLines_list = self.read_block(block_index, start_offset_per_block, lines_to_read)
            # add lines into queue and update queue
            queue = self.add_list_to_queue(newLines_list, line_in_mem_per_block, block_index, queue)

        prev_term = ""
        accumulated_postings = []
        final_dictionary = "" # term freq reference
        final_postings = "" # term docIDs...
        posting_ref = 0
        line_in_mem = 0
        last_unique_term = False

        while not queue.empty():
            item = queue.get()
            curr_term = item[0]
            curr_postings = item[1].split() # a list of string
            curr_block_index = item[2]

            line_in_mem_per_block[curr_block_index] -= 1

            # append same term together
            if (prev_term == "" or prev_term == curr_term):
                prev_term = curr_term
                for doc_id in curr_postings:
                    # if doc_id does not exists in current posting yet, add into posting
                    if doc_id not in accumulated_postings:
                        accumulated_postings.append(doc_id)

            # if new term, append previous term to final dictionary and postings
            if (curr_term != prev_term):
                # create and get new lines for dictionary and posting (with skip pointers)
                new_dictionary_posting_line = self.new_line(prev_term, self.sort_postings(accumulated_postings), posting_ref)
                final_dictionary += new_dictionary_posting_line[0]
                final_postings += new_dictionary_posting_line[1]
                # update posting reference by adding length of new posting line (with skip pointers)
                posting_ref += len(new_dictionary_posting_line[1])
                line_in_mem += 1

                # reset values
                prev_term = curr_term
                accumulated_postings = curr_postings

                # check if last term is unique, i.e. different from previous term
                if (queue.empty()):
                    last_unique_term = True
                
            # load another set of lines into queue
            if (line_in_mem_per_block[curr_block_index] == 0):
                # read lines_to_read number of lines from block with curr_block_index
                newLines_list = self.read_block(curr_block_index, start_offset_per_block, lines_to_read)
                # add lines into queue and update queue
                queue = self.add_list_to_queue(newLines_list, line_in_mem_per_block, curr_block_index, queue)

            # write out into dictionary and postings file
            if (line_in_mem == self.MAX_LINES_IN_MEM):
                self.write_block(self.out_dict, final_dictionary)
                self.write_block(self.out_postings, final_postings)

                # reset values
                line_in_mem = 0
                final_dictionary = "" 
                final_postings = ""

        # append last unique term to final dictionary and postings
        if (last_unique_term):
            # create and get new lines for dictionary and posting (with skip pointers)
            new_dictionary_posting_line = self.new_line(curr_term, curr_postings, posting_ref)
            final_dictionary += new_dictionary_posting_line[0]
            final_postings += new_dictionary_posting_line[1]

        # write out into final dictionary and postings
        print("writing to output files...")
        self.write_block(self.out_dict, final_dictionary)
        self.write_block(self.out_postings, final_postings)

    def read_block(self, block_index, start_offset_per_block, lines_to_read):
        """
        Method to read from block with block_index lines_to_read numebr of lines starting from start_offset

            Parameters:
                block_index: an integer
                start_offset_per_block: a dictionary with [block_index:integer : start_offset:integer]
                lines_to_read: an integer
        
            Returns:
                lines_to_read number of lines in block with block_index
        """
        block_path = os.path.join(os.getcwd(), "blocks")
        start_line = start_offset_per_block[block_index]

        f = open(os.path.join(block_path, "block_" + str(block_index) + ".txt"), 'r')
        f.seek(start_line)
        lines = []

        # read from line number start_line to (start_line + lines_to_read - 1)
        for i in range (0, lines_to_read):
            line = f.readline().strip()
            # stop if reaches end of file
            if len(line) == 0:
                break
            lines.append(line)
            start_offset_per_block[block_index] += len(line) + 1 # add 1 for "\n"
        
        f.close()
            
        return lines

    def write_block(self, out_file, content):
        """
        Method to write content into file
        
            Parameters:
                out_file: a file
                content: a string
        """
        f = open(out_file, "a")
        f.write(content)
        f.close()

    def add_list_to_queue(self, newLines_list, line_in_mem_per_block, block_index, queue):
        """
        Method to add the list of new lines into queue and update the lines loaded into memory from block with block_index

            Parameters:
                newLines_list: a list of string
                line_in_mem_per_block: a dictionary with [block_index:integer : line_in_mem:integer]
                block_index: an integer
                queue: a queue with item [term, postings, block_index]
    
            Returns:
                An updated queue
        """
        for line in newLines_list:
                line_in_mem_per_block[block_index] += 1
                term_postings = line.split(" ", 1)
                term = term_postings[0]
                postings = term_postings[1]
                queue.put([term, postings, block_index])
        return queue
    
    def new_line(self, prev_term, accumulated_postings, posting_ref):
        """
        Method to construct a new dictionary line of 'term docFreq posting_ref' and a new posting line of 'term postings_with_skip_pointers'

            Parameters:
                prev_term: a string
                accumulated_postings: a list of string
                posting_ref: an integer
            
            Returns:
                A list of dictionary and posting new lines
        """
        # construct a new dictionary line of 'term docFreq posting_ref'
        new_dictionary_line = prev_term + " " + str(len(accumulated_postings)) + " " + str(posting_ref) + "\n"
    
        # construct a new posting line of 'term postings_with_skip_pointers'
        postings_with_skip_pointers = self.get_postings_with_skip_pointers(accumulated_postings)
        new_posting_line = prev_term + " " + postings_with_skip_pointers + "\n"

        return [new_dictionary_line, new_posting_line]
    
    def get_postings_with_skip_pointers(self, accumulated_postings):
        """
        Method to calculate and get postings with skip pointers

            Parameters:
                accumulated_postings: a list of string
            
            Returns:
                A string of posting list with skip pointers
        """
        length = len(accumulated_postings)
        min_skip_length = 9

        # do not add skip pointers if length of postings is smaller than min_skip_length
        if (length < min_skip_length):
            return ' '.join(accumulated_postings)

        postings_with_skip_pointers = ""
        skip_len = floor(sqrt(length))

        for i in range (0, length):
            if (i % skip_len == 0):
                postings_with_skip_pointers += accumulated_postings[i] + "|" + str(skip_len) + " "
            else:
                postings_with_skip_pointers += accumulated_postings[i] + " "

        return postings_with_skip_pointers

    def sort_postings(self, accumulated_postings):
        """
        Method to sort postings
        
            Parameters:
                accumulated_postings: a list of string

            Returns:
                A list of sorted postings
        """
        list_of_sorted_ids = []
        for doc_id in accumulated_postings:
            list_of_sorted_ids.append(int(doc_id))
        list_of_sorted_ids.sort()
        result = [str(i) for i in list_of_sorted_ids]
        return result
