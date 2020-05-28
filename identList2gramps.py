#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 29 23:05:13 2020

Function to convert csv family tree (idented list) to Gramps CSV

@author: luiz
"""

fileName = "/media/luiz/Volume/Dokumente/Fotografien und Videos/ÁrvoreGen/A GRANDE ÁRVORE - Medeiros (csv export).csv"

import pandas as pd
import numpy as np

import individuum as ind

data = pd.read_csv(fileName, delimiter=';')

def isInt(s):
    try:
        int(s)
        return True
    except:
        return False

# User preferences:
buildGraph = False

# Initializing vars:
nameList = []
genList = []
symbList = []
nameSet = set([])
if buildGraph == True:
    indivArr = np.array([])
else:
    indivSet = set([])
nextIsName = False
nextIsChild = True
blockBegin = True
ident = 0
for iRow, row in enumerate(data.itertuples()):
    generation = 0
    for iCol, element in enumerate(row):
        if element == '|':
            generation = generation + 1
        if iRow >= 2 and iCol >= 2 and iCol <= 11:
            if type(element) == str and nextIsName == True: #and len(element) > 2: # looks like a name
                nameList.append(element) # preserve order
                genList.append(generation) # put current generation
                if element not in nameSet:
                    if blockBegin == True:
                        indiv = ind.individuum(name = element, bithday = row[16], death = row[17])
                    elif nextIsChild == False:
                        indiv = ind.individuum(name = element, bithday = row[16], death = row[17])
                    else:
                        nameArr = np.array(nameList)
                        genArr = np.array(genList)
                        symbArr = np.array(symbList)
                        if buildGraph == False:
                            parent1 = str(nameArr[genArr == generation - 1][-1]) # last person whose generation is the last
                            #parent2 = str(nameArr[genArr == generation - 1 and (symbArr[:-1] != 'z')][-2]) # before last person whose generation is the last
                            parent2 = str(nameArr[np.logical_and(genArr == generation - 1, symbArr != 'z')][-1]) # before last person whose generation is the last
                        else:
                            parent1 = indivArr[genArr[:-1] == generation - 1][-1] # last person whose generation is the last
                            parent2 = indivArr[np.logical_and(genArr[:-1] == generation - 1, symbArr[:-1] != 'z')][-1] # before last person whose generation is the last
                        indiv = ind.individuum(name = element, father = parent2, mother = parent1, birthday = row[17], death = row[18], bplace = row[16]) # parents will be inverted in some cases, but... there is no gender info in the table
                nameSet.add(element) # prevent adding the same person again
                indiv.ident = ident
                ident = ident + 1
                if buildGraph == False:
                    indivSet.add(indiv)
                else:
                    indivArr = np.append(indivArr, indiv)
                nextIsName = False
            elif type(element) == str and len(element) == 1: # is one-character long
                if element == 'z': # next element is non-filio, but spouse or partner
                    symbList.append('z')
                    blockBegin = False
                    nextIsChild = False #
                    nextIsName = True
                elif element == 'v': # begin of a new block
                    symbList.append('v')
                    blockBegin = True#
                    nextIsName = True
                elif isInt(element): # next element: counting children
                    symbList.append(element)
                    blockBegin = False
                    nextIsChild = True
                    nextIsName = True

famSet = set()
for indiv in indivSet:
    famSet.add((indiv.mater, indiv.pater))

# now going to build a dataframe
headLines = "Person	Surname	Given	Call	Suffix	Prefix	Title	Gender	Birth date	Birth place	Birth source	Baptism date	Baptism place	Baptism source	Death date	Death place	Death source	Burial date	Burial place	Burial source	Note".split('	')

dataTb = pd.DataFrame([])

dataDict = dict([])
for indiv in indivSet:
    dataDict['id1'] = indiv.ident#id
    dataDict['Person'] = '[I' + "{:04d}".format(indiv.ident) + ']' #id
    
    # if there is a nickname between brackets:
    if indiv.nomen.find('(') != -1:
        dataDict['Nick'] = indiv.nomen[indiv.nomen.find("(")+1:indiv.nomen.find(")")]
        name = indiv.nomen[:indiv.nomen.find('(')].rstrip()
    else:
        dataDict['Nick'] = ''
        name = indiv.nomen

    if len(name.split(' ')) > 1: # if there is a complete name
        dataDict['Surname'] = name.split(' ')[-1] # last
        dataDict['Given'] = ' '.join(name.split(' ')[:-1])
    else: # if the name is only one word
        dataDict['Given'] = name # until any '(' and remove whitespaces at the end
        dataDict['Surname'] = ''
    
    dataDict['Full name'] = indiv.nomen
    dataDict['Birth date'] = indiv.natalis
    dataDict['Death date'] = indiv.mortis
    dataDict['Birth place'] = indiv.locNatalis
    dataTb = dataTb.append(dataDict, ignore_index=True)

famId = 0
marrDict = dict([])

marrTb = pd.DataFrame([])
for fam in famSet:
    if fam == (None, None): # case both parents are not given
        continue # skip, go to the next
    marrDict['id2'] = famId
    marrDict['Marriage'] = '[F' + "{:04d}".format(famId) + ']'
    hb = int(dataTb.loc[(dataTb['Full name'] == fam[1])]['id1'])
    wf = int(dataTb.loc[(dataTb['Full name'] == fam[0])]['id1'])
    marrDict['Husband'] = '[I' + "{:04d}".format(hb) + ']'
    marrDict['Wife'] = '[I' + "{:04d}".format(wf) + ']'
    marrDict['Husband Name'] = fam[1]
    marrDict['Wife Name'] = fam[0]
    famId = famId + 1
    marrTb = marrTb.append(marrDict, ignore_index=True)

famDict = dict([])
famTb = pd.DataFrame([])
for indiv in indivSet:
    if indiv.mater != None and indiv.pater != None: # both parents are given/listed
        indFam = marrTb.loc[(marrTb['Husband Name'] == indiv.pater) & (marrTb['Wife Name'] == indiv.mater)] # locating family of individual
        famDict['Family'] = '[F' + "{:04d}".format(int(indFam['id2'])) + ']'
        famDict['Child'] = '[I' + "{:04d}".format(indiv.ident) + ']' 
        famTb = famTb.append(famDict, ignore_index=True)
    elif indiv.mater != None: # only father is given
        print('ignoring for now family for: ' + indiv.nomen)
    elif indiv.pater != None:
        print('ignoring for now family for: ' + indiv.nomen)

completeTb = dataTb
completeTb = completeTb.join(marrTb, how='outer')
completeTb = completeTb.join(famTb, how='outer')

completeTb.to_csv('/media/luiz/Volume/Dokumente/Fotografien und Videos/ÁrvoreGen/out.csv')
# with open('csvfile.csv','wb') as file:
#     for line in text:
#         file.write(line)
#         file.write('\n')