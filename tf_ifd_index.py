from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from document_dictionary import DocumentDictionary
from nltk.corpus import stopwords
import re
import nltk
from nltk.stem import SnowballStemmer
from dictionary import Dictionary
from collections import defaultdict
from math import log

class WeightedIndex():
    """Class implementing a simple index for boolean retrival
    """

    def __init__(self,text='bibbia.txt'):
        self._corpus = text
        self._index = {}
        self._document_dictionary = DocumentDictionary(text='bibbia.txt')
        self._document_dictionary.build_dictionary()
        self._boolean_index = None
        #clean dictionary is a map (book,par)-->normalized list of strings
        self._cleaned_dictionary = None
        self._cleaned_dictionary_abs = None
        self._dictionary = None
        self._index = None
        #total number of documents in the collection
        self._N = self._document_dictionary.no_documents
        

    def clean_text(self):
        """Remove punctuation from the text, then tokenize it and stem it.
           Meanwhile creates a running set which will be the (stemmed) vocabulary,
           object to pass to the Dictioanry object 
           
        """
        #Create a second object which will become the cleaned dictionary
        cleaned_dictionary = DocumentDictionary(text='bibbia.txt')
        cleaned_dictionary.build_dictionary()
        
        #Create the set of the stopwords for rapid check
        stopword = set(stopwords.words('italian'))
     
        #Create a set to be a dictionary_set
        dict_set = set()
        for k in cleaned_dictionary.keys():
            #First need to eliminate apostrophe to not have false compound terms
            par = re.sub('\'',' ',cleaned_dictionary[k])
            tokens_text = nltk.Text(nltk.wordpunct_tokenize(par))
            #Eliminates all non textual chars
            final = [w.lower() for w in tokens_text if w.isalpha()]
            final_no_sw = [w for w in final if w not in stopword]
            #Apply stemming
            s = SnowballStemmer('italian')
            final_no_sw_stemmed = [s.stem(w) for w in final_no_sw]
            dict_set.update(set(final_no_sw_stemmed))
            cleaned_dictionary.assign(k,final_no_sw_stemmed)
        self._cleaned_dictionary = cleaned_dictionary
        self._dict_set = dict_set
        

    def create_dict(self):
        d = Dictionary(self._dict_set)
        d.build_dictionary()
        self._dictionary = d 


    def get_dict(self):
        return self._dictionary

    def create_double_dictionary(self):
        """Creates to dictioanary : one maps from keys to absolute numbers
           the other maps from absolute number to keys
           At the end creates a dictionary with absulute values fo
           the construction of the index
        """
        #Creates keys to abs
        dict_keyss = sorted(list(self._document_dictionary.keys()))
        absolute = list(range(len(dict_keyss)))
        keys_to_abs = dict(list(zip(dict_keyss,absolute)))  
        abs_to_keys = {v:k for (k,v) in keys_to_abs.items()}
        self._keys_to_abs = keys_to_abs
        self._abs_to_keys = abs_to_keys  
        
        #Creating absolute index
        cleaned_dictionary_abs = dict([(keys_to_abs[k],self._cleaned_dictionary[k]) for k in self._cleaned_dictionary.keys()])
        self._cleaned_dictionary_abs = cleaned_dictionary_abs
    
    def create_boolean_index(self):
        """Creates the index scanning through the cleaned_dictionary abs
           leverages on defaultdict to not check everytime the properties
           Index is a dictionary
        """
        index = defaultdict(set)
        #no couting index-->surrogate of a boolean matrix
        for k in self._cleaned_dictionary_abs.keys():
            for w in self._cleaned_dictionary_abs[k]:
                index[w].update({k})

        self._boolean_index = index

    
    def compute_document_frequency(self):
        """Computes the df term. Period.
        """
        N = self._dictionary.dict_len
        idf_dict = {term:log(N/len(self._boolean_index[term])) for term in self._dictionary}
        self.idf_dict = idf_dict
          

    def compute_term_frequency(self):
        """Computes the df term, stored as a dict--> term:[(1,df1),(2,df2)...]
           If a term doesn't appear in a document (0 in the implicit matrix),
           just don't store anything. Every list is kept in order.
           Anyway the matrix can be completely reconstructed with this dictionary
        """
        tf_dict = defaultdict(list)
        #Creates a boolean index to not useless check 
        #already ordered dictionary of words
        for term in self._dictionary:
            #get the posting list of the term and count only in the posting list
            posting_list = list(self._boolean_index[term])
            for idx in posting_list:
                #now compute the occurrences of the term in the document idx
                occurrences = self._cleaned_dictionary_abs[idx].count(term) 
                tf_dict[term].append((idx,occurrences))
        self.tf_dict = tf_dict
       
    def build_tfidf_dict(self):
        """This function will complete the tfidf score
           Is again a fucking dictionary
           This stuff really need some refactoring mate.
        """ 
        #nested
        def compute(term,tuple_sequence):
            to_return = [(i,v*self.idf_dict[term]) for (i,v) in tuple_sequence]
            return to_return 

        tf_idf_dict = {term:compute(term,self.tf_dict[term]) for term in self.tf_dict}
        self.tf_idf_dict = tf_idf_dict
               
#    def create_invereted_index(self):
#       d = self._clean_dictionary_abs

if __name__ == '__main__':
    w = WeightedIndex()
    w.clean_text()
    w.create_dict()
    w.create_double_dictionary()
    w.create_boolean_index()
    w.compute_document_frequency()
    w.compute_term_frequency()
    w.build_tfidf_dict()
