import re 

class DocumentDictionary():
    """Class which behaves similarly to the dict buildt in structure
This class will be representing a mapping in the form:
(no_book,no_paragraph):text.
Useful for retriving and display documents against the query
    """
    def __init__(self,text = 'bibbina.txt'):
        self._corpus = text
        self._dictionary = {}

    def build_dictionary(self):
        """Pretty messy method:
        scan line per line, creating key in the dictionary 
        as new book or paragraph are found
        """
        with open(self._corpus) as bible:
            book = 1
            previous_paragraph = 0
            for line in bible:  
                if line[0].isdigit():
                    paragraph = int(line.split()[0])
                    if abs(paragraph-previous_paragraph) <= 1:
                        previous_paragraph = paragraph
                        self._dictionary[(book,paragraph)] = []
                    else:
                        book+=1
                        previous_paragraph = paragraph
                        self._dictionary[(book,paragraph)] = []
                else:
                    self._dictionary[(book,paragraph)] += line
            for k in self._dictionary:
                self._dictionary[k] = ''.join(self._dictionary[k])
                
    def assign(self,key,item):
        self._dictionary[key] = item            
                        
    def __getitem__(self,position):
        book,paragraph = position
        try:
            return self._dictionary[(book,paragraph)]
        except:
            return 'Something wrong occurred with keys: ({0},{1})'.format(book,paragraph)

    def keys(self):
        return self._dictionary.keys()


if __name__ == '__main__':
    d = DocumentDictionary()
    d.build_dictionary()
    print(d[(1,1)])
