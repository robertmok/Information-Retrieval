#Design & Details
The stemming algorithm I used is Porter’s stemming algorithm, I used the python version created by Vivake Gupta. I used the common_words file for the stop words removal process. 

**invert.py** will start by applying stemming first if you have chosen to then it will remove stop words if you have chosen to. Stemming and stop words removal is only applied to the title and the abstract in the collection. If the stemming was chosen, it will apply stemming to collection and save to file output.txt. If stop words removal was chosen, it will apply it and save to file temp.txt. After that, the program will extract all the terms from the title and abstract and store it with the document ID in an array named dict2. After extraction, the terms are sorted alphabetically. The program will now group the same terms together creating a dictionary and posting. Dictionary is saved in an array named dictionary and posting is saved in an array named posting. The link to posting saved in the dictionary, it is the index to the posting array for that term.  The dictionary starts off empty then for each term in dict2 it will see if it is in the dictionary yet. If not, then the term is added to dictionary and posting for that term is added. If it is in the dictionary then it will search for the document number in posting. If document number is found then the document and term frequency is increased. If the document number is not found then it is added to posting. When that process is done, a dictionary and posting will be created. Dictionary and posting are saved to files, dictionary.txt and posting.txt. 

In **test.py**, there is an option to apply stemming to your query term. The program will read in the dictionary and posting from dictionary.txt and posting.txt. Next, the program will ask for a user input for a term. The user then has a choice to apply stemming to the term or not. The program will now find the term in the dictionary. If term is found then it will find and print the title and abstract for each document ID listed in the posting for that term.

#Instructions
1.	Make sure you have Python version 2.7 installed
2.	Make sure you have the following files:

    a.	invert.py 
    
    b.	test.py
    
    c.	output.txt
    
    d.	temp.txt
    
    e.	dictionary.txt
    
    f.	posting.txt
    
    g.	cacm.all
    
    h.	common_words
3.	Make sure all the files are in the same directory 
4.	Make sure files: output.txt, temp.txt, dictionary.txt, posting.txt are empty when you run invert.py! Delete text in those files if you want to run again!
5.	invert.py need files from “c.” to “h.” to run
6.	test.py needs files “e.” to “g.” to run
7.	 Open index.py or test.py in:

    a.	Python 2.7.6 IDLE, click Run from top menu and click Run Module or just press F5
    
    b.	Python PyScripter , click green arrow in the toolbar at the top or just press CTRL+F9
 
