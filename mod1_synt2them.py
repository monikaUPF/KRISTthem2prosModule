from conll import ConllStruct
import codecs
from itertools import tee, islice, chain, izip
import sys

path = sys.argv[1]
#path = "out_sleep_hygiene_IR.conll"
fd = codecs.open(path,"r",encoding="utf-8")
raw_conll = fd.read()
# cd Desktop/de && python mod1_synt2them.py out_eval.conll eval_them.conll
iCS = ConllStruct(raw_conll.encode("utf-8"))

# Uncomment this variable for counts
sentCount = 0
#lineCount = 1
#############################################################################
def coordination(sentence, cdList, verbList, propcount, spcount, endcoord, startcoord = 1):
	coordspan = 0
	coord_v = ""
	verb_m = ""
	endprop1 = 0
	for c in cdList:
		#print c
		# Look for coordinated verb
		for v in verbList:
			if v.deprel == "CJ":
				coord_v = v.id
			if v.id == c.head:
				#print "Verb == Coor part "
				verb_m = v.id
				endprop1 = int(c.id) -1
				coordspan = int(c.id)
	#print "Coordination variables", startcoord, verb_m, endprop1, coordspan, coord_v, endcoord
	# CHEKC HERE
	if coordspan > startcoord :
		if verb_m != "" and c.lemma == "und":
			print "coord1"
			propcount = writeProp(sentence, propcount, endprop1, startcoord, -1)
			thematicity(sentence, verb_m, endprop1, spcount, startcoord)
		elif verb_m != "" and c.lemma != "und":
			print "coord2"
			propcount = writeProp(sentence, propcount, endprop1, startcoord)
			thematicity(sentence, verb_m, endprop1, spcount, startcoord)
		elif coord_v != "" and coordspan < coord_v:
			print "coord3"
			propcount = writeProp(sentence, propcount, endcoord, coordspan)
			thematicity(sentence, coord_v, endcoord, spcount, coordspan)
		else:
			print "Something wrong with position in Coordination"
	return propcount, spcount, coordspan

#############################################################################
# Function Write thematicity ## Frontal specifiers (before the proposition starts are not annotated)
# Note in order to write a specifier, spcount must be passed, otherwise a T1 is written
def writeThem (sentence, end, start = 1, spcount = 0):
	if end == start:
		if spcount == 0:
			endThem = sentence.tokens[str(end)]
			if endThem.them == "_":
				#print "Wr single T1"
				endThem.them = "[T1]"
			elif "[T1]" in endThem.them :
				#print "Wr single T1"
				endThem.them = endThem.them
			elif "{" in endThem.them :
				#print "Wr single T1"
				endThem.them += "[T1]"
		else:
			#print "Wr SP"
			endThem = sentence.tokens[str(end)]
			if endThem.them == "_":
				endThem.them = "[SP" + str(spcount) + "]"
				spcount += 1
			elif "[SP" in endThem.them :
				endThem.them = endThem.them
			elif "{" in endThem.them :
				endThem.them += "[SP" + str(spcount) + "]"
				spcount += 1
	else:
		beginThem = sentence.tokens[str(start)]
		if beginThem.them == "_":
			beginThem.them = "["
		elif beginThem.them in ("{", "{{") :
			beginThem.them += "["
		if spcount == 0:
			endThem = sentence.tokens[str(end)]
			if endThem.them == "_":
				#print "Wr T1"
				endThem.them = "]T1"
			elif "T1" in endThem.them :
				#print "Wr T1"
				endThem.them = endThem.them
		else:
			endThem = sentence.tokens[str(end)]
			if endThem.them == "_":
				#print "Wr SP1"
				endThem.them = "]SP" + str(spcount)
				spcount += 1
	return spcount

#############################################################################
# Function Write propositions
# NOTE: special labels for zu construction and first part of coordinated sentences are introduced as labels Pz and Pc
# CHECK HERE WHY IT IS WRITING TWO PROP WHEN THERE IS A COORDINATION
def writeProp(sentence, propcount, end, start = 1, zu = 0):
	print "Enter writeProp function"
	propcount = propcount
	if start != 0 :
		beginProp = sentence.tokens[str(start)]
		if beginProp.them == "_":
			beginProp.them = "{"
			start = 0
		else:
			beginProp.them += "{"
	else:
		print "Something wrong with start parameter"
	endProp = sentence.tokens[str(end)]
	if endProp.them == "_" and zu > 0:
		print "Cond 1"
		endProp.them = "}Pz" + str(propcount)
		propcount += 1
	elif endProp.them == "_" and zu < 0:
		print "Cond 2"
		endProp.them = "}Pc" + str(propcount)
		propcount += 1
	elif endProp.them == "_":
		print "Cond 3"
		endProp.them = "}P" + str(propcount)
		propcount += 1
	else:
		print "Cond 4"
		endProp.them = "}P" + str(propcount) + endProp.them
		propcount += 1
	return propcount

#############################################################################
# Loop forward and backwards for thematicity relations Function
def loop4back(sentence, v_id, word, spcount, begloop, endloop):
	begspan = 0
	endspan = 0
	subj = int(word.id)
	stop_p = 0
	stop_n = 0
	next = subj + 1
	prev = subj - 1
	# Check relationed tokens to span head:
	r = begloop
	countrel = 0
	while r < endloop:
		if word.id == sentence.tokens[str(r)].head:
			countrel += 1
			r += 1
		else:
			r += 1
	#print "number of tokens related to head = ", countrel
	## Loop backwards
	while stop_p == 0 :
		if prev >= 1 and countrel > 0:
			#print "Entering loop backwards", prev
			checkstart = sentence.tokens[str(prev)].head
			if checkstart == word.id :
				begspan = int(sentence.tokens[str(prev)].id)
				prev -= 1
				countrel -= 1
				#print "Begspan in Condition ", begspan
			else:
				stop_p += 1
		elif begspan == 0 :
			begspan = subj
			stop_p += 1
		else:
			stop_p += 1
	## Loop forwards						
	while stop_n == 0 :
		#print "Entering loop forwards"
		if next < endloop:
			#print "Entering loop forwards at ", next
			checkend = sentence.tokens[str(next)].head
			if checkend == word.id and countrel > 1:
				#print "condition 1"
				endspan = int(sentence.tokens[str(next)].id)
				next += 1
				countrel -= 1
				#stop_n += 1
			elif checkend != word.id and countrel > 1:
				#print "condition 2"
				endspan = int(v_id) -1
				stop_n += 1
				#print "Long theme annotated at sentence ", sentCount
			# Added condition for frontal SP with coordination
			elif int(checkend) < int(v_id) and int(checkend) != 0 and sentence.tokens[str(next)].deprel != "PUNC" and spcount != 0: 
				#print "condition plus"
				endspan = int(sentence.tokens[str(next)].id)
				next += 1
				countrel -= 1
			else: 
				#print "condition 3"
				#endspan = subj
				stop_n += 1
		else: 
			#print "full stop"
			stop_n += 1
	## Annotation of themes
	if begspan != 0 and endspan != 0:
		#print "Theme beg end ", begspan, endspan
		writeThem(sentence, endspan, begspan, spcount)
		begspan = 0
		endspan = 0

#############################################################################
# Thematicity Function 
def thematicity(sentence, v_id, endloop, spcount, begloop = 1):
	#print "Entering thematicity function ", endloop, begloop, v_id
	d = begloop
	while d < endloop:
		#print d
		word = sentence.tokens[str(d)]
		## Look for SP (prepositional phrase)
		if word.head == v_id and int(word.id) < int(v_id) and word.deprel == "MO" :
			#print "SP candidate ", word.lemma
			if spcount != 0:
				loop4back(sentence,v_id, word, spcount, begloop, endloop)
			d+= 1
		## Look for T1
		elif word.deprel == "SB" and  int(word.id) < int(v_id):
			#print "T1 candidate ", word.lemma
			loop4back(sentence,v_id, word, 0, begloop, endloop)
			d+= 1
		else:
			d += 1
	return spcount
#############################################################################
##############################################################################
for sentence in iCS.sentences:
	#print sentence
	sentCount += 1
	#print "====================================== ", sentCount
	propcount = 2
#	print "Prop Count = ", propcount
	spcount = 1
	## Check number of propositions
	nV = 0
	verbList = []
	nPunc = 0
	puncList = []
	nCD = 0
	cdList = []
	nSub = 0
	subList = []
	relclause = 0
	relList = []
	zu= 0
	zuList = []
	## this variable was nW before and was not used. Debugging endsent.
	endsent = len(sentence.tokens)
	root_id = ""
	i=1
	#print "end ", endsent
	#print sentence
	while i < endsent:
		token = sentence.tokens[str(i)]
		#if i == 1:
			#print "----", token.form
		if token.pos.startswith("V") :
			nV += 1
			verbList.append(token)
			if token.deprel == "RC":
				relclause += 1
				relList.append(token)
		if token.deprel == "PUNC" :
			nPunc += 1
			puncList.append(token)
		if token.deprel == "CD" and token.pos == "KON":
			nCD += 1
			cdList.append(token)
		if token.deprel in ("CP","MO") and token.pos in ("KOUS", "PWAV"):
			nSub += 1
			subList.append(token)
		if token.deprel == "ROOT":
			root_id = token.id
		if token.deprel == "PM" and token.pos == "PTKZU":
			zu += 1
			zuList.append(token)
		i+=1

	#print nV, nPunc, nCD, nSub, relclause, zu
################################################################################################
################################################
	# Complex sentences (more than one verbal and punctuation element)
	if nV > 1 and nPunc >= 1 :
		print "Complex sentence found "
		################################################
		# Conditions for subordinated relative clauses
		################################################
		if relclause != 0:
			# check if there are more than 2 punc (e.g. marking enumeration)
			print "Relative clause"
			relpron = 0
			endrel = 0
			rel_v = ""
			#print puncList
			for idx,p in enumerate(puncList):
				#print p
				# it doesn't check the last punctuation in the list as it is always a full stop
				# It assumes there is a relative pronoun right after punctuation (rule only valid for German)
				checkrel = int(p.id) + 1
				#print "Checkrel = ", checkrel
				for v in relList :
					#print "id verb, check =", v.id, sentence.tokens[str(checkrel)].head
					if sentence.tokens[str(checkrel)].head == v.id :
						rel_v = v.id
						relpron = checkrel
						if idx < len(puncList)-1:
							endtoken = puncList[idx + 1]
							endrel = int(endtoken.id)-1
						else:
							endrel = endsent -1
					#else:
					#	print "Something wrong in relList"
			if relpron != 0 and endrel != 0:
				print "Relative clause writing embedded proposition"
				## Revise here annotate propositions. relpron is begprop. endprop can be next p in puncList
				propcount = writeProp(sentence, propcount, endrel, relpron)
				if rel_v != "":
					#print "Relative clause writing thematicity"
					#print "SP count = ", spcount
					## Main thematicity
					thematicity(sentence, root_id, relpron, spcount)
					## Embedded THEM 
					thematicity(sentence, rel_v, endrel, relpron)
				#else:
				#	print "Something wrong in relative clause"
#####################################################################################################################
		## Conditions for subordinated clauses (non-relative)
		elif nSub != 0 :
			print "Subordinated clause"
			subpart = 0
			endsub = 0
			sub_v = ""
			prevpart = 0
			checkprevP = 0
			front = 0
			for idx,p in enumerate(puncList):
				checkp = int(p.id)
				distpunt = checkp - checkprevP
				checkend = 0
				# Checks whether the punctuation mark is not following a previous mark (e.g. :" or .")
				if distpunt != 1:
					print "Punctuation = ", p.id
					if idx != len(puncList)-1:
						#print "IDX/ len = ", idx, len(puncList)
						checkend = int(puncList[idx + 1].id)
					else:
						checkend = endsent
					written = 0
					for s in subList:
						print s
						checks = int(s.id)
						checkhead = s.head
						if checks > checkp and checks < checkend and checks != prevpart:
							subpart = checkp + 1
							endsub = checkend - 1
							#print "Subpart/endsub 1st if", subpart, endsub
						#else:
							#print "Something wrong in subList"
						elif subpart != prevpart:
							subpart = checkp + 1
							endsub = checkend - 1
							#print "Subpart/endsub 2nd if", subpart, endsub
							prevpart = 0
						# Frontal subordination
						elif checks < checkp:
							#print "Frontal subordination"
							front = 1
							subpart = checks
							endsub = checkp-1

						for v in verbList:
							if checkhead == v.id :
								sub_v = v.id
							elif int(v.id) > checks and (int(v.id)+1) == checkp:
								sub_v = v.id
						#		print "Something wrong in verbList"

					if subpart != 0 and endsub != 0 and subpart != prevpart :
						# CHECK HERE
						print "Subordinated clause writing prop = ", subpart, " to ", endsub
						propcount = writeProp(sentence, propcount, endsub, subpart)
						checkwords = endsub - subpart
						## Check if there is coordination
						if checkwords > 5 and nCD > 0 and zu == 0:
							print "Entering coordination within juxtaposition P2"
							propcount, spcount, coordspan = coordination(sentence, cdList, verbList, propcount, spcount, endsub, subpart)						
						## Embedded THEM 
						elif sub_v != "":
							print "Subordinated clause writing thematicity"
							## Main thematicity
							thematicity(sentence, root_id, subpart, spcount)
							## Rheme in main clause if there is no frontal subordination
							if front == 0 and zu == 0:
								beginR1 = sentence.tokens[root_id]
								if beginR1.them == "_":
									beginR1.them = "["
								elif beginR1.them in ("{", "{{") :
									beginR1.them += "["
								#print "Subpart var = ", subpart
								endR1 = sentence.tokens[str(subpart - 2)]
								if endR1.them == "_":
									endR1.them = "]R1"
									#print "Rheme was written"
								#else :
									#print "thematicity is not empty = ", endR1.them
							## Embedded THEM
							thematicity(sentence, sub_v, endsub, 0, subpart)
						#else:
						#	print "Subordinated clause writing prop = ", subpart, " to ", endsub
						#	propcount = writeProp(sentence, propcount, endsub, subpart)
						endsub = 0
						subpart = 0
						prevpart = subpart
				checkprevP = checkp
#####################################################################################################################
		# Conditions for juxtaposed sentences
		else :
			print "Juxtaposed sentence"
			## Check begjux
			begjux = 1
			endjux = 0
			jux_v = ""
			prevpart = 0
			for idx,p in enumerate(puncList):
				#print p
				#print idx+1, " out of ", len(puncList)
				checkp = int(p.id)
				checkhead = p.head
				for v in verbList:
					checkv = int(v.id)
					#print v
					#print "Beginning is = ", begjux
					# Write P2
					if checkv >= begjux and checkv < checkp :
						print "Write P2"
						jux_v = v.id
						endjux = checkp -1
						propcount = writeProp(sentence, propcount, endjux, begjux, zu)
						begjux = checkp + 1
						checkwords = endjux - begjux
						#print checkwords, "words"
						if checkwords > 5 and nCD > 0 and zu == 0:
							#print "Entering coordination within juxtaposition P2"
							propcount, spcount, coordspan = coordination(sentence, cdList, verbList, propcount, spcount, endjux, begjux)
						elif checkwords > 4 and zu == 0:
							thematicity(sentence, jux_v, endjux, spcount)
					# Write P3
					if checkv >= begjux and checkv > checkp and prevpart == 0 and idx == (len(puncList)-1):
						print "Write P3"
						endjux = endsent -1
						prevpart = 1
						propcount = writeProp(sentence, propcount, endjux, begjux, zu)
						checkwords = endjux - begjux
						#print checkwords, "words"
						if checkwords > 5 and nCD > 0 and zu == 0:
							#print "Entering coordination within juxtaposition P3"
							propcount, spcount, coordspan = coordination(sentence, cdList, verbList, propcount, spcount, endjux, begjux)
						elif checkwords > 4 and zu == 0:
							thematicity(sentence, jux_v, endjux, spcount)
					## CHECH HERE. Write a rule for zu sentences
					#elif checkhead == root_id and zu != 0:
					#	print "Sentence with zu"
#####################################################################################################################
################################################
	# Coordination
	elif nV > 1 and nCD > 0:
		print "Coordinated sentence write prop"
		propcount, spcount, coordspan = coordination(sentence, cdList, verbList, propcount, spcount, endsent)
		#print "Coord span = ", coordspan
		if coordspan == 0:
			#print "No coordination. Entering thematicity function"
			spcount = thematicity(sentence, root_id, endsent, spcount)
		if nSub > 0:
			#print "Found Subordinated particle"
			begsub = 0
			endsub = 0
			for s in subList:
				begsub = int(s.id)
				endsub = int(s.head)
			if begsub != 0 and endsub != 0:
				print "Write prop"
				propcount = writeProp(sentence, propcount, endsub, begsub)
				checklength = endsub - begsub
				if checklength > 6:
					thematicity(sentence, str(endsub), endsub, 1, begsub)
###################
################################################
	elif endsent > 6:
		#print "Simple sentence"
		thematicity(sentence, root_id, endsent, spcount)
###################
################################################
	# Non-verbal sentences are assumed to be titles. DELETED AFTER FEEDBACK
	#elif nV == 0:
	#	writeThem(sentence, endsent)
#########################################################################

f = open(sys.argv[2], "w")
f.write(str(iCS))
f.close()

fd.close()