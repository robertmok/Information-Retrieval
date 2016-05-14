# Information-Retrieval

A information retrieval system simulation coded with Python.

There are two parts to this project.
- First part: A part of an information retrieval system
 
  1)  **invert.py** takes a collection of documents and generates its inverted index. It also contains options to do stemming and stopwords removal. 

  2) **test.py** tests the invert.py program. test.py will asks the user to type in a single term. If the term is in one of the documents in the collection, the program will display the document frequency and all the documents which contain this term. For each document, it will display the  document ID, the title, the term frequency and all the positions the term occurs in that document. Each time, when the user types in a valid term, the program will output the time from getting the user input to outputting the results. Finally, when the program stops, the average value for abovementioned time will also be displayed.
  
- Second part: A complete information retrieval system (Vector Space Model) 

  1) **invert.py** takes a collection of documents and generates its inverted index.
  
  2) **search.py** is the retrieval process for the vector space model. The cosine similarity formula (with length normalization) is used. A top-K retrieval method is also used. The program will return all the relevant results after a user enters a query.
  
  3) **eval.py** evalutates the performance of the information retrieval system. The program will output the average MAP (mean average precision) and R-Precision values over all queries.
