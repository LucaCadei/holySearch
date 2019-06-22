from simple_index import SimpleIndex
from nltk.stem import SnowballStemmer
from tf_ifd_index import WeightedIndex
import re
import nltk
from nltk.corpus import stopwords
from collections import Counter, defaultdict
from math import sqrt
import time

#TODO MEGLIO GENERALIZZARE TUTTO PER LE PROSSIME QUERY
class Query():
    """This class will be the interface between the user need
       and the underling information retrival system.
       The user can select which kind of query has to be done.
       Data structures are created run time depending on this 
    """
 
    def __init__(self, kind='tf_idf'):
        #for the boolean, for the next time it'll be a class methods to do everything
        self._query_kind = kind
#        self._index = SimpleIndex()
#        self._index.clean_text()
#        self._index.create_dict()
#        self._index.create_double_dictionary()
#        self._index.create_index()
        self.tf_idf_index = WeightedIndex()
        self.tf_idf_index.clean_text()
        self.tf_idf_index.create_dict()
        self.tf_idf_index.create_double_dictionary()
        self.tf_idf_index.create_boolean_index()
        self.tf_idf_index.compute_document_frequency()
        self.tf_idf_index.compute_term_frequency()
        self.tf_idf_index.build_tfidf_dict()
   
        self.normalized_document_length_dict = None


    def boolean_query(self, query = 'jesus AND christ'):
        """Given the boolean query, process it to match the same 
           processing of the text, and then retive the document by index
        """
        #Text processing of the query
        #Supposing to be given a well formed string : 'word1 AND/OR word2 AND/OR ...' 
        #This will be a super stupid example before I know well regex
        #just suppose one AND or OR between 2 words
        splitted = query.split()
        s = SnowballStemmer('italian')
        operation = 0
        if splitted[1] == 'AND':
            operation = 1
        else:
            operation = 0
        #TODO cambiare questa porcheria
        stemmed = [s.stem(term) for term in query.split() if (term != 'AND' and term != 'OR')]
        print(stemmed)
        results = set()
        if operation:
            results = set(self._index[stemmed[0]])
            print('results : ',results)
            #print(type(results))
            for term in stemmed:
                print(self._index[term])
                results = results.intersection(self._index[term])
        else:
            for term in stemmed:
                results = results.update(self._index[term])
        self.print_documents(results)

    def print_documents(self,retrived):
        for number in sorted(list(retrived)):
            book, par = self._index._abs_to_keys[number]
            print('Book : {}   ---   Paragraph : {}'.format(book,par))
            print(self._index.get_absolute(number))
    
    def tf_idf_query(self, query='cielo'):
        """Clean the query, create a list. Then, for each document in the corpus, 
           compute the sum of the tf_idf score
           PORCODDIO È LENTISSIMO
           To gain some speed up I calculate the score iff all query term are in the document
        """
        query = re.sub('\'',' ',query)
        tokens_text = nltk.Text(nltk.wordpunct_tokenize(query))
        #Eliminates all non textual chars
        final = [w.lower() for w in tokens_text if w.isalpha()]
        stopword = set(stopwords.words('italian'))
        final_no_sw = [w for w in final if w not in stopword]        
        s = SnowballStemmer('italian')
        #TODO FIX HE STOPWORDS PROBLEM
        query_list = [s.stem(term) for term in final_no_sw]
        print(query_list)
        

        #Compute the fucking score (not) for each fucking document
        retrived = []#will be in form:(n_doc,score)
        for idx in range(len(self.tf_idf_index._cleaned_dictionary_abs)):
#            print(set(self.tf_idf_index._cleaned_dictionary_abs[idx]))
            print(set(query_list))
            print(set(query_list) <= set(self.tf_idf_index._cleaned_dictionary_abs[idx]))
            if set(query_list)<=set(self.tf_idf_index._cleaned_dictionary_abs[idx]):
                #devo cercare nella lista dei doc:tf associata ai termini della query il termine corrispondente 
                #print(self.tf_idf_index.tf_idf_dict[q])
                total_list = [dict(self.tf_idf_index.tf_idf_dict[q])[idx] for q in query_list]
                #print(total_list)
                retrived.append((idx,sum(total_list)))
        
        #sort the retrived from the descending order with key the tf_idf
        sorted_retrived = sorted(retrived,key=lambda x: x[1], reverse=True)
        
        #TODO considerare solo i top k retrived o qualche altro metodo di cutoff
        
        self.last_retrived = sorted_retrived
    
    #Superdumb and slow version
    def cosine_query(self,query='uccisione di re erode'):
        """Implementation of the algorithm by Manning, Introduction to Information retrival, p.125
        """
        #First I calculate tf-idf score of the query
        #Firstly I clean the query and create a list
        tokens_text = nltk.Text(nltk.wordpunct_tokenize(query))
        #Eliminates all non textual chars
        final = [w.lower() for w in tokens_text if w.isalpha()]
        stopword = set(stopwords.words('italian'))
        final_no_sw = [w for w in final if w not in stopword]        
        s = SnowballStemmer('italian')
        query_list = [s.stem(term) for term in final_no_sw]
        #Term Frequency 
        plain_count = Counter(query_list)
        #multiply by the general inverted docuement frequency
        for term in plain_count:
            plain_count[term] *= self.tf_idf_index.idf_dict[term]
        
        #Now I calculate all the scores for all the docuemnt
        
        #First I need to calculate the length of all the tf-idf documents in the corspus
        #My god this will be rough
   
        lengths = defaultdict(list)
   
        for term in self.tf_idf_index.tf_idf_dict:
            for couple in self.tf_idf_index.tf_idf_dict[term]:
                lengths[couple[0]].append(couple[1])
 
        for idx in range(len(lengths)):
            lengths[idx] = sqrt(sum([x**2 for x in lengths[idx]]))
        print(lengths)
        self.lengths = lengths
        
        #FINITO IL CALCOLO DEI FATTORI DI NORMALIZZAZIONE
        scores = defaultdict(list)
        #computing the dot product
        for t in plain_count:
            posting_t = self.tf_idf_index.tf_idf_dict[t]
            for el in posting_t:
                scores[el[0]].append(el[1]*plain_count[t])
        #normalization
        for i in scores: 
                scores[i] = sum(scores[i])/lengths[i] 
        
        #Computing the top k sorting the array WOULD BE BETTER IF I HAD A FUCKING HEAP
        print(scores)
        scores = list(scores.items())
        sorted_scores = sorted(scores, key= lambda x:x[1],reverse=True)
        
        self.last_retrived = sorted_scores[:3]        

 
    def print_tf_idf(self):
        for i in range(3):
            print(self.tf_idf_index._abs_to_keys[self.last_retrived[i][0]])
            print(self.tf_idf_index._document_dictionary[self.tf_idf_index._abs_to_keys[self.last_retrived[i][0]]])
            print('\n\n')
            
        
if __name__ == '__main__':
    tic = time.time()
    q = Query()
    #q.boolean_query('vantaggio AND fatica')
    #print(results)
    #q.tf_idf_query('davide e golia')
    #q.print_tf_idf() 
    q.cosine_query()
    q.print_tf_idf()
    toc = time.time()
    print('Elapsed time --> {}'.format(toc-tic))
    query = input('Chiedi e ti sarà dato --> ')
    while query != 'quit':
        q.cosine_query(query)
        q.print_tf_idf()
        query = input('Chiedi e ti sarà dato --> ')

