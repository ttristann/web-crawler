import os.path
import sys

class Parser:

    def __init__(self):
        self.count_per_word = {} # {word: count, ...}
        self.url_total_words = {} # {url: total word count}

    # reads through each line of text file and tokenizes words
    def tokenize(self,stringDoc, url):
            tokens = []
            word = ""

            for char in stringDoc:
                # we will check via ascii number. If it is a (number or char): (then keep), else: (ignore)
                if((65 <= ord(char) <= 90) or (97<=ord(char)<=122) or (48<=ord(char)<=57)):
                    word += char.lower()

                elif word != "": # ensures we are not adding an empty string to the tokens list
                    tokens.append(word)
                    word = ""
 
            self.computeWordFrequencies(tokens, url)



    #creates dictionary updates final Dict with new words
    def computeWordFrequencies(self,tokens, url):
        stop_words = {
        "i", "a", "about","an","are","as","at","be","by","com","for", "from",
        "how","in","is","it","of","on","or","that","the","this",
        "to","was","what","when","where","who","will","with","www"}
        count = 0
        for word in tokens: #iterate through each "token"
            if(word not in stop_words): #ensure word is not a stop word. 
                # add content 
                if (word in self.count_per_word): 
                    self.count_per_word[word] += 1
                else:
                    self.count_per_word[word] = 1
                count += 1
                
        self.url_total_words[url] = count

  

    def getURLTotalWords(self):
        return self.url_total_words
    
    def getMaxWordsUrl(self):
        return sorted(self.url_total_words.items(), key=lambda x: (-x[1], x[0]))[0]
    
    def getTopFifty(self):
        # sorts data. First elements are most word counts
        return sorted(self.count_per_word.items(), key=lambda tokens:(-tokens[1], tokens[0]))[:50]



