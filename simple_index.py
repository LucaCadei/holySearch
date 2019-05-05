from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 
from document_dictionary import DocumentDictionary
from nltk.corpus import stopwords
import re
import nltk
from nltk.stem import SnowballStemmer
from dictionary import Dictionary
from collections import defaultdict

class SimpleIndex():
    """Class implementing a simple index for boolean retrival
    """

    def __init__(self,text='bibbina.txt'):
        self._corpus = text
        self._index = {}
        self._document_dictionary = DocumentDictionary(text='bibbina.txt')
        self._document_dictionary.build_dictionary()
        self._index = None
        #clean dictionary is a map (book,par)-->normalized list of strings
        self._cleaned_dictionary = None
        self._cleaned_dictionary_abs = None
        self._dictionary = None
        self._index = None
        

    def clean_text(self):
        """Remove punctuation from the text, then tokenize it and stem it.
           Meanwhile creates a running set which will be the (stemmed) vocabulary,
           object to pass to the Dictioanry object 
           
        """
        #Create a second object which will become the cleaned dictionary
        cleaned_dictionary = DocumentDictionary(text='bibbina.txt')
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

    def __getitem__(self,position):
        book, paragraph = position
        try:
            return self._cleaned_dictionary[(book,paragraph)]
        except:
            return 'Something wrong occurred with keys: ({0},{1})'.format(book,paragraph)

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

    #TODO creates the index based on the choice of the user
    def create_index(self, index='boolean'):
        create_boolean_index()

    def create_boolean_index(self):
        """Creates the index scanning through the cleaned_dictionary abs
           leverages on defaultdict to not check everytime the properties
        """
        index = defaultdict(set)
        #no couting index-->surrogate of a boolean matrix
        for k in self._cleaned_dictionary_abs.keys():
            for w in self._cleaned_dictionary_abs[k]:
                index[w].update({k})

        self._index = index
     
if __name__ == '__main__':
    i = SimpleIndex()
    i.clean_text()
    #print(i[(1,1)])
    i.create_dict()
    #d = i.get_dict()
    i.create_double_dictionary()
    i.create_boolean_index()
 
            
        

    

