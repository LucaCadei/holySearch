class Dictionary():
    """Wrapper for a list that ecapsulates the dictionary
    """
    def __init__(self,dict_set):
        self._dict_set = dict_set
        self._token_dictionary = None
        self.dict_len = None
 
    def build_dictionary(self):
        listed_dict = list(self._dict_set)
        listed_dict.sort()
        self._token_dictionary = listed_dict
        self.dict_len = len(listed_dict)
        

    def __getitem__(self,k):
        return self._token_dictionary[k]

