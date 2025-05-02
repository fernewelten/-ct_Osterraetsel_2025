#Solver für das c't Osterrätsel April 2025, geschrieben in Python 3

import pdb # Python-Debugger freischalten
from enum import Enum, auto
from heapq import heappop, heappush # Heaps
import pickle # Programmentitäten schreiben, lesen
from math import sqrt

# Rutschrichtungen
class Dir(Enum):
	def __str__(self):
		""" Druckansicht ist nur der jeweilige reine Name """
		return f"{self.name}"
		
	# Die Richtungen sind im Uhrzeigersinn geordnet
	R = auto() # →
	D = auto() # ↓
	L = auto() # ←
	U = auto() # ↑
	
# Nach welcher Regel Chilly rutscht. 
class Mode(Enum):
	def __str__(self):
		""" Druckansicht ist der jeweilige Name """
		return f"{self.name}"
		
	NONE = 0
	TILES = auto() # Nicht zweimal auf dem gleichen Feld zum Stehen kommen
	SLIDES = auto() # Nicht zweimal denselben Rutsch vollziehen


MODE = None 		# Rutschregel
BOARD = None		# Start-Spielbrett
X_DIM = None		# Breite des Spielbretts
Y_DIM = None 		# Höhe des Spielbretts
CHILLY_LOC = None 	# Chillys Start-Standort
EXIT_LOC = None 	# End-Standort
EGGS = None			# Standorte der Eier auf dem Start-Spielbrett
EGG_DESTS = None 	# Zu jedem Ei,
					#	die Zielhaltepunkte der Rutsche, auf dem es liegt
EGG_SOURCES = None 	# Zu jedem Ei, 
					#	die Starthaltepunkte der Rutsche, auf dem es liegt
EGG_DISTANCES = None 	# Zu jedem Ei, Abstände zu den anderen Eiern
PORTALS = None 		# Von wo nach wo die Portale führen
NODES = None		# Graph der Haltepunkte auf dem Spielbrett
NODE_DIST_ESTIMATES = None # Entfernungen zwischen Haltepunkten, in Anz. Rutschen

################################################################################
# Initialisierungen

def init_game1():
	# Chillys Rutschregel
	global MODE
	MODE = Mode.SLIDES

	# Das Spielbrett beim Start
	# Felder sind "True" genau dann wenn unbetretbar (Baum, Blume, Fels)
	# Zeilen (die vertikale Dimension) nummeriere ich von oben nach unten.
	# Hinweis: Ich will später BOARD[x][y] schreiben, also die 
	# horizontale Komponente zuerst. 
	# Damit das klappt, muss ich hier "gespiegelt" initialisieren: 
	# Auf dem Bild folgen 'BOARD[0][0]', 'BOARD[1][0]', 'BOARD[2][0]' …
	# hintereinander v.l.n.r., wohingegen in der unten stehenden
	# Initialisierung diese Werte untereinander v.o.n.u. stehen.
	global BOARD
	#        Y →  0      1      2      3      4      5      6      7 	    X ↓	 
	BOARD = [ 	[ True,  False, True,  True,  True,  True,  True,  True],	# 0
				[ True,  False, False, False, False, True,  False, True], 	# 1
				[ True,  False, False, False, False, False, False, True],   # 2
				[ True,  True,  False, False, False, False, True,  True],   # 3
				[ True,  False, False, True,  False, False, False, True],   # 4
				[ True,	 False, False, False, False, False, False, True],   # 5
				[ True,	 False, False, False, True,  False, False, True],   # 6
				[ True,  False, True,  True,  True,  True,  True,  True] ]  # 7 
	
	# Dimensionen des Spielbretts
	global X_DIM
	X_DIM = 8
	global Y_DIM
	Y_DIM = 8
	
	# Chillys Standort
	global CHILLY_LOC
	CHILLY_LOC = (7, 1) 
	
	# Chillys Ziel
	global EXIT_LOC
	EXIT_LOC = (0, 1)
	
	# Lage der Eier, jeweils gegeben durch (x-Koo., y-Koo.)
	global EGGS
	EGGS = { 	(2, 1), 
				(5, 1), 
				(2, 5), 
				(4, 6) }

	# Lage des jeweiligen Ursprungs und des Ziels der Portale (Eislöcher)
	# jeweils gegeben durch (x-Koo., y-Koo.) 
	# Wenn Chilly zum Beispiel auf (4, 1) rutscht, landet er auf (6, 6)
	global PORTALS
	PORTALS =  { (4, 1): (6, 6),
				 (6, 6): (1, 4), 
				 (1, 4): (4, 1) }

def init_game2():
	global MODE
	MODE = Mode.TILES

	global BOARD
	#        Y →  0      1      2      3      4      5     			  X X
	#        Y →    6      7      8      9      10     11  	 		  ↓ ↓
	BOARD = [   [ False, False, False, False, True,  True,         #  0
					False, True,  False, False, True,  False,  ],  #    0	
				[ True,  False, False, True,  True,  False,        #  1
					False, True,  False, False, False, False,  ],  #    1	
				[ False, False, True,  False, False, True,         #  2
					False, False, False, False, False, True,   ],  #    2 	
				[ True,  False, False, False, False, False,        #  3
					False, False, True,  False, False, False,  ],  #    3 	
				[ False, False, True,  False, False, False,        #  4
					False, False, False, True,  False, False,  ],  #    4 	
				[ False, False, False, False, True,  False,        #  5
					False, True,  False, False, True,  False,  ],  #    5 	
				[ False, False, True,  False, False, False,        #  6
					True,  False, False, True,  False, False,  ],  #    6		
				[ False, False, False, False, False, False,        #  7
					False, False, False, False, False, True,   ],  #    7 	
				[ False, False, False, False, True,  False,        #  8
					True,  True,  True,  False, False, False,  ],  #    8 	
				[ False, False, False, True,  True,  True,         #  9
					False, True,  False, False, False, True,   ],  #    9 	
				[ True,  False, False, False, True,  False,        #  10
					False, True,  False, True,  False, False,  ],  #    10 	
				[ False, False, False, False, False, True,         #  11
					False, False, False, False, False, False,  ],  #    11 
				[ True,  True,  False, True,  True,  True,         #  12
					False, True,  False, False, True,  True,   ]]  #    12 
	
	global X_DIM
	X_DIM = 13
	global Y_DIM
	Y_DIM = 12
	
	global CHILLY_LOC
	CHILLY_LOC = (11, 10)
	
	global EXIT_LOC
	EXIT_LOC = (1, 1)
	
	global EGGS
	EGGS = { 	(1, 8),
				(2, 9),
				(4, 5), 
				(4, 11),
				(8, 0),
				(10, 2),
				(10, 6),
				(10, 8),
				(11, 0) }
				

	global PORTALS
	PORTALS =  { (0, 0): (11, 2), 
				 (11, 2): (0, 0) }


def init_game3():
	# Das dritte Spiel ist wie das zweite mit kleinen Abweichungen
	init_game2()
	global MODE
	MODE = Mode.EDGES
	global BOARD
	BOARD[11][8] = True

################################################################################

def print_board(eggs = set(), chilly_loc = (-1, -1)):
	""" Spielbrett ausgeben (für Debugging)
	"""
	output = f"   Chilly: {chilly_loc} | Eier: {len(eggs)} | {MODE}\nX→ "
		
	for x in range(X_DIM):
		output += "{0:<2d} ".format(x)
	output += "# ↓ Y\n"
	for y in range(Y_DIM):
		output += "   "
		for x in range(X_DIM):
			el = BOARD[x][y]
			if el:
				output += "#"	# nicht betretbar
			elif (x, y) in PORTALS:
				output += "∆"	# Portal
			elif (x, y) in eggs:
				output += "O"	# Ei
			elif (x, y) == EXIT_LOC:
				output += "↑"	# Endlage
			else:
				output += "_"
				
			if chilly_loc == (x, y):
				output += "C" 	# Hier ist Chilly
			elif (not NODES is None) and (x, y) in NODES:
				output += "*"	# Hier ist ein Rutsch-Haltepunkt
			else:
				output += "_"

			output += " "
		output += f" ← {y}\n"
	print(output)
	return 

def pb(state):
	return print_board(state.eggs, state.chilly_loc)

################################################################################

class State:
	""" Zwischenstand auf der Suche nach einer längsten Rutschfolge
	
		Ich suche eine Folge von Rutschen, die von Chillys Startposition ausgeht
		und eine Position erreicht, in der Chilly alle Eier eingesammelt hat.
		Hierbei möchte ich jeden Zwischenstand nur einmal nachhalten. 
		Als „Zwischenstand“ bezeichne ich hierbei eine Situation, die
		Chilly genau dieselben Möglichkeiten der Weitersuche bietet, 
		egal wann und wie Chilly diese Situation erreicht.
		Da sich das reine Spielbrett nicht verändert, definiert sich ein solcher
		Zwischenstand durch die folgenden Daten:
		- Chillys Standort,
		- alle Rutsche bzw. Standorte, die sich Chilly verbietet
		. die jeweilige Lage der noch nicht eingesammelten Eier
		
		Zusätzlich halte ich für den Zwischenstand in einer Zeichenkette nach,
		welche Rutsche (Richtungen) nötig sind, um den Zwischenstand zu erreichen.
	"""
	
	chilly_loc = None	# Chillys Standort
	forbidden = set()	# Rutsche bzw. Felder, die sich Chilly verbietet
	eggs = set()		# Lage der noch nicht eingesammelten Eier
	access_path = None  # Rutschfolge, um nach hier zu gelangen
	
	def __init__(self, chilly_loc, forbidden, eggs, access_path = ""):
		self.chilly_loc = chilly_loc
		self.forbidden = forbidden
		self.eggs = eggs
		self.access_path = access_path


	def __str__(self):
		return f"State(chilly_loc = {self.chilly_loc}, forbidden = {self.forbidden}, eggs = {self.eggs}, ap = {self.access_path})"

	def print(self):
		""" Ausdruck des Objekts """
		
		print(f"State(chilly_loc = {self.chilly_loc},")
		print(f"      forbidden = {self.forbidden},")
		print(f"      eggs = {self.eggs},")
		print(f"      ap = {self.access_path})")

	
	def deepcopy(self):
		""" Einen Zwischenstand in allen Teilen kopieren (sog. 'tiefe' Kopie)
	
			Return - die Kopie
		"""
		return State(self.chilly_loc, 
					 self.forbidden.copy(), 
					 self.eggs.copy(), 
					 self.access_path)


	def slide(self, dir):
		""" In die angegebene Richtung rutschen
		
			Return - None, wenn das nicht geht
				   - self, in allen anderen Fällen
		"""
		
		slide_data = NODES[self.chilly_loc].get(dir)
		if slide_data is None:
			return None # Diese Richtung ist gesperrt
		
		if MODE == Mode.TILES:
			if slide_data.dest in self.forbidden:
				return None # Hat sich Chilly verboten
			# Wenn Chilly in diesem Rutsch-Modus auf ein Portal
			# rutscht, dann kann Chilly sowohl den Ausgangspunkt
			# des Portals wiederbetreten als auch den Endpunkt,
			# laut Spezifikation in der Aufgabe.
			if not slide_data.dest in PORTALS:
				self.forbidden.add(slide_data.dest)
		elif MODE == Mode.SLIDES:
			new_edge = (self.chilly_loc, slide_data.dest)
			if new_edge in self.forbidden:
				return None # Hat sich Chilly verboten
			self.forbidden.add(new_edge)
		self.chilly_loc = slide_data.dest
		self.eggs -= slide_data.eggs
		
		return self
		
	
	def can_chilly_reach(self, dests):
		""" Ob Chilly einen Haltepunkt in 'dests' erreichen kann
		
			A*-Algorithmus
			
			Berücksichtigt werden nur diejenigen Verbote, die sich Chilly am
			Anfang dieser Funktion gesetzt hat. Verbote, die sich Chilly auf
			dem Weg zu den Ziel-Haltepunkten setzt, werden NICHT berücksichtigt.
			Das ist auch nicht nötig, denn der A*-Algo sucht den _kürzesten_
			Weg zum Ziel. Chilly hat dann nichts davon, einen Ort mehrfach zu
			betreten bzw. eine Kante mehrfach zu rutschen. In diesen Fällen 
			könnte Chilly einen kürzeren Weg rutschen, wenn er gleich richtig
			rutscht. 
			
			dests - eine Menge Knoten aus NODES
			Return - False, wenn kein Knoten aus 'dests' erreichbar ist.
		"""
		
		for dest in dests:
			# Gibt zum Haltepunkt 'node' an, wie lang der kürzest bekannte Weg 
			# ist, um von Chillys Standort aus zu 'node' zu gelangen.
			# Für Chillys Standort selbst ist das natürlich 0
			dist_to_reach = { self.chilly_loc: 0 }
			
			# Ein Heap.
			# Jedes Paar '(dist, node)' nennt die geschätzte Gesamtentfernung 
			# 'dist', um von Chillys Standort über den Haltepunkt 'node' zum 
			# Zielhaltepunkt 'dest' zu gelangen
			# Diese Schätzung darf zu tief liegen, aber nicht zu hoch.
			# Anfangs schätzen wir für Chillys Standort die Gesamtentfernung 0
			# (das ist natürlich VIEL zu tief)
			to_be_explored = [(0, self.chilly_loc)]

			while to_be_explored:
				# Wir betrachten von allen noch nicht untersuchten Orten immer
				# diejenigen zuerst, bei dem wir die geringste Gesamtentfernung 
				# vermuten. Dafür sorgt ein Heap. 'heappop()' entnimmt dem Heap
				# immer das _kleinste_ Element
				(_, current_node) = heappop(to_be_explored)

				if current_node in dests:
					return True # Suche erfolgreich
				
				dist_to_reach_successor = dist_to_reach[current_node] + 1
				for slide_data in NODES[current_node].values():
					successor = slide_data.dest
					if (MODE == Mode.SLIDES 
						and (current_node, successor) in self.forbidden):
							continue # Chilly hat sich diesen Rutsch verboten
					elif (MODE == Mode.TILES
						and successor in self.forbidden):
						continue # Chilly hat sich diesen Haltepunkt verboten
					
					if (successor not in dist_to_reach or 
						dist_to_reach_successor < dist_to_reach[successor]):
						# Wir haben einen Pfad zu 'successor' gefunden 
						# bzw. eine besseren als alle bisher bekannten. 
						if not dest in NODE_DIST_ESTIMATES[successor]:
							continue # Es gibt gar keinen Weg von dort zum Ziel
						dist_to_reach[successor] = dist_to_reach_successor
						estimate_for_total_path = \
							dist_to_reach_successor + NODE_DIST_ESTIMATES[successor][dest]
						heappush(to_be_explored, (estimate_for_total_path, successor))

		return False  # Suche fehlgeschlagen


	def is_dead_end(self):
		""" Ob dieser Zwischenstand eine Sackgasse ist
		
			Die aufgeführten Tests ignorieren alle, dass sich Chilly bei 
			seinen Wegen laufend weitere Rutsche verbietet. Diejenigen Verbote, 
			die sich Chilly jedoch im jetzigen Zwischenstand schon verboten _hat_, 
			die werden berücksichtigt.
			
			Es lohnt sich, einigen Aufwand zu betreiben, um Sackgassen zu
			identifizieren. Jeder Zwischenstand und alle seine direkten und 
			indirekten Abkömmlinge werden immer wieder ausgearbeitet, was zu
			einer exponentiellen "Vermehrung" führt. Je früher ein Zwischenstand
			ausgeschieden wird, umso weniger zwecklose Abkömmlinge können entstehen.
		
			Return - True, dann wenn dieser Zwischenstand garantiert nicht zu 
					 einem gültigen Endstand führen kann (wenn er eine Sackgasse ist)
		"""

		eggs_left = len(self.eggs)
		if (eggs_left == 0):
			# Chilly muss heraus können. Mehr ist nicht mehr zu testen
			return not self.can_chilly_reach({ EXIT_LOC })
		
		# Chilly muss jedes verbliebene Ei erreichen können.
		for egg in self.eggs:
			if not self.can_chilly_reach(EGG_SOURCES[egg]):
				return True
				
		# Eine Kopie, die ich modifizieren kann, ohne 'self' zu überschreiben
		copy = self.deepcopy()
		
		# Wenn Chilly zu jedem verbliebenen Ei teleportiert wird, dann muss 
		# Chilly von dort aus zum Ausgang können.
		for egg in self.eggs:
			for dest in EGG_DESTS[egg]:
				copy.chilly_loc = dest
				if copy.can_chilly_reach({ EXIT_LOC }):
					break
			else:
				return True
		
		if (eggs_left <= 1):
			# Mehr wüsste ich nicht, was getestet werden kann.
			return False
			
		if (eggs_left == 2):
			# Chilly muss von einem Ei zum anderen kommen, oder 
			# anders rum. Dass Chilly vom letzten Ei zum Ausgang
			# kann, haben wir schon getestet.
			(e1, e2) = list(self.eggs)
			last_egg_reachable = False
			for (egg1, egg2) in [ (e1, e2), (e2, e1) ]:
				for node in EGG_DESTS[egg1]:
					copy.chilly_loc = node
					if copy.can_chilly_reach(EGG_SOURCES[egg2]):
						last_egg_reachable = True
						break
				if last_egg_reachable:
					break
			return not last_egg_reachable
		
		# Es sind also noch mindestens drei Eier im Spiel.
		# _Alle_ Kombinationen von Eiern kann ich unmöglich abprüfen,
		# also suche ich ersatzweise zwei möglichst weit auseinander
		# liegende Eier und ein drittes, das möglichst weit von diesen
		# beiden entfernt liegt.
		# Die beiden weitest voneinander entfernten Eier bestimmen
		(best_dist, best_e1, best_e2) = (-1, None, None)
		for e1 in self.eggs:
			for e2 in self.eggs:
				if e2 == e1:
					continue
				dist = EGG_DISTANCES[e1][e2] + EGG_DISTANCES[e2][e1]
				if (dist > best_dist):
					(best_dist, best_e1, best_e2) = (dist, e1, e2)
					
		# Ein drittes Ei bestimmen, das möglichst weit von den anderen
		# entfernt liegt.
		(e1, e2) = (best_e1, best_e2)
		(best_dist, best_e3) = (-1, None)
		for e3 in self.eggs:
			if e3 == e1 or e3 == e2:
				continue
			dist = (EGG_DISTANCES[e1][e3] + 
					EGG_DISTANCES[e3][e1] + 
					EGG_DISTANCES[e2][e3] + 
					EGG_DISTANCES[e3][e2]) 
			if (dist > best_dist):
					(best_dist, best_e3) = (dist, e3)
		e3 = best_e3
		
		# Es muss eine Reihenfolge der Eier geben, die Chilly
		# hintereinander besuchen kann
		last_egg_reachable = False
		for (egg1, egg2, egg3) in [ (e1, e2, e3), 
									(e1, e3, e2), 
									(e2, e1, e3), 
									(e2, e3, e1),
									(e3, e1, e2),
									(e3, e2, e1)]:
			for node in EGG_DESTS[egg1]:
				# Dass Chilly zu jedem Ei kommt, haben wir schon 
				# abgeprüft. Aber wenn (eine Kopie von) Chilly zum
				# Endpunkt des ersten Eis teleportiert wird, kommt 
				# er von dort aus zum zweiten Ei?
				copy.chilly_loc = node
				if not copy.can_chilly_reach(EGG_SOURCES[egg2]):
					continue
				
				# Kommt Chilly auch vom zweiten zum dritten Ei?
				for qnode in EGG_DESTS[egg2]:
					copy.chilly_loc = qnode
					if copy.can_chilly_reach(EGG_SOURCES[egg3]):
						last_egg_reachable = True
						break
				if last_egg_reachable:
					break
			if last_egg_reachable:
				break
		return not last_egg_reachable


class SlideData:
	""" Eigenschaften der Kante (bzw. des Rutsches) im Graph der Haltepunkte """
	
	dest: None # Zu welchem Haltepunkt der Rutsch führt
	eggs: None # Eier, die auf dem Weg eingesammelt werden
	
	def __init__(self, dest, dir, eggs = set()):
		self.dest = dest
		self.eggs = eggs


	def __str__(self):
		return f"SlideData(dest = {self.dest}, eggs = {self.eggs})"


	def print(self):
		""" Ausdruck des Objekts """
		
		print(f"SlideData(dest = {self.dest},")
		print(f"          eggs = {self.eggs})")
		
################################################################################
# Ermittlung des Graphs der Haltepunkte und der Rutsche zwischen Haltepunkt und
# Haltepunkt, aus dem Spielbrett

def board_one_step(coo, dir):
	""" Chilly 1 Feld weit auf dem Spielbrett in die übergebene Richtung ziehen
		
		dir - 	 Eine Richtung, in die Chilly gezogen werden soll
		Return - None, 				   wenn der Schritt unmöglich ist
				 (coo, eggs, do_halt), in allen anderen Fällen
					coo 	- Chillys neue Koordinaten
					eggs	- die hier liegenden Eier
					do_halt - Ob ein Rutsch hiermit beendet ist
	"""
	(coo_x, coo_y) = coo
	
	# Chillys neuen Standort auf dem Spielbrett bestimmen
	match dir:
		case Dir.R:
			(coo_x, coo_y) = (coo_x + 1, coo_y) 
		case Dir.D:
			(coo_x, coo_y) = (coo_x, coo_y + 1) 
		case Dir.L:
			(coo_x, coo_y) = (coo_x - 1, coo_y) 
		case Dir.U:
			(coo_x, coo_y) = (coo_x, coo_y - 1)
	
	# Wenn Chilly auf der einen Seite vom Spielbrett fällt,
	# kommt er auf der anderen Seite wieder herauf.
	if coo_x < 0:
		coo_x += X_DIM
	elif coo_x >= X_DIM:
		coo_x -= X_DIM
	if coo_y < 0:
		coo_y += Y_DIM
	elif coo_y >= Y_DIM:
		coo_y -= Y_DIM
		
	if BOARD[coo_x][coo_y]:
		return None # Chilly kann nicht auf dieses Feld
	
	coo = (coo_x, coo_y)
	eggs = set()
	if coo in EGGS:
		eggs.add(coo)
	
	if coo == EXIT_LOC:
		return (coo, eggs, True) # Endlage erreicht
	
	# Chilly durchs Portal schicken, wenn er draufsteht
	try:
		coo = PORTALS[coo]
	except KeyError:
		return (coo, eggs, False)	# Kein Portal
		
	if coo in EGGS:
		eggs.add(coo)
	return (coo, eggs, True) # Portalrutsch


def board_slide(coo, dir):
	""" Chilly auf dem Spielbrett in die übergebene Richtung rutschen
	
		Chilly kommt dann also auf einem Haltepunkt zum Stehen.
		coo 	- Chillys Standort auf dem Spielbrett
		dir 	- Eine Richtung, in die Chilly gezogen werden soll
		Return - None, 			   wenn der Rutsch unmöglich ist
			   - (coo, collected), in allen anderen Fällen
					- coo       	- Chillys neuer Standort
					- collected		- Menge der eingesammelten Eier
	"""
		
	# Erster Schritt
	outcome = board_one_step(coo, dir)
	if outcome is None:
		return None # Dieser Rutsch war nicht möglich
		
	(coo, collected , do_halt) = outcome
	
	# Weitere Schritte in die gleiche Richtung
	while not do_halt:
		outcome = board_one_step(coo, dir)
		if outcome is None: # noch weiter ging nicht
			break
		(coo, eggs, do_halt) = outcome
		collected.update(eggs)
	
	return (coo, collected)
	

def construct_graph():
	""" Den Graph der prinzipiell erreichbaren Haltepunkte aufbauen
	
		'nodes[A][dir] == SlideData(B, eggs)', das bedeutet: 
		Von Haltepunkt 'A' aus kann man in Richtung 'dir' direkt zu 
		Haltepunkt 'B' rutschen. Hierbei begegnet man den Eiern in
		'eggs'. Ob sich Chilly hierbei einen Rutsch "verboten" hat,
		wird in diesem Graphen außer Acht gelassen.
		
		Gleichzeitig aufgebaut wird zu jedem Ei, die Menge der 
		Ausgangspunkte von Rutschen, die an diesem Ei vorbeiführen
		und die Menge der Endpunkte derselben.
		
		Return - Graph der Haltepunkte
	"""

	# Anfangs bekannt ist der Zielpunkt des Spielbretts.
	# Von dort aus geht es nur hinaus, es gibt also keine abgehenden Kanten
	nodes = { EXIT_LOC: dict() }
	egg_sources = { egg: set() for egg in EGGS }
	egg_dests = { egg: set() for egg in EGGS }
	
	# Liste der Haltepunkte, die noch untersucht werden müssen
	unexplored = [ CHILLY_LOC ]
	
	while unexplored:
		node = unexplored.pop();
		if not node in nodes:
			nodes[node] = dict()
		
		for dir in Dir:
			# Auf dem Spielbrett in Richtung 'dir' rutschen
			outcome = board_slide(node, dir)
			if outcome is None:
				continue # In diese Richtung kann nicht gerutscht werden
			(dest, eggs) = outcome
			nodes[node][dir] = SlideData(dest = dest, dir = dir, eggs = eggs)
			if not dest in nodes:
				# Neuer Haltepunkt gefunden. 
				# Dieser Haltepunkt muss noch untersucht werden.
				unexplored.append(dest)
			for egg in eggs:
				egg_sources[egg].add(node)
				egg_dests[egg].add(dest)
		
		# Wenn ein Ei direkt auf einem Haltepunkt liegt, dann kommt es nur
		# darauf an, dass Chilly auf diesen Haltepunkt rutscht, und nicht 
		# von wo aus bzw. wohin ab da.
		if node in EGGS:
			egg_sources[node] =  { node }
			egg_dests[node] =  { node }
		
	return (nodes, egg_sources, egg_dests)


def dijkstra(start):
	""" Berechnet zu jedem Haltepunkt die Entfernung vom Startpunkt zu ihm
		
		Dijkstras Algo
		
		start - der Startpunkt
	"""
	
	# Jedem Haltepunkt die bisher bekannte kürzeste Entfernung vom 
	# Startpunkt zuweisen. Die Entfernung wird in Rutschen gerechnet
	# Anfangs ist das beim Startpunkt 0, bei allen anderen 'unendlich'
	node_distances = { n : float('inf') for n in NODES }
	node_distances[start] = 0
	
	# Ein Heap.
	# Haltepunkte, die noch untersucht werden müssen, geordnet nach 
	# bisher bekannter kürzester Entfernung vom Startpunkt
	# Anfangs ist das nur der Startpunkt
	unexplored = [(0, start)]
	
	while unexplored:
		# Immer denjenigen Haltepunkt entnehmen, der dem Startpunkt
		# am nächsten liegt. 
		(current_distance, current_node) = heappop(unexplored)
		
		if current_distance > node_distances[current_node]:
			# Ein kürzerer Weg hierher ist schon bekannt,
			# also brauchen wir diesen nicht weiter zu verfolgen
			continue 
		
		# Entfernung vom Startpunkt, wenn wir über den aktuellen 
		# Haltepunkt zu einem seiner Nachfolger gehen 
		new_distance = current_distance + 1
		for edge_data in NODES[current_node].values():
			successor = edge_data.dest
			if new_distance < node_distances[successor]:
				# Aktualisiere die bekannte kürzeste Entfernung
				node_distances[successor] = new_distance
				# Diesen Nachfolger müssen wir noch untersuchen
				heappush(unexplored, (new_distance, successor))

	# Wenn 'node_distances' für einen Haltepunkt jetzt immer noch die 
	# Entfernung 'unendlich' eingetragen hat, dann ist dieser nicht vom
	# Startpunkt erreichbar. Diese Einträge löschen, der Übersicht wegen.
	return { key: v for key, v in node_distances.items() if v != float('inf') }


def calc_dist_estimates():
	""" Schätzwerte für den Abstand zu Haltepunkten und Eiern berechnen
	
		Die Schätzwerte wären exakt ohne dasjenige, was sich Chilly 
		verbietet - so aber UNTERschätzen sie die tatsächlichen Abstände
	"""
	
	node_dist_estimates = dict()
	
	for node in NODES:
		node_dist_estimates[node] = dijkstra(node)
	return node_dist_estimates


def calc_egg_distances():
	""" Berechne, wie weit Eier auseinander liegen 
	
		Berechnet wird jeweils die kürzeste Entfernung.
	"""
	
	egg_dists = dict()
	
	for egg_from in EGGS:
		egg_dists[egg_from] = dict()
		for egg_to in EGGS:
			if egg_to == egg_from:
				egg_dists[egg_from][egg_to] = 0 
				continue
			best_dist = float('inf')
			for node_from in EGG_DESTS[egg_from]:
				for node_to in EGG_SOURCES[egg_to]:
					if NODE_DIST_ESTIMATES[node_from].get(node_to, float('inf')) < best_dist:
						best_dist = NODE_DIST_ESTIMATES[node_from][node_to]
			egg_dists[egg_from][egg_to] = best_dist
			
	return egg_dists


def search_solution():
	""" Systematisch nach Rutschfolgen suchen, die Chilly zum Ausgang führen

		Da diese Routine seeeeehhhr lang dauert, laufend die besten gefundenen
		Rutschfolgen in einer Datei speichern. So kann der Suchlauf jederzeit
		vorzeitig abgebrochen werden. 
		
		Es sind auch noch einige 'print()' zu Debugging-Zwecken im Programmcode
		verblieben.
	
		Return - None, wenn es keine solche Rutschfolge gibt
		       - die längste gefundene Rutschfolge, in allen anderen Fällen 
	"""
	
	# Eine Zeichenkette, die angibt, wie man zu einem "gewinnenden" Endstand kommt.
	best_winner_so_far = None
	best_winner_length = -1
	best_state_slide_length = -1
	
	# Anfangsstand. Zum Aufbau, siehe die Klassendefinition von 'State'
	init_state = State(CHILLY_LOC, set(), EGGS, "")
	
	# Wie die Zwischenstände priorisieren, das ist die Frage …!
	# Grundsätzlich ist ein Zwischenstand mit vielen Rutschen besser, denn
	# Chilly will ja einen _langen_ Weg finden. Die Weglänge ist also ein 
	# positives Priorisierungs-Kriterium. 
	# Chilly soll sich mit dem Einsammeln der Eier Zeit lassen. Also sind 
	# viele schon eingesammelte Eier ein negatives Priorisierungs-Kriterium.
	# Aber hier ist die Sache nicht so einfach: Wenn anfangs noch nicht 
	# viele Eier gesammelt sind, ist es vielleicht besser, dass Chilly öfter 
	# rutscht, denn das macht es leichter, Sackgassen bei den späteren 
	# Zuständen auszumachen (je mehr Rutsche, desto mehr verbotene Haltepunkte
	# oder Kanten). Später im weiteren Verlauf ist es aber besser, dass Chilly 
	# zu Potte kommt und die verbliebenen  Eier einsammelt, sonst kommt er nie 
	# zum Ziel. 
	# Also definiere ich mal die Anzahl der gesammelten Eier als negativen Anreiz
	# und die Anzahl der Rutsche als positiven Anreiz, aber die Quadratwurzel 
	# davon.
	# Dass ich die Anzahl der Eier halb werte, das kann ich nicht rechtfertigen.
	# Diesen Multiplikator habe ich durch "Fummeln" bzw. blindes Hin- und
	# Herprobieren ermittelt.
	# Der in dieser Funktion verwendete Heap läuft sehr, sehr voll. Um
	# Hauptspeicher zu sparen, schiebe ich nicht die Zwischenstände selbst auf
	# den Heap, sondern eine speichergünstige Abart davon. 
	def push_to_heap(state):
		eggs_found = len(EGGS) - len(state.eggs)
		slide_count = len(state.access_path)
		compact_state = (state.chilly_loc, 
						 tuple(state.forbidden), 
						 tuple(state.eggs), 
						 state.access_path)
		estimate = eggs_found/2 - sqrt(slide_count)
		heappush(unexplored, (estimate, compact_state))
		
	def pop_from_heap():
		(_, compact_state) = heappop(unexplored)
		(chilly_loc, forbidden, eggs, access_path) = compact_state
		return State(chilly_loc, set(forbidden), set(eggs), access_path)
	
	# Heap der noch zu bearbeitenden Zwischenstände, wird ggf. in Dateien 
	# ausgelagert, wenn er zu voll wird
	unexplored = []
	heap_max = 6000000 # Größer darf der Heap nicht werden
	push_to_heap(init_state)
	
	state_count = 0 # Anzahl bearbeiteter Zwischenstände
	pruned_count = 0 # Anz. der als Sackgassen erkannten Zwischenstände
	batch_state_count = 0 # Anz. in der aktuellen Charge
	batch_pruned_count = 0
	batch_added_count = 0
	
	# Diese beiden Dateien dienen als externen Puffer, wenn zu viele Zwischenstände
	# auflaufen, um im Hauptspeicher gehalten zu werden. Es werden immer
	# Zwischenstände aus einer Datei (fp_in) gelesen und neue Zwischenstände (fp_out) 
	# in eine andere Datei geschrieben. 
	# Wenn die Datei 'fp_in' jeweils vollständig durchlaufen ist und sich herausstellt, 
	# dass Zwischenstände in 'fp_out' stehen, dann werden die Rollen von 'fp_in' und 
	# 'fp_out' getauscht und die (jetzige) Datei 'fp_out' gelöscht. Sobald etwas Platz 
	# im Hauptspeicher ist, werden Elemente von fp_in dort hereingemischt.
	with open("G:\\Temp\\{MODE}{X_DIM}-1.dat", mode='w+b') as fp1:
		with open("G:\\Temp\\{MODE}{X_DIM}-2.dat", mode='w+b') as fp2:
			fp_in = fp1
			fp_out = fp2
			
			while True: 
				# Hole den nächsten Zwischenstand
				current_state = None
				if unexplored:
					current_state = pop_from_heap()
				while len(unexplored) < heap_max:
					# Zwischenstände aus den Pufferdateien holen und hereinmischen
					try: 
						stuffed = pickle.load(fp_in)
						push_to_heap(stuffed)
						stuffed = None
					except EOFError:
						fp_out.flush() # Ggf. gepufferte Ausgaben wegschreiben
						if fp_out.tell() == 0:
							# Keine gepufferten Zwischenstände mehr
							break
						# Rollen von 'fp_in' und 'fp_out' tauschen
						(fp_out, fp_in) = (fp_in, fp_out)
						fp_in.seek(0)
						fp_out.seek(0)
						fp_out.truncate(0)
				if current_state is None:
					if not unexplored: 
						break # Fertig: Alle Zwischenstände untersucht
					current_state = pop_from_heap()
				
				state_count += 1
				batch_state_count += 1
				
				current_slides = len(current_state.access_path)
				if ((batch_state_count >= 200000) or
					current_slides > best_state_slide_length):
					if current_slides > best_state_slide_length:
						best_state_slide_length = current_slides
					print(f"# slides: {current_slides},", 
						  f"states: {state_count:_},",
						  f"pruned: {pruned_count:_},",
						  f"b-states: {batch_state_count:_},",
						  f"b-added:  {batch_added_count:_},",
							  f"b-pruned: {batch_pruned_count:_},",
						  f"winner: {best_winner_so_far} ({best_winner_length})")
					with open("c:\\temp\\log.txt", "a") as log:
						print(f"# slides: {current_slides},", 
							  f"states: {state_count:_},",
							  f"pruned: {pruned_count:_},",
							  f"b-states: {batch_state_count:_},",
							  f"b-added:  {batch_added_count:_},",
							  f"b-pruned: {batch_pruned_count:_},",
							  f"winner: {best_winner_so_far} ({best_winner_length})",
							  file = log)	
					print("    current # eggs:", len(current_state.eggs),
						  "    Füllstand: ", len(unexplored), len(unexplored) / heap_max)
					batch_state_count = 0
					batch_added_count = 0
					batch_pruned_count = 0
					
				if current_state.chilly_loc == EXIT_LOC:
					# Dieser Zwischenstand ist ein Endstand.
					# Nur Endstände, bei denen alle Eier eingesammelt sind, zählen.
					if current_state.eggs:
						pruned_count += 1
						continue
					
					winner_ap = current_state.access_path
					winner_length = len(winner_ap)
					if best_winner_length < winner_length:
						(best_winner_so_far, best_winner_length) = (winner_ap, winner_length)
						winfile = f"G:\\temp\\{X_DIM}-winners.txt"
						with open(winfile, "a") as win_fp:
							print(f"{winner_length:3d}", 
								  current_state.access_path, 
								  file = win_fp)
					continue
				
					
						
				# Alle Rutschmöglichkeiten von diesem Zwischenstand aus durchgehen 
				for dir in Dir:
					new_state = current_state.deepcopy();
					result = new_state.slide(dir);
					if result is None: 
						new_state = None
						continue # In diese Richtung zu rutschen, ist nicht möglich
					new_state.access_path += str(dir)	
					# Dieser Zwischenstand ist neu
					
					if new_state.chilly_loc == EXIT_LOC:
						# Dieser Zwischenstand ist ein Endstand.
						# Nur Endstände, bei denen alle Eier eingesammelt sind, zählen.
						if new_state.eggs:
							new_state = None
							continue
					
						winner_ap = new_state.access_path
						winner_length = len(winner_ap)
						if best_winner_length < winner_length:
							(best_winner_so_far, best_winner_length) = (winner_ap, winner_length)
							winfile = f"G:\\temp\\{MODE}{X_DIM}-winners.txt"
							with open(winfile, "a") as win_fp:
								print(f"{winner_length:3d} {winner_ap}", file = win_fp)
						continue
					
					# Beim Durchkämmen von Suchräumen ist es entscheidend wichtig,
					# Zwischenstände so früh wie möglich auszuscheiden, 
					# sobald klar und sicher ist, dass sie nicht mehr zum Ziel 
					# führen können. Ansonsten verschwendet das Programm viel 
					# Aufwand mit dem Ausforschen von Sackgassen.
					if new_state.is_dead_end():
						pruned_count += 1
						batch_pruned_count += 1
						new_state = None
						continue	
					
					batch_added_count += 1
					if len(unexplored) < heap_max:
						push_to_heap(new_state)
					else:
						# Überlauf in Datei schreiben
						fpos = fp_out.tell()
						try:
							pickle.dump(new_state, fp_out)
						except OSError as e:
							# Wir sind anscheinend völlig voll. Der Zwischenstand
							# fällt durch das Raster.
							fp.out.seek(fpos)
					new_state = None
		
	# Alle Zwischenstände sind jetzt abgearbeitet.
	return best_winner_so_far
	
################################################################################
################################################################################
# Hauptprogramm

# Je nach Aufgabe die zugehörige Funktion entkommentieren:
#init_game1()	# Rutschpartie 1
#init_game2()	# Rutschpartie 2
init_game3()	# Rutschpartie 3

(NODES, EGG_SOURCES, EGG_DESTS) = construct_graph()
print_board(EGGS, CHILLY_LOC)

NODE_DIST_ESTIMATES = calc_dist_estimates()
EGG_DISTANCES = calc_egg_distances()

SOLUTION = search_solution()

if SOLUTION is None:
	print("🐧 Chilly schmollt. Er konnte keine Lösung bestimmen")
else:
	print(f"🐧 Chilly fand eine Lösung mit {len(SOLUTION)} Rutschen.");
	print(f"Sie lautet: {SOLUTION}")
	