from conll import ConllStruct
import codecs
from itertools import tee, islice, chain, izip
import sys
#import os
#import string
import re
#import logging
from random import randint
#logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


fpath = sys.argv[1]
ext = fpath.split(".")[-1]

############################################
## Dictionary for thematicity - SSML conversion
dictTags = {}
dictTags["pitch"] = {}
dictTags["pitch"]["sT"] = 20
dictTags["pitch"]["T"] = 15
dictTags["pitch"]["R"] = 10
dictTags["pitch"]["sSP"] = 25
dictTags["pitch"]["SP"] = 20
dictTags["pitch"]["P"] = 15
dictTags["pitch"]["Pz"] = 15

#dictTags["pitch"]["T(T)"] = 25
#dictTags["pitch"]["R(R)"] = -15
#dictTags["pitch"]["R(T)"] = 35

dictTags["rate"] = {}
dictTags["rate"]["sT"] = -25
dictTags["rate"]["T"] = -15
dictTags["rate"]["R"] = 10
dictTags["rate"]["sSP"] = -20
dictTags["rate"]["SP"] = -10
dictTags["rate"]["P"] = -10
#dictTags["rate"]["T(R)"] = 50
#dictTags["rate"]["T(T)"] = 15
#dictTags["rate"]["R(R)"] = 25
#dictTags["rate"]["R(T)"] = 45

dictTags["comb"] = {}
dictTags["comb"]["sT"] = [20,-25]
dictTags["comb"]["T"] = [15,-15]
dictTags["comb"]["R"] = [10, 10]
dictTags["comb"]["sSP"] = [25,-20]
dictTags["comb"]["SP"] = [20,-10]
dictTags["comb"]["P"] = [15,-10]

#dictTags["volume"] = {}
#dictTags["volume"]["T+9"] = -20
#dictTags["volume"]["T-9"] = 20
#dictTags["volume"]["R"] = -5
#dictTags["volume"]["SP"] = -10
#dictTags["volume"]["P"] = 30
#dictTags["volume"]["T(R)"] = 15
#dictTags["volume"]["T(T)"] = 30
#dictTags["volume"]["R(R)"] = -25
#dictTags["volume"]["R(T)"] = 30


keysDict = dictTags.keys()

#################################
def getPlusValue(posVal):
	if posVal > 0:
		posVal = "+" + str(posVal)
	else:
		posVal = str(posVal)
	return posVal

def tagtype(key,span,result, token, pos, splitWith = ""):
	if key != "comb":
		val = dictTags[key][span]
		insertProsodyTag(val, result, token, pos)
	else:
		valp = dictTags[key][span][0]
		valr = dictTags[key][span][1]
		insertcombTag(valp,valr, result, token, pos)

def insertProsodyTag(value, result, token, pos, splitWith = ""):
	vals = range(value-5, value+5, 5)
	randIdx = randint(0, len(vals)-1)
	randVal = vals[randIdx]
	plusValue = getPlusValue(randVal)
	label = "<prosody "+ key + "=\""+ plusValue + "%\">"
	result.insert(pos,label)
	if splitWith == "":
		result.append("<\\prosody>")
	else:
		wordend = token.split(splitWith)[0]
		result.append(wordend + "<\\prosody>")
	#return plusValue

def insertcombTag (valp,valr, result, token, pos, splitWith = ""):
	valsp = range(valp-5, valp+5, 5)
	randIdxp = randint(0, len(valsp)-1)
	randValp = valsp[randIdxp]
	plusValuep = getPlusValue(randValp)
	valsr = range(valr-5, valr+5, 5)
	randIdxr = randint(0, len(valsr)-1)
	randValr = valsr[randIdxr]
	plusValuer = getPlusValue(randValr)
	label = "<prosody pitch=\""+ plusValuep + "%\" rate=\"" + plusValuer + "%\">"
	result.insert(pos,label)
	if splitWith == "":
		result.append("<\\prosody>")
	else:
		wordend = token.split(splitWith)[0]
		result.append(wordend + "<\\prosody>")
	#return plusValuep, plusValuer

def insertBreak(value, result, token, conll = 1):
	label = "<boundary duration=\""+ str(value) + "\"/>"
	if conll == 1:
		result.append(label)
	else:
		wordend = token.split(">")[0]
		result.append(wordend + ">" + label)
def insertProp(value):
	label = "<prosody pitch=\""+ str(value) + "%\">"
	result.insert(pos,label)
	result.append("<\\prosody>")

########################################
result = []
checkopen = ["[","{"]
checkthem = ["}P","]T1","[T1]","]SP1","[SP1]", "{[SP1]", "R1"]
if ext == "conll":
	fd = codecs.open(fpath,"r",encoding="utf-8")
	raw_conll = fd.read()
	iCS = ConllStruct(raw_conll.encode("utf-8"))
	#print "Processing conll file"
	for idx,sentence in enumerate(iCS.sentences):
		endsent = len(sentence.token_list)
		pos = 0
		idr = randint(0,len(keysDict)-1)
		key = keysDict[idr]
		count = 0
########################################
		# Check if the sentence contains a zu construction to delete commas
		zuConst = 0
		root_id = ""
		oneSyl = 0
		nProp = 0
		for line in sentence.token_list:
			if "Pz" in line.them:
				zuConst += 1
			if "ROOT" in line.deprel :
				root_id = line.id
			if line.pos in ("PIS","PDS"):
				oneSyl = 1
				#print line
			if "}P" in line.them:
				nProp += 1

		valZu = dictTags["pitch"]["Pz"]
		valProp = dictTags["pitch"]["P"]
		rest = zuConst
		restProp = nProp
########################################
		i=0
		end = len(sentence.token_list)
		while i < end:
			token = sentence.token_list[i]
			skipcoma = 0
			if zuConst != 0 and "," in token.form and root_id == token.head:
				skipcoma += 1
			else:
				result.append(token.form)
			# Find the begining of a thematicity span and store its position
			if any(o in token.them for o in checkopen):
				pos = len(result) - 1
				if "{" in token.them :
					count += 1
					#print "Sentence = ", idx ,"count = ", count
######################
		# Apply prosody based on thematicity	
			if any(t in token.them for t in checkthem):
				if "[SP1]" in token.them :
					tagtype(key,"sSP", result, token.form, pos)
					insertBreak(400,result,token.form)
					count -= 1
				elif "]SP1" in token.them:
					tagtype(key,"SP", result, token.form, pos)
					insertBreak(200,result,token.form)
					count -= 1
				elif "[T1]" in token.them and oneSyl == 0:
					tagtype(key,"sT", result, token.form, pos)
					insertBreak(200,result, token.form)
					count -= 1
				elif "]T1" in token.them:
					tagtype(key,"T", result, token.form, pos)
					insertBreak(400,result, token.form)
					count -= 1
				elif "R1" in token.them:
					tagtype(key,"R", result, token.form, pos)
					insertBreak(300,result,token.form)
#					count -= 1	
				# Addition after feedback Pc coordinated clause, Pz um zu construction, R1 before subordinated clause
				elif "}Pc" in token.them:
					insertBreak(400,result,token.form)
					count -= 1
				elif "}Pz" in token.them:
					# Missing decaying pitch gradually in steps
					if rest == zuConst :
						insertProp(valZu)
						rest -= 1
					else :
						valZu -= 5
						insertProp(valZu)
						rest -= 1
					if token.id < end - 2 :
						insertBreak(100,result,token.form)
				elif "}P" in token.them and count == 1:
					#print "Sentence = ", idx ,"rest = ", restProp, "nProp = ", nProp
					if restProp == nProp and nProp > 3:
						insertProp(valProp)
						restProp -= 1
					## CHECK HERE condition if nprop = 2:
					elif restProp == nProp and nProp == 2:
						tagtype(key,"P", result, token.form, pos)
					else :
						valProp -= 5
						insertProp(valProp)
						restProp -= 1
					if token.id < end - 2 :
						insertBreak(400,result,token.form)
					count -= 1
				
			i += 1
		result.append("\n\n")
		pos +=1

elif ext == "txt":

	infile = open(fpath,"r").read()
	sentences = infile.split("\n\n")
	#print "Processing txt file"
	##################################### AS IT WAS IN IS2017
	for sentence in sentences:
		tokens = sentence.split(" ")
		pos = 0
		idr = randint(0,len(keysDict)-1)
		key = keysDict[idr]
		for idx,token in enumerate(tokens, 1):
			#print idx, token
			# Find the begining of a thematicity span and store its position
			if token.find(checklist[0]) != -1:
				result.append(token[1:])
				pos = len(result) - 1
			##################################### RULES NEED TO BE REVISED FOR GERMAN
			# Apply prosody considering type of span (T, R, SP, P)		
			elif token.find(checklist[3]) != -1:
				# Check theme does not contain embedded spans
				if re.findall("\D\]T1",token):
					# Apply modifications accoring to theme length
					if idx >= 9: 
						val = dictTags[key]["T+9"]
						insertProsodyTag(val, result, token, pos)
					else:
						val = dictTags[key]["T-9"]
						insertProsodyTag(val, result, token, pos)
				elif re.findall("\d\]T1",token) and checklist[2] in token:
					val = dictTags[key]["P"]
					insertProsodyTag(val, result, token, pos, "}")

			elif token.find(checklist[4]) != -1:
				val = dictTags[key]["R"]
				insertProsodyTag(val, result, token, pos,"]")

			elif token.find(checklist[5]) != -1:
				val = dictTags[key]["SP"]
				insertProsodyTag(val, result, token, pos,"]")
			elif token.endswith("]T1(T1)"):
				print checklist[6]
				val = dictTags[key]["T(T)"]
				insertProsodyTag(val, result, token, pos,"]")
			elif token.find(checklist[7]) != -1:
				val = dictTags[key]["R(T)"]
				insertProsodyTag(val, result, token, pos,"]")
			elif token.find(checklist[8]) != -1:
				val = dictTags[key]["T(R)"]
				insertProsodyTag(val, result, token, pos,"]")
			elif token.find(checklist[9]) != -1:
				val = dictTags[key]["R(R)"]
				insertProsodyTag(val, result, token, pos,"]")
			elif checklist[10] in token:
				val = dictTags[key]["P"]
				insertProsodyTag(val, result, token, pos, "}")
		
			# Include words with no thematicity marker
			else:		
				found = False
				for c in checklist:
					if c in token:
						found = True
						break
				if checklist[1] in token:
					result.append(token[1:])
				if not found:
					result.append(token)
		result.append("\n\n")
else:
	print "File format not supported."
	print "Please, provide a txt or conll file."

#print " ".join(result)
f = open(sys.argv[2], "w")
#f = open("output.conll","w")
f.write(" ".join(result))
f.close()

fd.close()