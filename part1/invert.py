#!/usr/bin/env python
import string
import cPickle
from operator import itemgetter

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
    #create a edited version of cacm.all with only .I, .T and .W and save to file named edited.txt
    print"Creating edited version of cacm.all ..."
    out = open("edited.txt", "a")
    infile = open("cacm.all","r")
    line = infile.readline()
    while 1:
        if (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".A" in line.split())| (".K" in line.split()) | (".C" in line.split()):
            while 1:
                if (".I" in line.split()) | (".T" in line.split()) | (".W" in line.split()) | (line == ''):
                    break
                else:
                    line = infile.readline() #skip line
        if line == '':
            break

        if ".I" in line.split(): #if found id
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    out.write(line) #write line to file
                    line = infile.readline() #next line

        if ".T" in line.split(): #if found title
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    out.write(line) #write line to file
                    line = infile.readline() #next line

        if ".W" in line.split(): #if found abstract
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    out.write(line) #write line to file
                    line = infile.readline() #next line
    infile.close()
    out.close()
    print "Edited version of cacm.all completed"

    #from edited.txt, remove all ,./;'\[]`<>?:"|{}~!@#$%^&*()_+ and save to file named clean.txt
    print "Removing punctuations ..."
    out = open("clean.txt", "a")
    infile = open("edited.txt","r")
    line = infile.readline()
    while 1:
        edited = ""
        if (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".A" in line.split())| (".K" in line.split()) | (".C" in line.split()):
            while 1:
                if (".I" in line.split()) | (".T" in line.split()) | (".W" in line.split()) | (line == ''):
                    break
                else:
                    line = infile.readline() #skip line
        if line == '':
            break

        if ".I" in line.split(): #if found id
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    out.write(line) #write line to file
                    line = infile.readline() #next line

        if ".T" in line.split(): #if found title
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    edited = line.translate(None,string.punctuation) #remove punctuation from line
                    out.write(edited) #write edited line to file
                    line = infile.readline() #next line
                    edited = ""

        if ".W" in line.split(): #if found abstract
            out.write(line) #write the tag
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    edited = line.translate(None,string.punctuation) #remove punctuation from line
                    out.write(edited) #write edited line to file
                    line = infile.readline() #next line
                    edited = ""
    infile.close()
    out.close()
    print "Removed punctuations complete"

    #===========================================================================
    #Optional 1
    stemming = raw_input("Apply stemming? (y/n): ");
    if stemming == "y":
        p = PorterStemmer()
        out = open("output.txt","a")
        #if len(sys.argv) > 1:
            #for f in sys.argv[1:]:
                #infile = open(f, 'r')

        print "Stemming ..."
        infile = open("clean.txt","r") #change to clean.txt  #testing.txt #change to cacm.all file ++++++++++++++++++++++++++++++++++++++++
        line = infile.readline() #new
        while 1:
            output = ''
            word = ''
            #if (".I" not in line) & (".B" not in line) & (".N" not in line) & (".X" not in line) & (".T" not in line) & (".A" not in line) & (".W" not in line):
                #line = infile.readline()

            if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".A" in line.split()) | (".K" in line.split()) | (".C" in line.split()):
                while 1:
                    output = ''
                    if (".T" in line.split()) | (".W" in line.split()) | (line == ''):
                        break
                    else:
                        out.write(line)
                        line = infile.readline()

            if line == '':
                print "Stemming complete"
                break
            if ".T" in line.split(): #if found title, stem the words
                out.write(line)
                while 1:
                    output = ''
                    word = ''
                    line = infile.readline()
                    if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                        break
            #indented
                    for c in line:
                        if c.isalpha():
                            word += c.lower()
                        else:
                            if word:
                                output += p.stem(word, 0,len(word)-1)
                                word = ''
                            output += c.lower()
                    #print output,
                    out.write(output)

            if ".W" in line.split(): #if found abstract, stem the words
                out.write(line)
                while 1:
                    output = ''
                    word = ''
                    line = infile.readline()
                    if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split())| (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                        break

                    for c in line:
                        if c.isalpha():
                            word += c.lower()
                        else:
                            if word:
                                output += p.stem(word, 0,len(word)-1)
                                word = ''
                            output += c.lower()
                    #print output, #comma after output means print on the same line
                    out.write(output)

        out.close()
        infile.close()

    """
    #==========================================================================
    #Option 2
    stopword = raw_input("Remove stopwords? (y/n): ");
    if stopword == "y":
        if stemming == "y":
            edit = open("output.txt", "r")
        else: #not stemed
            edit = open("clean.txt", "r") #change to clean.txt #testing.txt #change to cacm.all file  ++++++++++++++++++++++++++++++++++++++++
        temp = open("temp.txt", "a")
        line = ''
        line = edit.readline()
        print "Removing stopwords ..."

        while 1:
            #if (".I" not in line) & (".B" not in line) & (".N" not in line) & (".X" not in line) & (".T" not in line) & (".A" not in line) & (".W" not in line):
                    #line = edit.readline()

            if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".A" in line.split())| (".K" in line.split()) | (".C" in line.split()):
                while 1:
                    if (".T" in line.split()) | (".W" in line.split()) | (line == ''):
                        break
                    else:
                        temp.write(line)
                        line = edit.readline()

            if line == '':
                print "Stopwords removal complete"
                break

            if ".T" in line.split(): #if found title, remove stopwords
                temp.write(line)
                #stwds = open("stopwords.txt","r")
                while 1:
                    stwds = open("common_words","r") #stopwords.txt #or common_words ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    line = edit.readline()
                    if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split())| (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                        #stwds.close()
                        break
                    while 1:
                        sword = stwds.readline().replace('\n', '') #check word with every stopword #replace newline character with a space so that the word is followed by a space
                        if sword == '':
                            if "\n" not in line:
                                line = line+"\n"
                            temp.write(line)
                            stwds.close()
                            break
                        if sword in line.split():
                            #print sword
                            line = line.split()
                            #print line
                            line = filter(lambda x: x != sword, line)
                            #print line
                            line = " ".join(line)
                            #print line
                        #line = line.replace(sword, "") #does not remove "the" if the word is "The" in collection, only work if you stem which change "The" to "the"

            if ".W" in line.split(): #if found abstract, remove stopwords
                temp.write(line)
                #stwds = open("stopwords.txt","r")
                while 1:
                    stwds = open("common_words","r") #stopwords.txt #or common_words +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                    line = edit.readline()
                    if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split())| (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                        #stwds.close()
                        break
                    while 1:
                        sword = stwds.readline().replace('\n', '') #check word with every stopword
                        if sword == '':
                            if "\n" not in line:
                                line = line+"\n"
                            temp.write(line)
                            stwds.close()
                            break
                        if sword in line.split():
                            #print sword
                            line = line.split()
                            #print line
                            #for w in range(len(line)):
    	                       #if line[w] == sword:
    		                      #line.remove(sword)
                            #line.remove(sword)
                            line = filter(lambda x: x != sword, line)
                            #print line
                            line = " ".join(line)
                            #line = line.replace(sword, "") #remove!
                            #print line
        edit.close()
        temp.close()
    """

    #========================================================================
    #Gathering terms from title and abstract and store terms with id
    #if yes/no stopword or stemming or both
    #if (stemming == "y") & (stopword == "y"):
      #  infile = open("temp.txt","r")
    #elif (stemming == "y") & (stopword == "n"):
     #   infile = open("output.txt","r")
    #elif (stemming == "n") & (stopword == "y"):
     #   infile = open("temp.txt")
    #else: #not stemed & stopwords not removed
     #   infile = open("clean.txt","r") #changed to clean.txt #testing.txt #change to cacm.all file ++++++++++++++++++++++++++++++++++++++

    #if yes stemming
    if stemming == "y":
        infile = open("output.txt","r")
    else:
        infile = open("clean.txt","r")

    print "Gathering terms ..."
    #out = open("temp2.txt","a")
    counter = 0 #word position counter
    dict1 = []
    dict2 = []
    line = infile.readline()
    while 1:
        if (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".A" in line.split())| (".K" in line.split()) | (".C" in line.split()):
            while 1:
                if (".I" in line.split()) | (".T" in line.split()) | (".W" in line.split()) | (line == ''):
                    break
                else:
                    line = infile.readline() #go to next line
        if line == '':
            break

        if ".I" in line.split(): #if found id
            counter = 0 #reset counter
            id = 0
            idline = line.split()
            id = idline[1] #list starts at [0], id number is in [1]
            line = infile.readline()
            while 1:
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split()) | (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                else:
                    line = infile.readline()

        if ".T" in line.split(): #if found title
            while 1:
                line = infile.readline() #goes to the next line after ".T" tag line
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split())| (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                line = line.split()
                for index in range(len(line)):
                    counter = counter+1 #increase counter
                    dict1 = []
                    data = "".join(line[index])
                    dict1.append(data)
                    dict1.append(id)
                    dict1.append(counter) #save term position
                    dict2.append(dict1) #save dict1[term, id, pos] in dict2[] => dict2 [ [term,id,pos], [...], ...]
                    #data = data+" "+id+"\n" #term followed by id and a newline
                    #out.write(data)

        if ".W" in line.split(): #if found abstract
            while 1:
                line = infile.readline() #goes to next line after ".W" tag line
                if (".I" in line.split()) | (".B" in line.split()) | (".N" in line.split()) | (".X" in line.split()) | (".T" in line.split()) | (".A" in line.split()) | (".W" in line.split())| (".K" in line.split()) | (".C" in line.split()) | (line == ''):
                    break
                line = line.split()
                for index in range(len(line)):
                    counter = counter+1 #increase counter
                    dict1 = []
                    data = "".join(line[index])
                    dict1.append(data)
                    dict1.append(id)
                    dict1.append(counter) #save term position
                    dict2.append(dict1)
                    #data = data+" "+id+"\n" #term followed by id and a newline
                    #out.write(data)
    #out.close()
    infile.close()

    print "Gathering terms complete"
    #sort dict2 alphabetically
    #print dict2
    #dict2.sort(key=lambda x:x[0]) #captialized words will be at the front from A to Z then lower case after from A to Z
    #dict2 = sorted(dict2, key=lambda x: (x[0].upper(), x[0].islower())) #sort with capitalized words
    #print "\n"
    #print dict2
    #from operator import itemgetter
    #dict2.sort(key=itemgetter(0))    #for large lists

    print "Sorting dict2 ..."
    dict2 = sorted(dict2, key=lambda k: (k[0].lower()))
    #for index in range(len(dict2)):
        #print dict2[index]

    print "Sorting complete"

    #===========================================================================
    #Option 2
    #remove stopwords
    #read stopword file
    stopword = raw_input("Remove stopwords? (y/n): ");
    if stopword == "y":
        print "Removing stopwords ..."
        #for each word in stopword file, go through dict2
        stwds = open("common_words","r") #stopwords.txt #or common_words ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #dict3 =[]
        while 1: #for every stopword, go through dict2
            line = stwds.readline().replace('\n', '') #remove the "\n" newline at the end when reading
            if line == "":
                break
            #for index in range(len(dict2)): #for every word in dict2, find the stopword
             #   if line not in dict2[index]: #if term is not a stopword, add to dict3
              #      dict3.append(dict2[index])
            #dict2 = []
           # dict2 = dict3 #switch back the removed stopword list

            for index in range(len(dict2)):
                #print line, dict2[index]
                #print line in dict2[index]
                #print line == dict2[index][0]
                #if line == dict2[index][0]
                if line in dict2[index]:
                    dict2[index] = [] #mark the stopword spot to a [] blank
        dict2 = [item for item in dict2 if item != []] #remove all [] blanks from dict2
        print "Remove stopwords complete"
        #for index in range(len(dict2)):
            #print dict2[index]

    #===========================================================================
     #Create Dictionary and Postings
    print "Creating Dictionary and Posting ..."
    dout = open("dictionary.txt", "a")
    pout = open("posting.txt","a")
    dict = [] #term, doc freq, link to posting
    dictionary = [] #add dict to dictionary
    post = [] #doc number, term freq, term positions      [ [doc#], [term freq], [ [pos doc1],[pos doc2] ] ]
    posting = [] #add post to posting
    link = 0 #counter for index to posting array
    length = len(dict2)-1
    for index in range(length): #len(dict2)): #for every term in dict2
        #print "Progress:", index, "/", length
        dict = []
        post = []
        #if dictionary is empty, add a term in
        if len(dictionary) == 0:
            #print "EMPTY"
            #print dict2[index][0]
            dict.append(dict2[index][0]) #term
            dict.append(1) #found it in 1 doc in the beginning, will increase later below if more found
            dict.append(link) #index(link) to posting array
            link = link+1 #counter for index to posting array
            dictionary.append(dict) #add to dictionary
            #print dictionary
            #print len(dictionary)
            post.append([dict2[index][1]]) #doc id
            post.append([1]) #term freq in doc in the beginning, will increase later below if more found
            post.append([[dict2[index][2]]]) #post.append([[-1]]) #unknown position yet, place holder +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            posting.append(post)
            #print posting
        else:
        ##if term is not in dictionary, add term and add posting
            #if term is in dictionary
            inside = 0
            for d in range(len(dictionary)):
                if dict2[index][0] == dictionary[d][0]: #comput == computer = False!
                #if dict2[index][0] in dictionary[d][0]: #"comput in computer = True!
                    inside = 1
                    dict = []
                    post = []
                    #for x in range(len(dictionary)):
                        #if dict2[x][0] == dictionary[x][0]: #term == term
                            #idx = dictionary[x][2] #link to posting
                    idx = dictionary[d][2]
                    #if doc number is not in doc ID, add it
                    if dict2[index][1] not in posting[idx][0]:
                        posting[idx][0].append(dict2[index][1])
                        #add term freq, position
                        posting[idx][1].append(1)
                        posting[idx][2].append([dict2[index][2]]) #posting[idx][2].append([-1]) #default position +++++++++++++++++++++++++++++++++
                        #increase doc freq for dictionary
                        #dictionary[x][1] = dictionary[x][1]+1
                        dictionary[d][1] = dictionary[d][1]+1
                    #else find doc number in doc id, increase to term freq
                    else:
                        for i in range(len(posting[idx][0])):
                            if dict2[index][1] == posting[idx][0][i]:
                                posting[idx][1][i] = posting[idx][1][i]+1 #increase term freq
                                posting[idx][2][i].append(dict2[index][2]) #add term position ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


##                if dict2[index][0] not in dictionary[d][0]: #dict2[Term][ID]  dictionary[[Term,..,..],[...],...]
##                    dict.append(dict2[index][0]) #term
##                    dict.append(1) #found it in 1 doc in the beginning, will increase later below if more found
##                    dict.append(link) #index(link) to posting array
##                    link = link+1 #counter for index to posting array
##                    dictionary.append(dict) #add to dictionary
##                    print dictionary
##                    post.append([dict2[index][1]]) #doc id
##                    post.append([1]) #term freq in doc in the beginning, will increase later below if more found
##                    post.append([[-1]]) #unknown position yet, place holder +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##                    posting.append(post)
##                    dict = []
##                    post = []


            #if term is not in dictionary, add term and add posting
            if inside == 0:
                dict = []
                post = []
                dict.append(dict2[index][0]) #term
                dict.append(1) #doc freq, found it in 1 doc in the beginning, will increase later below if more found
                dict.append(link) #index(link) to posting array
                link = link+1 #counter for index to posting array
                dictionary.append(dict) #add to dictionary
                #print dictionary
                post.append([dict2[index][1]]) #doc id
                post.append([1]) #term freq in doc in the beginning, will increase later below if more found
                post.append([[dict2[index][2]]]) #post.append([[-1]]) #unknown position yet, place holder +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
                posting.append(post)


##                else: #if term is in dictionary
##                    dict = []
##                    post = []
##                    #for x in range(len(dictionary)):
##                        #if dict2[x][0] == dictionary[x][0]: #term == term
##                            #idx = dictionary[x][2] #link to posting
##                            idx = dictionary[d][2]
##                            #if doc number is not in doc ID, add it
##                            if dict2[index][1] not in posting[idx][0]:
##                                posting[idx][0].append(dict2[index][1])
##                                #add term freq, position
##                                posting[idx][1].append(1)
##                                #increase doc freq for dictionary
##                                #dictionary[x][1] = dictionary[x][1]+1
##                                dictionary[d][1] = dictionary[d][1]+1
##                            #else find doc number in doc id, increase to term freq
##                            else:
##                                for i in range(len(posting[idx][0])):
##                                    if dict2[index][1] == posting[idx][0][i]:
##                                        posting[idx][1][i] = posting[idx][1][i]+1


    #print "\n"
    #print dictionary
    #print "\n"
    #print posting
    #for p in range(len(dictionary)):
        #print "Dictionary:",dictionary[p]," Posting:", posting[p]
    print "Dictionary and Posting created"
    print "Total Terms:", len(dictionary)

    #write dictionary to file
    print "Writing to file ..."
    cPickle.dump(dictionary, open("dictionary.txt", "wb"))
    #write posting to file
    cPickle.dump(posting, open("posting.txt", "wb"))

    dout.close()
    pout.close()
    print "Writing complete"


