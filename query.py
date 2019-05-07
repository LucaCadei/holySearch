from simple_index import SimpleIndex
from nltk.stem import SnowballStemmer
from tf_ifd_index import WeightedIndex
import re
import nltk
from nltk.corpus import stopwords

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
            #print(set(query_list))
            #print(set(query_list) <= set(self.tf_idf_index._cleaned_dictionary_abs[idx]))
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

    def print_tf_idf(self):
        for i in range(5):
            print(self.tf_idf_index._abs_to_keys[self.last_retrived[i][0]])
            print(self.tf_idf_index._document_dictionary[self.tf_idf_index._abs_to_keys[self.last_retrived[i][0]]])
            print('\n\n')
            
        
if __name__ == '__main__':
    q = Query()
    #q.boolean_query('vantaggio AND fatica')
    #print(results)
    q.tf_idf_query('l\'arca di noe')
    q.print_tf_idf()

