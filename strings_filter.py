from words_finder_singleton import finder


class StringsFilter(object):
    def __init__(self, min_key_length, word_content_threshold, blacklists):
        self.min_key_length = min_key_length
        self.word_content_threshold = word_content_threshold
        self.blacklist = set()
        for txt in blacklists:
            for line in open(txt, "r"):
                self.blacklist.add(line.replace('\n', '').replace('\r', ''))

    def pre_filter(self, string):
        """
         Used to preprocess the input of the classifier. Invalid strings (strings that cannot be API Keys)
         are directly filtered through this function

         :param string: the string that should be evaluated
         :type string: string
         :return: False if it can't be an API key, True otherwise
         """
        # filter short and invalid strings
        if not string or len(string) < self.min_key_length:
            return False
        # filter keys in blacklist
        if self.blacklist and string in self.blacklist:
            return False
        # and string that are just hex numbers (e.g. Android's R values)
        if string.startswith(('0x', '0X', '-0x', '-0X')):
            if string.endswith('L'):
                s = string[:-1]
            else:
                s = string
            try:
                int(s, 16)
                return False
            except ValueError:
                pass
        return True

    def pre_filter_mystring(self, mystring):
        """
        MyString version of pre_filter

        :param mystring: the string that should be evaluated
        :type mystring: MyString
        :return: False if it can't be an API key, True otherwise
        """
        if not mystring:
            return False
        else:
            return self.pre_filter(mystring.value)

    def post_filter(self, string):
        if finder.get_words_percentage(string) >= self.word_content_threshold:
            return False
        return True

    def post_filter_mystring(self, mystring):
        if not mystring:
            return False
        else:
            return self.post_filter(mystring.value)
