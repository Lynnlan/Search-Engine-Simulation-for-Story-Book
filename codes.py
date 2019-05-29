import string
import math

# *******************************************************************************
# create a list of stopwords: forbidden.

stopword = open('stopwords.txt', 'r', encoding='utf-8')
forbidden = []

for line in stopword:
    word = line.strip()
    forbidden.append(word)
stopword.close()

# *******************************************************************************
# prepare for printing all titles.

# all_title is a list that store all titles of fairy tale. This is used to print the "building index" part.
all_title = []


def print_title(tlist):
    for i in range(len(tlist)):
        print(i + 1, tlist[i])


# *******************************************************************************
# manipulate grimms and build index

w2s = {}
grimms = open('grimms.txt', 'r', encoding='utf-8')
g = grimms.readlines()

for i in range(124, 9182):
    gline = g[i].strip()

    # find title of each story.
    if gline.isupper():
        # if an all uppercase sentence has a number in the string, it is a sub-title which will be skipped.
        # this is used to deal with the two parts of "The Adventures of Chanticleer and the Partlet"
        if any(char in '0123456789' for char in gline) == False:
            title = gline
            all_title.append(title)
        continue
    else:
        # remove punctuations for lines in story
        for c in string.punctuation:
            gline = gline.replace(c, "")

    #  dictionary of dictionary
    for word in gline.lower().split():
        # skip words in stopwords.txt and use lower() to change words to lowercase.
        if word not in forbidden:
            w2s.setdefault(word, {}).setdefault(title, []).append(i)

grimms.close()


# *******************************************************************************
#  the function to print out the result of the search query.


def printResult(aquery):
    # append all query word into a list: qwlist.
    qwlist = []
    for w in aquery.strip().split():
        qwlist.append(w)
    print("query =  " + aquery.strip())

    # decide which boolean word in the query and lead to right function.
    if len(qwlist) == 1:
        printOneResult(qwlist[0])
    elif len(qwlist) == 2:
        printAndResult(qwlist)
    elif len(qwlist) == 3:
        if qwlist[1] == 'or':
            del qwlist[1]
            printOrResult(qwlist)
        elif qwlist[1] == 'and':
            del qwlist[1]
            printAndResult(qwlist)
        elif qwlist[1] == 'morethan':
            del qwlist[1]
            printMorethanResult(qwlist)
        elif qwlist[1] == 'near':
            del qwlist[1]
            printNearResult(qwlist)
        else:
            printManyResult(qwlist)
    else:
        printManyResult(qwlist)


# *******************************************************************************
# The function when the query only contains one word.


def printOneResult(qword):
    # store all possible titles into a list
    title_list = []
    if qword in w2s:
        for k in w2s[qword].keys():
            title_list.append(k)
        for t in title_list:
            print('\t', t)
            printLine(qword, t)
    else:
        print('\t--')


# *******************************************************************************
# The function when the query contains 'or' word.


def printOrResult(qwlist):
    # store all possible titles into a list
    title_list = []
    for qword in qwlist:
        if qword in w2s:
            for k in w2s[qword].keys():
                # this "if" is to guarantee the uniqueness of title in the list.
                if k not in title_list:
                    title_list.append(k)

    if len(title_list) == 0:
        print('\t\t--')

    # print the result of "or" query.
    for t in title_list:
        print('\t', t)
        for qword in qwlist:
            # if the query word is not in w2s's key, print '--'
            if qword not in w2s:
                print('\t\t', qword, '\n\t\t\t--')
            else:
                # for each query word see whether w2s[query word][t] exists
                # which means to find out whether current title in title_list also in w2s[query word].keys().
                if w2s[qword].get(t, 0) != 0:
                    print('\t\t', qword)
                    printLine(qword, t)
                else:
                    print('\t\t', qword, '\n\t\t\t--')


# *******************************************************************************
# The function when the query contains 'and' word or contains 2 words that joint by whitespace.


def printAndResult(qwlist):
    title_list = []
    if qwlist[0] not in w2s or qwlist[1] not in w2s:
        print('\t--')
    else:
        # store common titles of two query words into title_list.
        for k in w2s[qwlist[0]].keys():
            if k in w2s[qwlist[1]].keys():
                title_list.append(k)
        if len(title_list) == 0:
            print('\t--')
        else:
            for t in title_list:
                print('\t', t)
                for qword in qwlist:
                    print('\t\t', qword)
                    printLine(qword, t)


# *******************************************************************************
# The function when the query contains more than 2 words that joint by whitespace.


def printManyResult(qwlist):
    # title_list is to store all fairy tale titles that contains one of the word in qwlist.
    title_list = []
    # num_in_w2s is to count the number of words in the query which are also in w2s.keys().
    num_in_w2s = 0
    for qword in qwlist:
        if qword in w2s:
            for t in w2s[qword].keys():
                title_list.append(t)
            num_in_w2s += 1

    # num_in_w2s == len(qwlist) means all words in query are in w2s.keys(). So, if num_in_w2s != len(qwlist), we can print "--" directly.
    if num_in_w2s == len(qwlist):
        # frequency_dic is a dictionary: key: title name ; value: the frequency each title appears in the title_list.
        frequency_dic = dict((x, title_list.count(x)) for x in set(title_list))

        # new_title_list is a list that store the all story titles that contains all words in the query.
        # if one title's frequency (frequency_dic[story name]) equals the length of query, this is the title we need to found. I'll store it in the "new_title_list".
        new_title_list = []
        for akey in frequency_dic:
            if frequency_dic[akey] == len(qwlist):
                new_title_list.append(akey)

        for t in new_title_list:
            print('\t', t)
            for qword in qwlist:
                print('\t\t', qword)
                printLine(qword, t)
    else:
        print('\t--')


# *******************************************************************************
# The function when the query contains 'near'


def printNearResult(qwlist):
    title_list = []
    if qwlist[0] not in w2s or qwlist[1] not in w2s:
        print('\t--')
    else:
        for k in w2s[qwlist[0]].keys():
            if k in w2s[qwlist[1]].keys():
                title_list.append(k)
        if len(title_list) == 0:
            print('\t--')
        else:
            for t in title_list:
                for line_num1 in w2s[qwlist[0]][t]:
                    for line_num2 in w2s[qwlist[1]][t]:
                        if math.fabs(line_num1 - line_num2) <= 1:
                            print('\t', t)
                            printLine(qwlist[0], t)
                            printLine(qwlist[1], t)


# *******************************************************************************
# The function when the query contains 'morethan'


def printMorethanResult(qwlist):
    title_list = []

    #this is for the pattern "word morethan number"
    if qwlist[1].isdigit():
        for k in w2s[qwlist[0]].keys():
            if len(w2s[qwlist[0]][k]) > int(qwlist[1]):
                title_list.append(k)
        if len(title_list) == 0:
            print('\t--')
        else:
            for s in title_list:
                print('\t', s)
                printLine(qwlist[0], s)
    #this is for the pattern "word1 morethan word2"
    else:
        for k in w2s[qwlist[0]].keys():
            title_list.append(k)
        for s in title_list:
            # if word2 doesn't in story of current title, the frequency of word1 will morethan word2 (has a 0 frequency).
            if s not in w2s[qwlist[1]].keys():
                print('\t', s, '\n\t\t', qwlist[0])
                printLine(qwlist[0], s)
                print('\t\t', qwlist[1], '\n\t\t\t--')
            else:
                if len(w2s[qwlist[0]][s]) > len(w2s[qwlist[1]][s]):
                    print('\t', s)
                    printLine(qwlist[0], s)
                    printLine(qwlist[1], s)


# *******************************************************************************
# the function to print all the lines that contain the query string


def printLine(qword, t):
    for num in w2s[qword][t]:
        # highlight the query word.
        highlight = g[num].replace(qword, '**' + qword.upper() + '**')
        print('\t\t\t', num, highlight.strip())


# *******************************************************************************
# Loading process


print('Loading stopwords...\n', forbidden)
print('\nBuilding index...')
print_title(all_title)
print("\nWelcome to the Grimms' Fairy Tales search system!\n")

# *******************************************************************************
# testing


stop_sign = True
# the input query sign will show repeatly until the sign of stop: 'qquit'
while stop_sign:
    query = input("Please enter your query:")
    if query != 'qquit':
        printResult(query)
        print()
    else:
        stop_sign = False
