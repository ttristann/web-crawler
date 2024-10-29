import os.path
import sys

class Parser:

    def __init__(self):
        self.totalData = {}
        self.finalDict = {}

    # reads through each line of text file and tokenizes words
    def tokenize(self,url, stringDoc):
            tokens = []
            word = ""

            for char in stringDoc:
                # we will check via ascii number. If it is a (number or char): (then keep), else: (ignore)
                if((65 <= ord(char) <= 90) or (97<=ord(char)<=122) or (48<=ord(char)<=57)):
                    word += char.lower()

                elif word != "": # ensures we are not adding an empty string to the tokens list
                    tokens.append(word)
                    word = ""
 
            self.computeWordFrequencies(tokens)


    #creates dictionary updates final Dict with new words
    def computeWordFrequencies(self,tokens):
        stop_words = {
        "i", "a", "about","an","are","as","at","be","by","com","for", "from",
        "how","in","is","it","of","on","or","that","the","this",
        "to","was","what","when","where","who","will","with","www"}

        for word in tokens: #iterate through each "token"
            if(word not in stop_words): #ensure word is not a stop word. 

                # add content 
                if (word in self.finalDict): 
                    self.finalDict[word] += 1
                else:
                    self.finalDict[word] = 1

        print(self.finalDict)


    # sorts data. First elements are most word counts
    
    def displayCount(wordCounts):
        finalData = sorted(wordCounts.items(), key=lambda tokens:(-tokens[-1], tokens[0])) #https://www.freecodecamp.org/news/sort-dictionary-by-value-in-python/
        for pair in finalData:
            print(f"{pair[0]} -> {pair[1]}")

    #
    def fileSimilarity(self,tokens1, tokens):
        tokens1 = computeWordFrequencies(tokenize(file1)) # O(n) + O(n)
        tokens2 = computeWordFrequencies(tokenize(file2)) # O(n) + O(n)
        final = [] #purely for testing purposes
        smallest = tokens1
        biggest = tokens2

        # because we are checking similar words, we can iterate through the smaller dictionary to reduce
        # some run time. ex:{1,2} vs {1,2,3,4,5,6,7,8,9,10}, Why iterate through all 10 if the most common
        # words share between both dictionaries is dic 2. Len() is O(1) time.

        if len(tokens2) < len(tokens1):
            smallest = tokens2
            biggest = tokens1

        count = 0
        for key,value in smallest.items(): #O(n)
            if key in biggest:
                final.append(key)
                count += 1
        return count

    #finalDict will hold the ultimate sized dictionary with every word
    #this function simply adds the words from second into finalDict

