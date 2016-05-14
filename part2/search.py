#!/usr/bin/env python
import cPickle
import time
import math
import string

"""Porter Stemming Algorithm
This is the Porter stemming algorithm, ported to Python from the
version coded up in ANSI C by the author. It may be be regarded
as canonical, in that it follows the algorithm presented in

Porter, 1980, An algorithm for suffix stripping, Program, Vol. 14,
no. 3, pp 130-137,

only differing from it at the points maked --DEPARTURE-- below.

See also http://www.tartarus.org/~martin/PorterStemmer

The algorithm as described in the paper could be exactly replicated
by adjusting the points of DEPARTURE, but this is barely necessary,
because (a) the points of DEPARTURE are definitely improvements, and
(b) no encoding of the Porter stemmer I have seen is anything like
as exact as this version, even with the points of DEPARTURE!

Vivake Gupta (v@nano.com)

Release 1: January 2001

Further adjustments by Santiago Bruno (bananabruno@gmail.com)
to allow word input not restricted to one word per line, leading
to:

release 2: July 2008
"""

import sys

class PorterStemmer:

    def __init__(self):
        """The main part of the stemming algorithm starts here.
        b is a buffer holding a word to be stemmed. The letters are in b[k0],
        b[k0+1] ... ending at b[k]. In fact k0 = 0 in this demo program. k is
        readjusted downwards as the stemming progresses. Zero termination is
        not in fact used in the algorithm.

        Note that only lower case sequences are stemmed. Forcing to lower case
        should be done before stem(...) is called.
        """

        self.b = ""  # buffer for word to be stemmed
        self.k = 0
        self.k0 = 0
        self.j = 0   # j is a general offset into the string

    def cons(self, i):
        """cons(i) is TRUE <=> b[i] is a consonant."""
        if self.b[i] == 'a' or self.b[i] == 'e' or self.b[i] == 'i' or self.b[i] == 'o' or self.b[i] == 'u':
            return 0
        if self.b[i] == 'y':
            if i == self.k0:
                return 1
            else:
                return (not self.cons(i - 1))
        return 1

    def m(self):
        """m() measures the number of consonant sequences between k0 and j.
        if c is a consonant sequence and v a vowel sequence, and <..>
        indicates arbitrary presence,

           <c><v>       gives 0
           <c>vc<v>     gives 1
           <c>vcvc<v>   gives 2
           <c>vcvcvc<v> gives 3
           ....
        """
        n = 0
        i = self.k0
        while 1:
            if i > self.j:
                return n
            if not self.cons(i):
                break
            i = i + 1
        i = i + 1
        while 1:
            while 1:
                if i > self.j:
                    return n
                if self.cons(i):
                    break
                i = i + 1
            i = i + 1
            n = n + 1
            while 1:
                if i > self.j:
                    return n
                if not self.cons(i):
                    break
                i = i + 1
            i = i + 1

    def vowelinstem(self):
        """vowelinstem() is TRUE <=> k0,...j contains a vowel"""
        for i in range(self.k0, self.j + 1):
            if not self.cons(i):
                return 1
        return 0

    def doublec(self, j):
        """doublec(j) is TRUE <=> j,(j-1) contain a double consonant."""
        if j < (self.k0 + 1):
            return 0
        if (self.b[j] != self.b[j-1]):
            return 0
        return self.cons(j)

    def cvc(self, i):
        """cvc(i) is TRUE <=> i-2,i-1,i has the form consonant - vowel - consonant
        and also if the second c is not w,x or y. this is used when trying to
        restore an e at the end of a short  e.g.

           cav(e), lov(e), hop(e), crim(e), but
           snow, box, tray.
        """
        if i < (self.k0 + 2) or not self.cons(i) or self.cons(i-1) or not self.cons(i-2):
            return 0
        ch = self.b[i]
        if ch == 'w' or ch == 'x' or ch == 'y':
            return 0
        return 1

    def ends(self, s):
        """ends(s) is TRUE <=> k0,...k ends with the string s."""
        length = len(s)
        if s[length - 1] != self.b[self.k]: # tiny speed-up
            return 0
        if length > (self.k - self.k0 + 1):
            return 0
        if self.b[self.k-length+1:self.k+1] != s:
            return 0
        self.j = self.k - length
        return 1

    def setto(self, s):
        """setto(s) sets (j+1),...k to the characters in the string s, readjusting k."""
        length = len(s)
        self.b = self.b[:self.j+1] + s + self.b[self.j+length+1:]
        self.k = self.j + length

    def r(self, s):
        """r(s) is used further down."""
        if self.m() > 0:
            self.setto(s)

    def step1ab(self):
        """step1ab() gets rid of plurals and -ed or -ing. e.g.

           caresses  ->  caress
           ponies    ->  poni
           ties      ->  ti
           caress    ->  caress
           cats      ->  cat

           feed      ->  feed
           agreed    ->  agree
           disabled  ->  disable

           matting   ->  mat
           mating    ->  mate
           meeting   ->  meet
           milling   ->  mill
           messing   ->  mess

           meetings  ->  meet
        """
        if self.b[self.k] == 's':
            if self.ends("sses"):
                self.k = self.k - 2
            elif self.ends("ies"):
                self.setto("i")
            elif self.b[self.k - 1] != 's':
                self.k = self.k - 1
        if self.ends("eed"):
            if self.m() > 0:
                self.k = self.k - 1
        elif (self.ends("ed") or self.ends("ing")) and self.vowelinstem():
            self.k = self.j
            if self.ends("at"):   self.setto("ate")
            elif self.ends("bl"): self.setto("ble")
            elif self.ends("iz"): self.setto("ize")
            elif self.doublec(self.k):
                self.k = self.k - 1
                ch = self.b[self.k]
                if ch == 'l' or ch == 's' or ch == 'z':
                    self.k = self.k + 1
            elif (self.m() == 1 and self.cvc(self.k)):
                self.setto("e")

    def step1c(self):
        """step1c() turns terminal y to i when there is another vowel in the stem."""
        if (self.ends("y") and self.vowelinstem()):
            self.b = self.b[:self.k] + 'i' + self.b[self.k+1:]

    def step2(self):
        """step2() maps double suffices to single ones.
        so -ization ( = -ize plus -ation) maps to -ize etc. note that the
        string before the suffix must give m() > 0.
        """
        if self.b[self.k - 1] == 'a':
            if self.ends("ational"):   self.r("ate")
            elif self.ends("tional"):  self.r("tion")
        elif self.b[self.k - 1] == 'c':
            if self.ends("enci"):      self.r("ence")
            elif self.ends("anci"):    self.r("ance")
        elif self.b[self.k - 1] == 'e':
            if self.ends("izer"):      self.r("ize")
        elif self.b[self.k - 1] == 'l':
            if self.ends("bli"):       self.r("ble") # --DEPARTURE--
            # To match the published algorithm, replace this phrase with
            #   if self.ends("abli"):      self.r("able")
            elif self.ends("alli"):    self.r("al")
            elif self.ends("entli"):   self.r("ent")
            elif self.ends("eli"):     self.r("e")
            elif self.ends("ousli"):   self.r("ous")
        elif self.b[self.k - 1] == 'o':
            if self.ends("ization"):   self.r("ize")
            elif self.ends("ation"):   self.r("ate")
            elif self.ends("ator"):    self.r("ate")
        elif self.b[self.k - 1] == 's':
            if self.ends("alism"):     self.r("al")
            elif self.ends("iveness"): self.r("ive")
            elif self.ends("fulness"): self.r("ful")
            elif self.ends("ousness"): self.r("ous")
        elif self.b[self.k - 1] == 't':
            if self.ends("aliti"):     self.r("al")
            elif self.ends("iviti"):   self.r("ive")
            elif self.ends("biliti"):  self.r("ble")
        elif self.b[self.k - 1] == 'g': # --DEPARTURE--
            if self.ends("logi"):      self.r("log")
        # To match the published algorithm, delete this phrase

    def step3(self):
        """step3() dels with -ic-, -full, -ness etc. similar strategy to step2."""
        if self.b[self.k] == 'e':
            if self.ends("icate"):     self.r("ic")
            elif self.ends("ative"):   self.r("")
            elif self.ends("alize"):   self.r("al")
        elif self.b[self.k] == 'i':
            if self.ends("iciti"):     self.r("ic")
        elif self.b[self.k] == 'l':
            if self.ends("ical"):      self.r("ic")
            elif self.ends("ful"):     self.r("")
        elif self.b[self.k] == 's':
            if self.ends("ness"):      self.r("")

    def step4(self):
        """step4() takes off -ant, -ence etc., in context <c>vcvc<v>."""
        if self.b[self.k - 1] == 'a':
            if self.ends("al"): pass
            else: return
        elif self.b[self.k - 1] == 'c':
            if self.ends("ance"): pass
            elif self.ends("ence"): pass
            else: return
        elif self.b[self.k - 1] == 'e':
            if self.ends("er"): pass
            else: return
        elif self.b[self.k - 1] == 'i':
            if self.ends("ic"): pass
            else: return
        elif self.b[self.k - 1] == 'l':
            if self.ends("able"): pass
            elif self.ends("ible"): pass
            else: return
        elif self.b[self.k - 1] == 'n':
            if self.ends("ant"): pass
            elif self.ends("ement"): pass
            elif self.ends("ment"): pass
            elif self.ends("ent"): pass
            else: return
        elif self.b[self.k - 1] == 'o':
            if self.ends("ion") and (self.b[self.j] == 's' or self.b[self.j] == 't'): pass
            elif self.ends("ou"): pass
            # takes care of -ous
            else: return
        elif self.b[self.k - 1] == 's':
            if self.ends("ism"): pass
            else: return
        elif self.b[self.k - 1] == 't':
            if self.ends("ate"): pass
            elif self.ends("iti"): pass
            else: return
        elif self.b[self.k - 1] == 'u':
            if self.ends("ous"): pass
            else: return
        elif self.b[self.k - 1] == 'v':
            if self.ends("ive"): pass
            else: return
        elif self.b[self.k - 1] == 'z':
            if self.ends("ize"): pass
            else: return
        else:
            return
        if self.m() > 1:
            self.k = self.j

    def step5(self):
        """step5() removes a final -e if m() > 1, and changes -ll to -l if
        m() > 1.
        """
        self.j = self.k
        if self.b[self.k] == 'e':
            a = self.m()
            if a > 1 or (a == 1 and not self.cvc(self.k-1)):
                self.k = self.k - 1
        if self.b[self.k] == 'l' and self.doublec(self.k) and self.m() > 1:
            self.k = self.k -1

    def stem(self, p, i, j):
        """In stem(p,i,j), p is a char pointer, and the string to be stemmed
        is from p[i] to p[j] inclusive. Typically i is zero and j is the
        offset to the last character of a string, (p[j+1] == '\0'). The
        stemmer adjusts the characters p[i] ... p[j] and returns the new
        end-point of the string, k. Stemming never increases word length, so
        i <= k <= j. To turn the stemmer into a module, declare 'stem' as
        extern, and delete the remainder of this file.
        """
        # copy the parameters into statics
        self.b = p
        self.k = j
        self.k0 = i
        if self.k <= self.k0 + 1:
            return self.b # --DEPARTURE--

        # With this line, strings of length 1 or 2 don't go through the
        # stemming process, although no mention is made of this in the
        # published algorithm. Remove the line to match the published
        # algorithm.

        self.step1ab()
        self.step1c()
        self.step2()
        self.step3()
        self.step4()
        self.step5()
        return self.b[self.k0:self.k+1]

#===============================================================================
#Main function
if __name__ == '__main__':

    dictionary = []
    posting = []
    #read dictionary file
    dictionary = cPickle.load(open('dictionary.txt', 'rb'))
    #read posting file
    posting = cPickle.load(open('posting.txt', 'rb'))

    #for p in range(len(dictionary)):
        #print "Dictionary:",dictionary[p]," Posting:", posting[p]
    print "Total Terms: ", len(dictionary)

    term = raw_input("Enter a term: ");
    term = str(term)

    while term != "ZZEND":
        output = ""
        output = term.split()
        print output
        queryterms = []
        #=======================================================================
        #Optional Stemming
        stemming = raw_input("Apply stemming? (y/n): ");
        if stemming == "y":
            p = PorterStemmer()
            output = ''
            word = ''
            for c in term:
                if c.isalpha():
                    word += c.lower()
                    #print "word", word
                else:
                    if word:
                        #print "if word", word
                        output += p.stem(word, 0,len(word)-1)
                        word = ''
                    output += c.lower()
            output += p.stem(word, 0,len(word)-1)
            print "Stemming applied: ", output
            output = output.split();
            print "output split:", output

        #=======================================================================
        #Optional Stopwords Removal
        stopword = raw_input("Remove stopwords? (y/n): ");
        if stopword == "y":
            for index in range(len(output)): #for all the terms user inputed, check if it is a stopword
                stwds = open("common_words","r")
                count = 0 #reset counter, 0 means not a stopword, 1 means is a stopword
                while 1: #for every stopword, check if query term matches a stopword
                    line = stwds.readline().replace('\n', '') #remove the "\n" newline at the end when reading
                    if line == "":
                        stwds.close()
                        break
                    if line == output[index]: #if it is a stopword
                        count =  1
                if count == 0: #if it was not a stopword
                    queryterms.append(output[index]) #put into query terms
            #print "query terms for only stopwords and stemming+no stopwords ", queryterms

        #=======================================================================
        #Query Terms extraction
        #if no stemming and with stopwords
        if (stemming == "n") & (stopword == "n"):
            queryterms = output
            #print "n n", queryterms
        #if only stemming
        if (stemming == "y") & (stopword == "n"):
            queryterms = output
        #if stemming and stopwords removed = by default queryterms already made
        #if only stopwords = by default queryterms already made
        print "Query Terms: ", queryterms

        #=======================================================================
        #find top K = 10, separate into 3 Tiers
        #for each term entered, find term in dictionary
        #tier1 = [] #threshold = 20+ posting          [docIDs for term1]
        Tier1 = [] #final tier1 list              [ [docIDs for term1] , [docIDs for term2 ]
        #tier2 = [] #threshold = 10-19 posting
        Tier2 = [] #final tier2 list
        tier3 = [] #threshold = 1-9
        Tier3 = [] #final tier3 list
        Rank = []
        #find term in dictionary
        found = 0
        #count1 = 0 #counter for tier1 index
        #count2 = 0 #counter for tier2 index
        for i in range(len(queryterms)): #for every query term
            found = 0 #reset
            #tier1 = [] #reset
            #tier2 = [] #reset
            tier3 = [] #reset
            for index in range(len(dictionary)): #for every term in dictionary find query term
                #print "Query term = ", queryterms[i], " Dictionary Term = ", dictionary[index][0]
                if queryterms[i] == dictionary[index][0]: #find the query term in dictionary
                    #print "YES+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                    print "Query Term:", queryterms[i]," Document freqency: ", dictionary[index][1]
                    found = 1
                    #Tiered Index: separate term postings into Tier 1 array with doc#: term freq = 20+, Tier 2 array with doc#: term freq = 10-19
                    spot = dictionary[index][2] #index in posting of that term
                    for x in range(dictionary[index][1]): #for every docID in posting list (the doc freq in dictionary), seperate into tiers
                        #if doc has term freq > 20+ then place into Tier 1
                        #print "posting term freq of doc: ", posting[spot][1][x]
                        if posting[spot][1][x] >= 20:
                            if posting[spot][0][x] not in Tier1: #if docID is not in Tier1 list then add it
                                #tier1.append(posting[spot][0][x]) #append docID
                                Tier1.append(posting[spot][0][x])
                        #if doc has term freq 10-19 then place into Tier 2
                        if (posting[spot][1][x] >= 10) & (posting[spot][1][x] < 20):
                            if posting[spot][0][x] not in Tier2: #if docID is not in Tier2 then add it
                                #tier2.append(posting[spot][0][x]) #append docID
                                Tier2.append(posting[spot][0][x])
                        #if doc has term freq 1-9 then place into tier 3
                        if (posting[spot][1][x] > 0) & (posting[spot][1][x] < 10):
                            if posting[spot][0][x] not in Tier3: #if docID is not in Tier3 then add it to tier3
                                tier3.append(posting[spot][0][x]) #append docID
                                #Tier3.append(posting[spot][0][x])
                    #=============================================================== ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    #keep the top 10 document in tier3 with highest tf*idf weight from dvector to calculate score
                    #create idf vector, idf = log (N / df)
                    idf = []
                    N = len(dictionary)+0.0
                    #print "N =", N
                    #for a in range(len(dictionary)):
                        #print "doc freq", dictionary[index][1]
                    idf.append(round(math.log10(N/dictionary[index][1]),2)) #calculate that one term's idf
                    #print "idf:", idf
                    #-----------------------------------------------------------
                    #find the top 10 highest weight in dvector
                    temp = [] #store the top 10 highest weight tf*idf
                    #match = 0
                    dvector = []
                    for o in range(len(tier3)): #for every docID in tier3
                        tf = []
                        #dvector = []
                        #create tf vector
                        #for y in range(len(dictionary)):
                        for a in range(len(posting[spot][1])): #for every docID in posting of every term
                            if posting[spot][0][a] == tier3[o]:  #if posting docID matches tier3 docID, then calculate the tf
                                    #match = 1
                                    #print "posting ", posting[y][1][a]
                                    #print "Tf append =", round(math.log10(posting[y][1][a]),2) + 1
                                tf.append(round(math.log10(posting[spot][1][a]),2) + 1) #tf = log (term freq) + 1
                                    #break?
                            #if match == 0: #if is no match then record as 0 for term freq
                                #tf.append(0)
                            #match = 0 #reset
                        #print "tf ", tf
                        #print "len tf=",len(tf)
                        #print "len idf=", len(idf)

                        #---------------------------------------------------------------
                        #create document vector tf*idf
                        #for d in range(len(tf)):
                            #print "tf =", tf[d], " idf", idf[d]
                            #print "dvector append=", round(tf[d]*idf[d],2)
                        dvector.append(round(tf[0]*idf[0],2)) #calculate only that term's tf*idf weight
                    #print dvector
                    #print len(tier3)
                    #print len(dvector)

                    #---------------------------------------------------------------
                    #find highest weight
                    temp = [] #reset
                    for e in range(len(dvector)):
                        highest = 0 #reset
                        pos = 0 #reset
                        if len(temp) == 10: #if temp has top 10 highest weight then stop
                            break
                        for m in range(len(dvector)):
                            if dvector[m] > highest:
                                highest = dvector[m]
                                pos = m
                        #print "highest:", dvector[pos]
                        temp.append(tier3[pos]) #store the docID
                        dvector[pos] = 0 #change highest score in scores to 0 so we dont use it again
                    #print "temp:", temp
                    #store the top 10 highest weight docID into final Tier3 list
                    for k in range(len(temp)):
                        Tier3.append(temp[k])

            if found == 0:
                print "Query Term:", queryterms[i], " not found!"
            #place tier1 into final Tier1 list
            #Tier1.append(tier1)
            print "Tier 1: ", Tier1
            #place tier2 into final Tier2 list
            #Tier2.append(tier2)
            print "Tier 2: ", Tier2
            #place tier3 into final Tier3 list
            #Tier3.append(tier3)
            print "Tier 3: ", Tier3, "\n"

        #=======================================================================
        #Ranking Documents, create vectors, calculate similarity scores
        tf = []
        idf = []
        dvector = [] #document vector
        qvector = [] #query vector
        ndvector = 0 #normalized document vector
        nqvector = 0 #normalized query vector
        dotproduct = 0
        scores = []
        match = 0
        N = 0

        #-----------------------------------------------------------------------
        #create idf vector, idf = log (N / df)
        N = len(dictionary)+0.0
        #print "N =", N
        for index in range(len(dictionary)):
            #print "doc freq", dictionary[index][1]
            idf.append(round(math.log10(N/dictionary[index][1]),2))
        #print "idf:", idf

        #-----------------------------------------------------------------------
        #create query vector and noramlized vector
        for index in range(len(dictionary)): #for every term in the dictionary
            if dictionary[index][0] in queryterms: #if dictionary term is one of the query term
                print "dictionary term: ", dictionary[index][0], " Query term:", queryterms
                #store the term freq in queryterm in the tf vector
                print "count of term in queryterms: ", queryterms.count(dictionary[index][0]), "\n"
                tf.append(round(math.log10(queryterms.count(dictionary[index][0])) + 1, 2)) #tf = log (term freq) + 1 ++++++++++++++++++++++
                #print tf
            else:
                #not in query term then add a 0 in tf vector
                tf.append(0)
        #print "query tf = ", tf
        #print "len tf=",len(tf)
        #print "len idf=", len(idf)
        #-----------------------------------------------------------------------
        #create query vector
        for d in range(len(tf)):
            #print "query tf =", tf[d], " idf", idf[d]
            #print "qvector append=", round(tf[d]*idf[d],2)
            qvector.append(round(tf[d]*idf[d],2))
        #print "qvector ", qvector
        #-----------------------------------------------------------------------
        #create normalized query vector
        #print "len qvector= ", len(qvector)
        for b in range(len(qvector)):
            nqvector = nqvector + qvector[b]*qvector[b]  #adding the square of each term freq
        #print "nqvector before sqrt=", nqvector
        nqvector = round(math.sqrt(nqvector),2)
        #print "nqvector=", nqvector

        #-----------------------------------------------------------------------
        #create document vector, normalized vector and calculate similarity score for every docID in Tier1
        if len(Tier1) != 0: #if Tier1 is not empty
            print "Tier1 len =", len(Tier1)
            for index in range(len(Tier1)): #for every docID in Tier1
                tf = [] #reset
                dvector = [] #reset
                ndvector = 0 #reset
                dotproduct = 0
                #create tf vector
                for y in range(len(dictionary)): #for every term in dictionary, find docID and record the term freq
                    for a in range(len(posting[y][1])): #for every docID in posting of every term
                        if posting[y][0][a] == Tier1[index]:  #if posting docID matches Tier1 docID, then calculate the tf
                            match = 1
                            #print "posting ", posting[y][1][a]
                            #print "Tf append =", round(math.log10(posting[y][1][a]),2) + 1
                            tf.append(round(math.log10(posting[y][1][a]),2) + 1) #tf = log (term freq) + 1
                            #break?
                    if match == 0: #if is no match then record as 0 for term freq
                        tf.append(0)
                    match = 0 #reset
                #print "tf ", tf
                #print "len tf=",len(tf)
                #print "len idf=", len(idf)
                #---------------------------------------------------------------
                #create document vector tf*idf
                for d in range(len(tf)):
                    #print "tf =", tf[d], " idf", idf[d]
                    #print "dvector append=", round(tf[d]*idf[d],2)
                    dvector.append(round(tf[d]*idf[d],2))
                #print "dvector ", dvector
                #---------------------------------------------------------------
                #calculate the normalized document vector
                #print "len dvector= ", len(dvector)
                for b in range(len(dvector)):
                    ndvector = ndvector + dvector[b]*dvector[b]  #adding the square of each term freq
                #print "ndvector before sqrt=", ndvector
                ndvector = round(math.sqrt(ndvector),2)
                #print "ndvector=", ndvector
                #---------------------------------------------------------------
                #calculate the dot product of d . q
                for c in range(len(qvector)):
                    dotproduct = dotproduct + qvector[c]*dvector[c] + 0.0
                #---------------------------------------------------------------
                #calculate the similarity score (d,q) = d . q / |d| . |q|
                scores.append(round(dotproduct/(ndvector*nqvector),2))
            print "Tier1 scores", scores
            #-------------------------------------------------------------------
            #Rank documents in Tier1
            highest = 0
            pos = 0
            if len(scores) >= 10: #if more than 10 scores
                for e in range(1,11): #choose top 10 highest scores #(1, 10) = 1, ... , 9 and not 1, ... , 10
                    highest = 0 #reset
                    pos = 0 #reset
                    for index in range(len(scores)): #for every scores
                        if scores[index] > highest:
                            highest = scores[index]
                            pos = index
                    Rank.append([Tier1[pos],highest]) #store the docID with score
                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
            else: #if less than 10 result
                for e in range(len(scores)):
                    highest = 0 #reset
                    pos = 0 #reset
                    for index in range(len(scores)):
                        if scores[index] > highest:
                            highest = scores[index]
                            pos = index
                    Rank.append([Tier1[pos],highest]) #store the docID with score into final ranking
                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
            print "Rank with only Tier1:", Rank, "\n"

        #=======================================================================
        scores = [] #reset
        match = 0 #reset
        #if less than K=10 rank documents then use Tier2
        if len(Rank) < 10:
            #create document vector, normalized vector and calculate similarity score for every docID in Tier2
            if len(Tier2) != 0: #if Tier2 is not empty
                print "Tier2 len =", len(Tier2)
                for index in range(len(Tier2)): #for every docID in Tier2
                    tf = [] #reset
                    dvector = [] #reset
                    ndvector = 0 #reset
                    dotproduct = 0
                    #create tf vector
                    for y in range(len(dictionary)): #for every term in dictionary, find docID and record the term freq
                        for a in range(len(posting[y][1])): #for every docID in posting of every term
                            if posting[y][0][a] == Tier2[index]:  #if posting docID matches Tier2 docID, then calculate the tf
                                match = 1
                                #print "posting ", posting[y][1][a]
                                #print "Tf append =", round(math.log10(posting[y][1][a]),2) + 1
                                tf.append(round(math.log10(posting[y][1][a]),2) + 1) #tf = log (term freq) + 1 ++++++++++++++++++++++++++++++++fixed?
                                #break?
                        if match == 0: #if is no match then record as 0 for term freq
                            tf.append(0)
                        match = 0 #reset
                    #print "tf ", tf
                    #print "len tf=",len(tf)
                    #print "len idf=", len(idf)
                    #---------------------------------------------------------------
                    #create document vector tf*idf
                    for d in range(len(tf)):
                        #print "tf =", tf[d], " idf", idf[d]
                        #print "dvector append=", round(tf[d]*idf[d],2)
                        dvector.append(round(tf[d]*idf[d],2))
                    #print "dvector ", dvector
                    #---------------------------------------------------------------
                    #calculate the normalized document vector
                    #print "len dvector= ", len(dvector)
                    for b in range(len(dvector)):
                        ndvector = ndvector + dvector[b]*dvector[b]  #adding the square of each term freq
                    #print "ndvector before sqrt=", ndvector
                    ndvector = round(math.sqrt(ndvector),2)
                    #print "ndvector=", ndvector
                    #---------------------------------------------------------------
                    #calculate the dot product of d . q
                    for c in range(len(qvector)):
                        dotproduct = dotproduct + qvector[c]*dvector[c] + 0.0
                    #---------------------------------------------------------------
                    #calculate the similarity score (d,q) = d . q / |d| . |q|
                    scores.append(round(dotproduct/(ndvector*nqvector),2))
                print "Tier2 scores", scores
                #-------------------------------------------------------------------
                #Rank documents in Tier2
                highest = 0
                pos = 0
    ##            if len(scores) >= 10: #if more than 10 scores
    ##                for e in range(1, 11): #choose top 10 highest scores #(1, 10) = 1, ... , 9 and not 1, ... , 10
    ##                    highest = 0 #reset
    ##                    pos = 0 #reset
    ##                    for index in range(len(scores)): #for every scores
    ##                        if scores[index] > highest:
    ##                            highest = scores[index]
    ##                            pos = index
    ##                    Rank.append([Tier2[pos],highest]) #store the docID with score
    ##                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
    ##            else: #if less than 10 result
                for e in range(len(scores)):
                    highest = 0 #reset
                    pos = 0 #reset
                    if len(Rank) == 10: #if Rank has top 10 documents then stop
                        break
                    for index in range(len(scores)):
                        if scores[index] > highest:
                            highest = scores[index]
                            pos = index
                    Rank.append([Tier2[pos],highest]) #store the docID with score into final ranking
                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
                print "Rank with Tier1 and Tier2:", Rank, "\n"

        #=======================================================================
        scores = [] #reset
        match = 0 #reset
        #if less than K=10 rank documents then use Tier3
        if len(Rank) < 10:
            #create document vector, normalized vector and calculate similarity score for every docID in Tier3
            if len(Tier3) != 0: #if Tier3 is not empty
                print "Tier3 len =", len(Tier3)
                for index in range(len(Tier3)): #for every docID in Tier3
                    tf = [] #reset
                    dvector = [] #reset
                    ndvector = 0 #reset
                    dotproduct = 0
                    #create tf vector
                    for y in range(len(dictionary)): #for every term in dictionary, find docID and record the term freq
                        for a in range(len(posting[y][1])): #for every docID in posting of every term
                            if posting[y][0][a] == Tier3[index]:  #if posting docID matches Tier3 docID, then calculate the tf
                                match = 1
                                #print "posting ", posting[y][1][a]
                                #print "Tf append =", round(math.log10(posting[y][1][a]),2) + 1
                                tf.append(round(math.log10(posting[y][1][a]),2) + 1) #tf = log (term freq) + 1 ++++++++++++++++++++++++++++++++fixed?
                                #break?
                        if match == 0: #if is no match then record as 0 for term freq
                            tf.append(0)
                        match = 0 #reset
                    #print "tf ", tf
                    #print "len tf=",len(tf)
                    #print "len idf=", len(idf)
                    #---------------------------------------------------------------
                    #create document vector tf*idf
                    for d in range(len(tf)):
                        #print "tf =", tf[d], " idf", idf[d]
                        #print "dvector append=", round(tf[d]*idf[d],2)
                        dvector.append(round(tf[d]*idf[d],2))
                    #print "dvector ", dvector
                    #---------------------------------------------------------------
                    #calculate the normalized document vector
                    #print "len dvector= ", len(dvector)
                    for b in range(len(dvector)):
                        ndvector = ndvector + dvector[b]*dvector[b]  #adding the square of each term freq
                    #print "ndvector before sqrt=", ndvector
                    ndvector = round(math.sqrt(ndvector),2)
                    #print "ndvector=", ndvector
                    #---------------------------------------------------------------
                    #calculate the dot product of d . q
                    for c in range(len(qvector)):
                        dotproduct = dotproduct + qvector[c]*dvector[c] + 0.0
                    #---------------------------------------------------------------
                    #calculate the similarity score (d,q) = d . q / |d| . |q|
                    scores.append(round(dotproduct/(ndvector*nqvector),2))
                print "Tier3 scores", scores
                #-------------------------------------------------------------------
                #Rank documents in Tier3
                highest = 0
                pos = 0
    ##            if len(scores) >= 10: #if more than 10 scores
    ##                for e in range(1, 11): #choose top 10 highest scores #(1, 10) = 1, ... , 9 and not 1, ... , 10
    ##                    highest = 0 #reset
    ##                    pos = 0 #reset
    ##                    for index in range(len(scores)): #for every scores
    ##                        if scores[index] > highest:
    ##                            highest = scores[index]
    ##                            pos = index
    ##                    Rank.append([Tier2[pos],highest]) #store the docID with score
    ##                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
    ##            else: #if less than 10 result
                for e in range(len(scores)):
                    highest = 0 #reset
                    pos = 0 #reset
                    if len(Rank) == 10: #if Rank has top 10 documents then stop
                        break
                    for index in range(len(scores)):
                        if scores[index] > highest:
                            highest = scores[index]
                            pos = index
                    Rank.append([Tier3[pos],highest]) #store the docID with score into final ranking
                    scores[pos] = 0 #change highest score in scores to 0 so we dont use it again
                print "Rank with Tier1, Tier2 and Tier3:", Rank, "\n"
        #=======================================================================
        #Sort Rank by highest scores
        print "Before Rank sort:", Rank
        Rank = sorted(Rank, key=lambda x: x[1], reverse=True) #sort highest to lowest
        print "After sort:", Rank
        #=======================================================================
        #print relevant documents and their scores and ranking order
        #For each result, the ranking order (e.g. 1, 2, 3), the document title and the author names should be displayed.
        for index in range(len(Rank)): #for every rank documents
            print "============================================================="
            print "Rank:", index+1, "  Document ID:", Rank[index][0], "  Relevance Score:", Rank[index][1]
            infile = open("cacm.all","r")
            line = infile.readline()
            find = 0
            string = ".I " + str(Rank[index][0]) #".I number"
            while find == 0:
                if string in line: #found id number
                    #if first == 0: #for the first time/in the beginning
                    line = infile.readline() #next line after ".I number"
                        #first = 1
                    while 1:
                        if (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()): #skip lines
                            while 1:
                                if (".I" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (line == ''): #find the title tag or the author tag
                                    break
                                else:
                                    line = infile.readline() #next line

                        if (".I" in line.split()) | (line == ''): #if found id tag, that mean it is the next document so stop or End of File
                            find = 1
                            #print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
                            break

                        if ".T" in line.split(): #found title tag
                            print "Title: "
                            while 1:
                                line = infile.readline() #skip the tag and reads line after it
                                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                                    break
                                print line

                        if ".A" in line.split(): #found author tag
                            print "Authors: "
                            while 1:
                                line = infile.readline() #skip the tag and read line after it
                                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                                    break
                                print line
                if line == '':
                    print "Note: End of Collection!"
                    break
                line = infile.readline() #go to next line to find the id number

            infile.close()

        term = raw_input("Enter a term(s): ");
        term = str(term)






