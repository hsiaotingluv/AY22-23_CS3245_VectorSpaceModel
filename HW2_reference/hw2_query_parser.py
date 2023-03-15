from boolean_query import BooleanQuery, AndQuery, OrQuery, NotQuery
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
import string

class QueryParser:
    
    def __init__(self, dictionary, postings_file):
        # print('Starting search...')
        self.dictionary = dictionary
        self.postings_file = postings_file
        self.BooleanQuery = BooleanQuery(dictionary, postings_file)
        self.ANDquery = AndQuery(dictionary, postings_file)
        self.ORquery = OrQuery(dictionary, postings_file)
        self.NOTquery = NotQuery(dictionary, postings_file)

    '''
    Returns a postfix notation expression to be evaluated
    '''
    def shunting_yard(self, query):
        # print("Beginning Shunting Yard Algorithm")

        # Operator precedence dictionary
        precedence = {"(": 3, ")": 3, "NOT": 2, "AND": 1, "OR": 0}

        # Stack to hold operators and parentheses
        operator_stack = []
        # Output queue to hold the postfix notation
        output_queue = []

        # Tokenize the query string 
        tokens = query.split()
        
        # Loop through to separate parenthesis
        separated_tokens = []
        for token in tokens:
            if "(" in token:
                separated_tokens.append("(")
                separated_tokens.append(token.replace("(", ""))
            elif ")" in token:
                separated_tokens.append(token.replace(")", ""))
                separated_tokens.append(")")
            else:
                separated_tokens.append(token)

        # Join the separated tokens back into a string, then tokenize
        separated_query = " ".join(separated_tokens)
        tokens = separated_query.split()

        for token in tokens:

            if token in precedence:
                # If token is an operator or parenthesis
                if token == "(":
                    # Left parenthesis, push onto the operator stack
                    operator_stack.append(token)
                elif token == ")":
                    # Right parenthesis, pop operators from stack to output queue
                    while operator_stack[-1] != "(":
                        output_queue.append(operator_stack.pop())
                    
                    # Discard the left parenthesis
                    operator_stack.pop()
                else: 
                    # Token is an operator
                    while operator_stack and operator_stack[-1] != "(" and precedence[token] <= precedence[operator_stack[-1]] and precedence[token] != "NOT":
                        output_queue.append(operator_stack.pop())
                    operator_stack.append(token)

            else: 
                # Token is an operand, push onto output queue
                # Stem and tokenize the term
                stemmer = PorterStemmer()
                remove_punctuation = str.maketrans('', '', string.punctuation)
                remove_digit = str.maketrans("", "", string.digits)

                word_token = sent_tokenize(token)
                word_token = word_tokenize(word_token[0])
                word_token = stemmer.stem(word_token[0].translate(remove_punctuation).translate(remove_digit)).lower()
                output_queue.append(word_token)

        # Pop remaining operators from stack to output queue
        while operator_stack:
            output_queue.append(operator_stack.pop())

        # Return the postfix notation as a string
        return " ".join(output_queue)


    '''
    Returns the matching postings to be written
    '''
    def evaluatePostfix(self, postfix_expression):
        # print("Beginning Postfix evaluation")        
        
        # Create an empty stack for operands 
        postings_stack = []

        # Tokenize the postfix expression
        tokens = postfix_expression.split()
        # print("This is the postfix expression: ", tokens)

        # Loop over the tokens in the expression
        for token in tokens:
            '''
            token is either a 'term' to be retrieved from the dictionary, or 
            an array containing a single string of postings
            '''

            if token == "AND":

                # -- Optimisation --
                # Recursively call itself?
                # ------------------

                # Pop the two top operands and apply the AND operator
                postings1 = postings_stack.pop()
                postings2 = postings_stack.pop()
                result = self.ANDquery.eval(postings1, postings2)
                postings_stack.append(result) 

            elif token == "OR":
                # Pop the two top operands and apply the OR operator
                postings1 = postings_stack.pop()
                postings2 = postings_stack.pop()
                result = self.ORquery.eval(postings1, postings2)
                postings_stack.append(result) 

            elif token == "NOT":
                # Pop the top operand and apply the NOT operator
                postings = postings_stack.pop()
                result = self.NOTquery.eval(postings)
                postings_stack.append(result)
                
            else: 
                # Token is an operand, append to stack
                # Token is either a TERM or a posting list of docIDs ["12", "14", ...]

                # If it's a list, it won't have the skip pointers. 
                # If it's a term, need to add it to unstrip anyway... 

                token =self.BooleanQuery.term_to_doc_ids(token)
                postings_stack.append(token)

        # At the end of the loop, the final result of the expression is on top of the stack
        # return (" ".join(map(str, postings_stack[-1]))).replace("|", "")
        result = [id.split("|")[0] for id in postings_stack[-1]]
        return (" ".join(result))


    