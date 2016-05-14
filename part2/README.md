#Instructions

**Language:** Python

**Version:** 2.7

Please make sure Python version 2.7 is installed

--------------------------------------------------------------------------------------------
**Files Required:**

Please make sure you have the following files

1. cacm.all
2. clean.txt       (empty/blank file)
3. common_words
4. dictionary.txt  (empty/blank file)
5. edited.txt      (empty/blank file)
6. eval.py
7. invert.py
8. output.txt      (empty/blank file)
9. posting.txt     (empty/blank file)
10. qrels.text
11. query.text
12. README.txt
13. search.py

**Note:** All these files should be in the same folder/directory

--------------------------------------------------------------------------------------------
**General How to Run a Python Program:**

**Way 1**. Open .py file in Python 2.7.6 IDLE, 
       click Run from top menu 
       and click Run Module or just press F5

**Way 2.** Open .py file in Python PyScripter, 
       click green arrow in the toolbar at the top 
       or just press CTRL+F9
       
--------------------------------------------------------------------------------------------

#Design & Details

###invert.py###

**Details:** 

- Python version of Porter’s stemming algorithm created by Vivake Gupta was used.
- common_words file was used for the stop words removal process.
- Posting list is ordered by document ID.
- Stemming optional.
- Stopwords removal optional.

**Files required to run invert.py:**

1. cacm.all
2. clean.txt 
3. common_words
4. dictionary.txt
5. edited.txt
6. output.txt
7. posting.txt

Please make sure that files 2,4,5,6,7 are EMPTY before you run!

Please run this program FIRST at least ONCE before running the other programs!

**Note:**

- If you want to rerun invert.py, you have to DELETE the content in files 2,4,5,6,7 manually so that it becomes EMPTY to run again!
- Run time can go from  2 to 10 mins depending on stemming and stopwords removal option.

--------------------------------------------------------------------------------------------
###search.py###

**Details:**

- The interface program is integrated into search.py.
- Stemming optional.
- Stopwords removal optional.
- Top K retreival is used. K is 10.
- Champion List is used in Tier 3.
- Tiered Index is used. 
  - Tier 1 threshold is 20+ (term frequency value).
  - Tier 2 threshold is 10 to 19 (term frequency value).
  - Tier 3 threshold is 1 to 9 (term frequency value).

**Formulas:**

Here are the forumlas used:
- idf = log(N/df) 
- tf = log(frequency) + 1
- query vector = tf * idf
- normalized query vector = squareroot(query vector ^2)
- document vector = tf * idf
- normalized document vector = squareroot(document vector ^2)
- similarity score = (d . q) / ( |d| . |q| )

**Files required to run search.py:**

1. cacm.all
2. dictionary.txt 
3. posting.txt

Before you run search.py, please run invert.py first if you have not run it ONCE!

This is so that the dictionary.txt and posting.txt is created!

**Note:**

- Do not input query with punctuations! 
- Punctuation removal is not implemented!

--------------------------------------------------------------------------------------------
###eval.py###

**Details:**

- Stemming optional.
- Stopwords removal optional.
- Top K retreival is used. K is 10 for each query term.
- Documents retrieved is dynamically changed to match total number of relevant documents to calculate R-Precision. In other words, K is changed at the end to match |R| for each query.
- Champion List is used in Tier 3.
- Tiered Index is used. 
  - Tier 1 threshold is 20+ (term frequency value).
  - Tier 2 threshold is 10 to 19 (term frequency value).
  - Tier 3 threshold is 1 to 9 (term frequency value).

**Formulas:**

Here are the formulas used:
- MAP = sum of precision values of all relevant documents retrieved / total relevant documents 
- R-Precision = r / |R|
- Average MAP = sum of MAP values / total number of MAP values
- Average R-Precision = sum of R-Precision values / total number of R-Precision values

**Files required to run eval.py:**

1. dictionary.txt
2. posting.txt
3. qrels.text
4. query.text

Before you run eval.py, please run invert.py first if you have not run it ONCE! 

This is so that the dictionary.txt and posting.txt is created!

**Note:**
- Default setting: stemming is applied.
- Default setting: stopwords removal is applied.
- Manually change default setting in source code to match the setting you chose in invert.py.
- Change in line 415 for stemming = "y" or "n"
- Change in line 468 for remove stopword = "y" or "n"
- Punctuations removal is implemented.


