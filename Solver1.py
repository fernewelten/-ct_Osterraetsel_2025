#Solver für das c't Osterrätsel April 2025

import pdb # Python-Debugger freischalten
from enum import Enum, auto
from heapq import heappop, heappush # Heaps
from tempfile import SpooledTemporaryFile # Temporäre Dateien
import pickle # Programmentitäten schreiben, lesen

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
	EDGES = auto() # Nicht zweimal entlang der gleichen Kante laufen


MODE = None 		# Rutschregel
BOARD = None		# Start-Spielbrett
X-DIM = None		# Breite des Spielbretts
Y-DIM = None 		# Höhe des Spielbretts
CHILLY_LOC = None 	# Chillys Start-Standort
EXIT_LOC = None 	# End-Standort
EGGS = None			# Standorte der Eier auf dem Start-Spielbrett
EGG_DESTS = None 	# Zu jedem Ei,
					#	die Zielhaltepunkte der Kanten, auf dem es liegt
EGG_SOURCES = None 	# Zu jedem Ei, 
					#	die Starthaltepunkte der Kanten, auf dem es liegt
EGG_DISTANCES = None 	# Zu jedem Ei, Abstände zu den anderen Eiern
PORTALS = None 		# Von wo nach wo die Portale führen
NODES = None		# Graph der Haltepunkte auf dem Spielbrett
NODE_DIST_ESTIMATES = None # Entfernungen zwischen Haltepunkten

################################################################################
# Initialisierungen

def init_game1():
	# Chillys Rutschregel
	global MODE
	MODE = Mode.EDGES

	# Das Spielbrett beim Start
	# Felder sind "True" genau dann wenn unbetretbar (Baum, Blume, Fels)
	# Zeilen nummeriere ich von oben nach unten.
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
	
	#Chillys Ziel
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
	# Wenn Chilly zum Beispiel auf (0, 3) rutscht, landet er auf (3, 0)
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
				output += "^"	# Endlage
			else:
				output += "_"
				
			if chilly_loc == (x, y):
				output += "C" 	# Hier ist Chilly
			elif (not NODES is None) and (x, y) in NODES:
				output += "*"	# Hier ist ein möglicher Rutsch-Haltepunkt
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
		. die noch nicht eingesammelten Eier (jew. gegeben durch ihren Standort)
		
		Zusätzlich halte ich für den Zwischenstand in einer Zeichenkette nach,
		welche Rutsche nötig sind, um den Zwischenstand zu erreichen.
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

	def slide(self, dir)
		""" In die angegebene Richtung rutschen
		
			Return - None, wenn das nicht geht
				   - self, in allen anderen Fällen
		"""
		
		edge_data = NODES[self.chilly_loc].get(dir)
		if edge_data is None:
			return None # Diese Richtung ist gesperrt
			
		if MODE == Mode.TILES:
			if edge_data.dest in self.forbidden:
				return None # Hat sich Chilly verboten
			self.forbidden += edge_data.dest
		elif MODE == Mode.EDGES
			new_edge = (self.chilly_loc, edge_data.dest)
			if new_edge in forbidden:
				return None # Hat sich Chilly verboten
			self.forbidden += new_edge
		self.chilly_loc = edge_data.dest
		self.eggs -= edge_data.eggs
		
		return self
		
	
	def can_chilly_reach(self, dests):
		""" Ob Chilly einen Haltepunkt in 'dests' erreichen kann
		
			A*-Algorithmus
			
			Berücksichtigt werden nur diejenigen Verbote, die sich Chilly am
			Anfang dieser Funktion gesetzt hat. Verbote, die sich Chilly auf
			dem Weg zu den Ziel-Haltepunkten setzt, werden NICHT berücksichtigt.
			Wenn diese Funktion also 'False' zurückgibt, gibt es keinen Weg
			von Chilly zu den Ziel-Haltepunkten. Wenn sie dagegen 'True'
			zurückgibt, kann es trotzdem sein, dass es keinen solchen Weg gibt.
			
			dests - eine Menge Knoten aus NODES
			
			Return - False, wenn kein Knoten aus 'dests' erreichbar ist.
		"""
		
		for dest in dests:
			# Gibt zum Haltepunkt 'node' an, wie lang der kürzest bekannte Weg 
			# ist, um von Chillys Standort aus zu 'node' zu gelangen.
			# Für Chillys Standort selbst ist das natürlich 0
			dist_to_reach = {self.chilly_loc: 0}
			
			# Jedes Paar '(dist, node)' nennt die geschätzte Gesamtentfernung 
			# 'dist', um von Chillys Standort über den Haltepunkt 'node' zum 
			# Zielhaltepunkt 'dest' zu gelangen
			# Diese Schätzung darf zu tief liegen, aber nicht zu hoch.
			# Anfangs schätzen wir für Chillys Standort die Gesamtentfernung 0.
			to_be_explored = [(0, self.chilly_loc)]

			while to_be_explored:
				# Wir betrachten von allen noch nicht untersuchten Orten immer
				# diejenigen zuerst, bei dem wir die geringste Gesamtentfernung 
				# vermuten
				(_, current_node) = heappop(to_be_explored)

				if current_node in dests:
					return True # Suche erfolgreich
				
				dist_to_reach_successor = dist_to_reach[current_node] + 1
				for edge_data in NODES[current_node].values():
					successor = edge_data.dest
					if (MODE == Mode.EDGES 
						and (current_node, successor) in self.forbidden):
							continue # Chilly hat sich diesen Rutsch verboten
					elif (MODE == Mode.TILES
						and successor in self.forbidden):
						continue # Chilly hat sich diesen Haltepunkt verboten
					
					if (successor not in dist_to_reach or 
						dist_to_reach_successor < dist_to_reach[successor]):
						# Wir haben einen Pfad zu 'successor' gefunden 
						# bzw. eine besseren als alle bisher bekannten. 
						dist_to_reach[successor] = dist_to_reach_successor
						estimate_for_total_path = \
							dist_to_reach_successor + NODE_DIST_ESTIMATES[successor][dest]
						heappush(to_be_explored, (estimate_for_total_path, successor))

		return False  # Suche fehlgeschlagen


	def is_dead_end(self)
		""" Ob dieser Zwischenstand eine Sackgasse ist
		
			Die aufgeführten Tests ignorieren alle, dass sich Chilly bei seinen Wegen
			laufend weitere Rutsche verbietet. Diejenigen Verbote, die sich Chilly jedoch
			im jetzigen Zwischenstand schon verboten _hat_, die werden berücksichtigt.
		
			Return - True, dann wenn dieser Zwischenstand garantiert nicht zu einem gültigen
					 Endstand führen kann.
		"""

		eggs_left = len(self.eggs)
		if (eggs_left == 0):
			# Chilly muss heraus können. Mehr ist nicht zu testen
			return not self.can_chilly_reach({ EXIT_LOC }):
		
		# Chilly muss jedes verbliebene Ei erreichen können.
		for egg in self.eggs:
			if not self.can_chilly_reach(EGG_SOURCES[egg])
				return True
				
		# Eine Kopie, die ich modifizieren kann, ohne 'self' zu überschreiben
		copy = self.deepcopy()
		
		# Chilly muss von jedem verbliebenen Ei aus zum Ausgang können.
		for egg in self.eggs:
			copy.chilly_pos = EGG_DESTS[egg]
			if not copy.can_chilly_reach({ EXIT_LOC })
				return True
		
		if (eggs_left <= 1)
			# Mehr wüsste ich nicht, was getestet werden kann.
			return False
			
		# Es sind also noch mindestens 2 Eier einzusammeln.
		# Alle möglichen Kombinationen will ich nicht ausprobieren.
		# Vertretungsweise nehme ich die beiden verbliebenen Eier,
		# die am meisten voneinander entfernt sind, und teste, 
		# ob Chilly von einem Ei zum anderen findet
		
		# Bestimme die beiden Eier
		(best_dist, best_pair) = (-1, None)
		for egg1 in eggs:
			for egg2 in eggs:
				dist = EGG_DISTANCES[egg1][egg2]
				if (dist > best_dist):
					(best_dist, best_pair) = (dist, (egg1, egg2))
		
		# Kann Chilly von einem Ei zum anderen?
		second_egg_reachable = False
		for (egg1, egg2) in [ best_pair, best_pair[::-1] ]:
			for node in EGG_DESTS[egg1]:
				copy.chilly_loc = node
				if copy.can_chilly_reach(EGG_SOURCES[egg2])
					second_egg_reachable = True
					break
			if second_egg_reachable:
				break
		return not second_egg_reachable


class SlideData:
	""" Eigenschaften der Kante im Graph der Haltepunkte """
	
	dest: None # Zu welchem Haltepunkt die Kante führt
	eggs: None # Eier, die auf dem Weg eingesammelt werden
	
	def __init__(dest, dir, eggs = set()):
		self.dest = dest
		self.eggs = eggs


	def __str__(self):
		return f"SlideData(dest = {self.dest}, eggs = {self.eggs})"


	def print(self):
		""" Ausdruck des Objekts """
		
		print(f"SlideData(dest = {self.dest},")
		print(f"         eggs = {self.eggs})")
		
################################################################################

def board_one_step(coo_x, coo_y, dir):
	""" Chilly 1 Feld weit in die übergebene Richtung ziehen
		
		dir - 	 Eine Richtung, in die Chilly gezogen werden soll
		Return - None, 							wenn der Schritt unmöglich ist
				 (coo_x, coo_y, eggs, do_halt), in allen anderen Fällen
					coo_x, coo_y 	- Chillys neue Koordinaten
					eggs			- die hier liegenden Eier
					do_halt 		- Ob ein Rutsch hiermit beendet ist
	"""
	
	# Chillys neuen Standort bestimmen
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
	
	eggs = set()
	if (coo_x, coo_y) in EGGS
		eggs += (coo_x, coo_y)
	
	if (self.chilly_loc) == EXIT_LOC:
		return (coo_x, coo_y, eggs, True) # Endlage erreicht
	
	# Chilly durchs Portal schicken, wenn er draufsteht
	try:
		(coo_x, coo_y) = PORTALS[(coo_x, coo_y)]
	except KeyError:
		return (coo_x, coo_y, eggs, False)	# Kein Portal
		
	if (coo_x, coo_y) in EGGS
		eggs += (coo_x, coo_y)
	return (coo_x, coo_y, eggs, True) # Portalrutsch


def board_slide(coo_x, coo_y, dir):
	""" Chilly in die übergebene Richtung rutschen
	
		Chilly kommt dann also auf einem Haltepunkt zum Stehen.
		(coo_x, coo_y) 	- Chillys Standort
		dir - Eine Richtung, in die Chilly gezogen werden soll
		Return - None, 						wenn der Rutsch unmöglich ist
				 (coo_x, coo_y, collected), in allen anderen Fällen
					- (coo_x, coo_y) - Chillys neuer Standort
					- collected		 - Menge der eingesammelten Eier
"""
		
		# Erster Schritt
		outcome = board_one_step(coo_x, coo_y, dir)
		if outcome is None:
			return None # Dieser Rutsch war nicht möglich
		(coo_x, coo_y, collected , do_halt) = outcome
		
		# Weitere Schritte in die gleiche Richtung
		while not do_halt:
			outcome = board_one_step(coo_x, coo_y, dir)
			if outcome is None: # geht nicht
				break
			(coo_x, coo_y, eggs, do_halt) = outcome
			collected += eggs
		
		return (coo_x, coo_y, collected)
	

def construct_graph():
	""" Den Graph der prinzipiell erreichbaren Haltepunkte aufbauen
	
		'nodes[A][dir] == SlideData(B, eggs)', das bedeutet: 
		Von Haltepunkt 'A' aus kann man in Richtung 'dir' direkt zu 
		Haltepunkt 'B' rutschen. Hierbei begegnet man den Eiern in
		'eggs'. Ob sich Chilly hierbei einen Rutsch "verboten" hat,
		wird in diesem Graphen außer Acht gelassen.
		
		Return - Graph der Haltepunkte
	"""

	# Anfangs bekannt ist der Zielpunkt des Spielbretts.
	# Von dort aus geht es nur hinaus, es gibt also keine abgehenden Kanten
	nodes = { EXIT_LOC: dict() }
	
	# Liste der Haltepunkte, die noch untersucht werden müssen
	unexplored = [ CHILLY_LOC ]
	
	while unexplored:
		node = unexplored.pop();
		if not node in nodes:
				nodes[node] = dict()
			
		for dir in Dir:
			# Auf dem Spielbrett in Richtung 'dir' rutschen
			outcome = board_slide(*node, dir)
			if outcome is None:
				continue # In diese Richtung kann nicht gerutscht werden
			(coo_x, coo_y, eggs) = outcome
			nodes[node][dir] = SlideData(dest = (coo_x, coo_y), eggs = eggs)
			if not dest in nodes:
				# Neuer Haltepunkt gefunden. 
				# Dieser Haltepunkt muss noch untersucht werden.
				unexplored += dest
			for egg in eggs:
				if not egg in egg_sources:
					egg_sources[egg] = set()
				egg_sources[egg] += dest
				if not egg in egg_dests:
					egg_dests[egg] = set()
				egg_dests[egg] += dest
				
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
	
	# Haltepunkte, die noch untersucht werden müssen, geordnet nach 
	# bisher bekannter kürzester Entfernung vom Startpunkt
	# Anfangs ist das nur der Startpunkt
	unexplored = [(0, start)]
	
	while unexplored:
		(current_distance, current_node) = heappop(unexplored)
		
		if current_distance > node_distances[current_node]:
			# Ein kürzerer Weg hierher ist schon bekannt,
			# also brauchen wir diesen nicht weiter zu verfolgen
			continue 
		
		# Entfernung vom Startpunkt, wenn wir über den aktuellen 
		# Haltepunkt zu einem seiner Nachfolger gehen 
		new_distance = current_distance + 1
		for edge_data in NODES[current_node]:
			successor = edge_data.dest
			if new_distance < node_distances[successor]:
				# Aktualisiere die bekannte kürzeste Entfernung
				node_distances[successor] = new_distance
				# Diesen Nachfolger müssen wir noch untersuchen
				heappush(unexplored, (new_distance, successor))
	
	return node_distances


def calc_dist_estimates()
	""" Schätzwerte für den Abstand zu Haltepunkten und Eiern berechnen
	
		Die Schätzwerte wären exakt ohne dasjenige, was sich Chilly 
		verbietet - so aber UNTERschätzen sie die tatsächlichen Abstände
	"""
	
	node_dist_estimates = dict()
	
	for node in NODES
		node_dist_estimates[node] = dijkstra(node)
	return node_dist_estimates


def calc_egg_distances():
	""" Berechne, wie weit Eier auseinander liegen """
	
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
					if NODE_DIST_ESTIMATES[node_from][node_to] < best_dist:
						best_dist = NODE_DIST_ESTIMATES[node_from][node_to]
			egg_dists[egg_from][egg_to] = best_dist
			
	return egg_dists


def search_solution():
	""" Systematisch nach Rutschfolgen suchen, die Chilly zum Ausgang führen
	
		Breitensuche über die Anzahl der Rutsche der jew. Folge
	
		Return - None, wenn es keine solche Rutschfolge gibt
		       - die längste gefundene Rutschfolge, in allen anderen Fällen 
	"""
	
	# Eine Zeichenkette, die angibt, wie man zu einem "gewinnenden" Endstand kommt.
	best_winner_so_far = None
	
	# Anfangsstand. Zum Aufbau, siehe die Klassendefinition von 'State'
	init_state = State(CHILLY_LOC, set(), EGGS, "")
	
	with SpooledTemporaryFile(max_size=2**30 - 1, mode='w+b', dir="G:\\Temp\\") as fp1:
		with SpooledTemporaryFile(max_size=2**30 - 1, mode='w+b', dir="G:\\Temp\\") as fp2:
			fp_in = fp1
			fp_out = fp2
			
			# Erster abzuarbeitender Zwischenstand ist der Anfangsstand
			try:
				pickle.dump(init_state, fp_out) 
			except OSError as e:
				# Datei-Überlauf, jetzt schon?! Weitermachen zwecklos
				exit(f"Fatal: 'pickle.dump()' scheiterte: {e}")
						
			# Im Folgenden wird die Datei 'fp_in' immer wieder durchlaufen
			# und die Zwischenstände, die in ihr enthalten sind, abgearbeitet.
			# Alle Zwischenstände, die hierbei neu gefunden werden,
			# werden in die Datei 'fp_out' geschrieben. 
			# Wenn die Datei 'fp_in' jeweils vollständig durchlaufen ist 
			# und sich herausstellt, dass Zwischenstände in 'fp_out' stehen
			# dann werden die Rollen von 'fp_in' und 'fp_out' getauscht und
			# die (jetzige) Datei 'fp_out' gelöscht.
			# Das geht solange, bis alle Zustände vollständig abgearbeitet
			# und hierbei keine neuen Zustände gefunden worden sind
			slides = 0 # Wieviele Rutsche die derzeitigen Zwischenstände umfassen
			states = 0 # Wieviele Zwischenstände in der aktuellen Datei waren
			rejected = 0 # Wieviele Zwischenstände als Sackgassen verworfen wurden
			while True: 
				try: 
					current_state = pickle.load(fp_in)
				except EOFError:
					# Ggf. gepufferte Ausgaben wegschreiben
					fp_out.flush()
					if fp_out.tell() == 0:
						# Fertig: es gibt keine abzuarbeitende Zwischenstände mehr
						fp_in = None
						fp_out = None
						break
					(fp_out, fp_in) = (fp_in, fp_out)
					fp_in.seek(0)
					fp_out.seek(0)
					fp_out.truncate(0)
					logmsg = f"# slides: {slides}, states: {states}, rejected: {rejected}, winner: {best_winner_so_far}"
					with open("c:\\temp\\log.txt", "a") as log:
						print(logmsg, file = log)
					print(logmsg)
					slides += 1
					states = 0
					rejected = 0
					continue
					
				if current_state.chilly_loc == EXIT_LOC:
					# Dieser Zwischenstand ist ein Endstand.
					# Nur Endstände, bei denen alle Eier eingesammelt sind, zählen.
					if not current_state.eggs:
						best_winner_so_far = current_state.access_path
					continue
				
				# Beim Durchkämmen von Suchräumen ist es entscheidend wichtig,
				# Zwischenstände so früh wie möglich auszuscheiden, 
				# sobald klar und sicher ist, dass sie nicht mehr zum Ziel 
				# führen können. Ansonsten verschwendet das Programm viel 
				# Aufwand mit dem Ausforschen von Sackgassen.
				if current_state.is_dead_end():
					rejected += 1
					continue		
						
				# Alle Rutschmöglichkeiten von diesem Zwischenstand aus durchgehen 
				for dir in Dir:
					# Eine schlichte Zuweisung des aktuellen Zwischenstands
					# an den neuen reicht hier nicht.
					# Der neue Zwischenstand muss eine _Kopie_ des aktuellen sein,
					# weil 'slide()' den neuen Zwischenstand verändert
					# und der aktuelle dabei _nicht_ mitverändert werden darf.
					new_state = current_state.deepcopy();
					result = new_state.slide(dir);
					if result is None: 
						continue # In diese Richtung zu rutschen, ist nicht möglich
						
					# Dieser Zwischenstand ist neu, wir können ihn nicht schon
					# mal angetroffen haben. Denn wir arbeiten alle Zwischenstände
					# nacheinander ab, die durch eine gewisse Länge an Rutschen 
					# erreichbar sind. Der neue Zwischenstand hat einen Rutsch mehr.
					states += 1
					try:
						pickle.dump(new_state, fp_out)
					except OSError as e:
						# Die Datei zum Aufnehmen der noch zu bearbeitenden
						# Zwischenstände ist übergelaufen. Weitermachen zwecklos
						exit(f"Fatal: 'pickle.dump()' scheiterte: {e}")
		
	# Alle Zwischenstände sind jetzt abgearbeitet.
	return best_winner_so_far
	
################################################################################
################################################################################
# Hauptprogramm

# Je nach Aufgabe die zugehörige Funktion entkommentieren:
#init_game1()	# Level 1
#init_game2()	# Level 2
init_game3()	# Level 3

(NODES, EGG_SOURCES, EGG_DESTS) = construct_graph()
print_board(EGGS, CHILLY_LOC)
breakpoint()

NODE_DIST_ESTIMATES = calc_dist_estimates()
EGG_DISTANCES = calc_egg_distances()

SOLUTION = search_solution()

if SOLUTION is None:
	print("🐧 Chilly schmollt. Er konnte keine Lösung bestimmen")
else:
	print(f"🐧 Chilly fand eine Lösung mit {len(SOLUTION)} Rutschen.");
	print(f"Sie lautet: {SOLUTION}")
	