#Solver für das c't Osterrätsel April 2025

import pdb # Anweisung ist nur zum Debuggen nötig
from enum import Enum, auto
import heapq

# Zugrichtungen
class Dir(Enum):
	def __str__(self):
		""" Druckansicht ist der jeweilige reine Name """
		return f"{self.name}"
		
	# Die Richtungen sind im Uhrzeigersinn geordnet
	R = auto() # →
	D = auto() # ↓
	L = auto() # ←
	U = auto() # ↑
	
# Nach welcher Regel Chilly zieht. 
class Mode(Enum):
	def __str__(self):
		""" Druckansicht ist der jeweilige Name """
		return f"{self.name}"
		
	NONE = 0
	TILES = auto() # Nicht zweimal auf dem gleichen Feld zum Stehen kommen
	EDGES = auto() # Nicht zweimal entlang der gleichen Kante laufen


MODE = None 	# Zugregel
BOARD = None	# Start-Spielbrett
CHILLY_LOC = None 	# Chillys Start-Standort
EGGS = None		# Standorte der Eier auf dem Start-Spielbrett
PORTALS = None 	# Von wo nach wo die Portale führen
GRAPH = None	# Graph der prinzipiell erreichbaren Felder auf dem Spielbrett

################################################################################
# Initialisierungen

def init_game1():
	# Chillys Zugregel
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
	# Wenn Chilly zum Beispiel auf (0, 3) zieht, landet er auf (3, 0)
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
			elif (not GRAPH is None) and (x, y) in GRAPH:
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
	""" Zwischenstand auf der Suche nach einer längsten Zugfolge zum Einsammeln aller Eier
	
		Ich suche eine Zugfolge, die von Chillys Startposition ausgeht
		und eine Position erreicht, in der Chilly alle Eier eingesammelt hat.
		Hierbei möchte ich jeden Zwischenstand nur einmal nachhalten. 
		Als „Zwischenstand“ bezeichne ich hierbei eine Situation, die
		Chilly genau dieselben Möglichkeiten der Weitersuche bietet, 
		egal wann und wie Chilly diese Situation erreicht.
		Da sich das reine Spielbrett nicht verändert, umfasst ein solcher
		Zwischenstand die folgenden Daten:
		- Chillys Standort,
		- alle Züge bzw. Orte, die sich Chilly wegen voriger Züge verbietet
		. die Lage der noch nicht eingesammelten Eier.
	"""
	
	chilly_loc = None	# Chillys Standort
	forbidden = set()	# Züge bzw. Felder, die sich Chilly verbietet
	eggs = set()		# Lage der noch nicht eingesammelten Eier
	
	def __init__(self, chilly_loc, forbidden, eggs):
		self.chilly_loc = chilly_loc
		self.forbidden = forbidden
		self.eggs = eggs


	def __str__(self):
		return f"State(chilly_loc = {self.chilly_loc}, forbidden = {self.forbidden}, eggs = {self.eggs})"


	def print(self):
		""" Ausdruck des Objekts """
		
		print(f"State(chilly_loc = {self.chilly_loc},")
		print(f"      forbidden = {self.forbidden},")
		print(f"      eggs = {self.eggs})")

	
	def to_dict_key(self):
		""" Den Zwischenstand so konvertieren, dass er Lexikonschlüssel sein kann.
	
			Klassen können keine Lexikonschlüssel sein.
			Tupel, die Tupel und/oder 'frozenset's enthalten, können das dahingegen.
			
			Return - der konvertierte Zwischenstand.
		"""
		return (self.chilly_loc, frozenset(self.forbidden), frozenset(self.eggs))
		
	
	def deepcopy(self):
		""" Einen Zwischenstand in allen Teilen kopieren (sog. 'tiefe' Kopie)
	
			Return - die Kopie
		"""
		return State(self.chilly_loc, self.forbidden.copy(), self.eggs.copy())

	
	def one_step(self, dir):
		""" Chilly 1 Feld weit in die übergebene Richtung ziehen
			
			dir - 	 Eine Richtung, in die Chilly gezogen werden soll
			Return - None, wenn der Zug nicht erlaubt oder möglich ist
			       - True, wenn Chilly anschließend stoppen muss
			       - False, in allen anderen Fällen
		"""
		
		# Chillys neuen Standort bestimmen
		(current_x, current_y) = self.chilly_loc
		match dir:
			case Dir.R:
				(new_x, new_y) = (current_x + 1, current_y) 
			case Dir.D:
				(new_x, new_y) = (current_x, current_y + 1) 
			case Dir.L:
				(new_x, new_y) = (current_x - 1, current_y) 
			case Dir.U:
				(new_x, new_y) = (current_x, current_y - 1)
		
		# Wenn Chilly auf der einen Seite vom Spielbrett fällt,
		# kommt er auf der anderen Seite wieder herauf.
		if new_x < 0:
			new_x += X_DIM
		elif new_x >= X_DIM:
			new_x -= X_DIM
		if new_y < 0:
			new_y += Y_DIM
		elif new_y >= Y_DIM:
			new_y -= Y_DIM
			
		if BOARD[new_x][new_y]:
			return None # Chilly kann nicht auf dieses Feld
		self.chilly_loc = (new_x, new_y)
				
		# Ei einsammeln, wenn vorhanden
		self.eggs.discard(self.chilly_loc)
		
		if (self.chilly_loc) == EXIT_LOC:
			return True # Endlage erreicht
		
		# Chilly durchs Portal schicken, wenn dies ansteht 
		try:
			self.chilly_loc = PORTALS[self.chilly_loc]
		except KeyError:
			return False	# Kein Portalzug
		return True	# Portalzug
		
			
	def move(self, dir, mode = MODE):
		""" Chilly so weit wie möglich in die übergebene Richtung ziehen
		
			Chilly kommt dann also auf einem Haltepunkt zum Stehen.
			
			dir - Eine Richtung, in die Chilly gezogen werden soll
			Return - None, wenn der Zug nicht möglich ist
				   - True, in allen anderen Fällen
		"""
		
		# Erster Schritt
		start_loc = self.chilly_loc
		outcome = self.one_step(dir)
		if outcome is None:
			return None # Dieser Zug war nicht möglich
		
		# Weitere Schritte in die gleiche Richtung
		while outcome == False:
			outcome = self.one_step(dir)
			
		if MODE == Mode.TILES: 
			if outcome == True:
				# Chilly ist durch ein Portal gegangen. 
				# Dann ist weder der Portal-Ursprung gesperrt 
				# (weil das kein Haltepunkt ist laut Aufgabenstellung) 
				# noch der Zielpunkt des Portals
				# (weil Chilly nicht ihn, sondern den Ursprung "ansteuert")
				pass
			elif self.chilly_loc in self.forbidden:
				return None # Hier war Chilly schon
			else:
				# Hierhin will Chilly nie wieder ziehen
				self.forbidden.add(self.chilly_loc)
		elif MODE == Mode.EDGES: 
			# Chilly ist also von 'start_loc' nach 'self.chilly_loc' gezogen.
			# Diesen Weg darf Chilly vorher noch nicht gezogen sein
			current_edge = (start_loc, self.chilly_loc)
			if current_edge in self.forbidden:
				return None
			# Diesen Weg will Chilly nie wieder nehmen
			self.forbidden.add(current_edge)
		return False


	def get_near_nodes(self, loc):
		""" Haltepunkte, die von 'loc' aus in gerader Linie mit einem Zug erreichbar sind
		"""
		
		# Schleifenkörper, wird für verschiedene Schleifen durchlaufen, s.u.
		def do_loop_body(x, y):
			nonlocal nodes
			if BOARD[x][y]:
				return True	# Feld kann nicht betreten werden, Schleifenabbruch
			if not (x, y) in GRAPH:
				return False # Kein Haltepunkt, Weiter
			if MODE == Mode.TILES and (x,y) in self.forbidden: 
				return False # Verbotener Haltepunkt, Weiter
			nodes.add((x, y))
			return False
		
		# Die nahe gelegenen Haltepunkte sammeln
		nodes = set()
		
		(loc_x, loc_y) = loc
		for x in range(loc_x, X_DIM):
			if do_loop_body(x, loc_y):
				break # Erstes nicht betretbare Feld erreicht
		for x in range(loc_x - 1, -1, -1):
			if do_loop_body(x, loc_y):
				break
		for y in range(loc_y, Y_DIM):
			if do_loop_body(loc_x, y):
				break
		for y in range(loc_y - 1, -1, -1):
			if do_loop_body(loc_x, y):
				break
		return nodes
			

	def does_path_exist(self, to_nodes):
		""" Ob es einen Pfad von Chillys Standort zu den Haltepunkten 'to_nodes' gibt
		
			Dijkstras Algo
			
			Es werden nur diejenigen verbotenen Züge berücksichtigt, die
			schon am Anfang der Routine verboten waren. Wenn die Routine also
			'False' zurückgibt, dann stimmt das, aber wenn sie 'True'
			zurückgibt, kann es in Wirklichkeit doch keinen solchen Pfad geben.
			Diese Unschärfe nehme ich inkauf.
			
			from-node - Haltepunkt aus 'GRAPH'
			to-nodes - Menge von Haltepunkteb 
			Return - 'False' dann, wenn es keinen solchen Pfad gibt
		"""
		
		# Wenn es keine Ziel-Standorte gibt, sind sie alle erreichbar.
		if not to_nodes:
			return True
			
		# Jedem Haltepunkt die bisher bekannte kürzeste Distanz vom 
		# Startpunkt zuweisen. Die Distanz wird in Zügen gerechnet
		# Anfangs ist das beim Startpunkt 0, bei allen anderen 'unendlich'
		distances = { node: float('inf') for node in GRAPH }
		distances[self.chilly_loc] = 0
		
		# Haltepunkte, die noch untersucht werden müssen, geordnet nach 
		# bisher bekannter kürzester Distanz vom Startpunkt
		# Anfangs ist das nur der Startpunkt
		unexplored = [(0, self.chilly_loc)]
		
		while unexplored:
			(current_distance, current_node) = heapq.heappop(unexplored)
			
			if current_node in to_nodes:
				return True # Ein Zielhaltepunkt ist erreicht, also erreichbar
			
			if current_distance > distances[current_node]:
				# Ein kürzerer Pfad hierher ist schon bekannt,
				# also brauchen wir diesen nicht weiter zu verfolgen
				continue 
			
			# Distanz vom Startpunkt, wenn wir über den aktuellen 
			# Haltepunkt zu einem seiner Nachfolger gehen 
			new_distance = current_distance + 1
			for successor in GRAPH[current_node]:
				if (MODE == Mode.EDGES 
					and (current_node, successor) in self.forbidden):
					continue # Chilly hat sich diesen Rutsch verboten
				elif (MODE == Mode.TILES
					and successor in self.forbidden):
					continue # Chilly hat sich diesen Nachfolger verboten
				
				if new_distance >= distances[successor]:
					# Über aktuellen Haltepunkt zu gehen, ist nicht kürzer 
					# als der bisher bekannte kürzeste Weg
					continue
				
				# Aktualisiere die bekannte kürzeste Distanz
				distances[successor] = new_distance
				# Diesen Nachfolger müssen wir noch untersuchen
				heapq.heappush(unexplored, (new_distance, successor))
		
		# Alle Möglichkeiten erschöpft, einen Pfad gibt es anscheinend nicht.
		return False

################################################################################

def construct_graph():
	""" Den Graph der prinzipiell erreichbaren Haltepunkte aufbauen
	
		'B in graph[A]', das bedeutet: Von Haltepunkt A aus
		kann man direkt (in _einem_ Zug) zu Haltepunkt B gelangen
		Ob sich Chilly hierbei einen Zug "verboten" hat, wird in diesem
		Graphen außer Acht gelassen.
		
		>==> In dieser Routine entspricht jeder Zwischenstand einem Haltepunkt

		Return - Graph der Haltepunkte
	"""
	
	# Anfangs bekannt ist der Anfangs- und Zielpunkt des Spielbretts 
	graph = { CHILLY_LOC: set(), EXIT_LOC: set() }
	
	# Anfangsstand. Zum Aufbau, siehe die Klassendefinition von 'State'
	# Anfangs müssen wir den Anfangspunkt des Spielbretts untersuchen
	init_state = State(CHILLY_LOC, set(), set())
	
	# Liste der Zwischenstände, die noch untersucht werden müssen
	unexplored = [ init_state ]
	
	while unexplored:
		current_state = unexplored.pop();
		node = current_state.chilly_loc
		
		if node == EXIT_LOC:
		    continue # von hier aus geht's nur raus
		
		# Alle Zugmöglichkeiten von diesem Zwischenstand aus durchgehen 
		for dir in Dir:
			# Eine schlichte Zuweisung des aktuellen Zwischenstands
			# an den neuen reicht hier nicht.
			# Der neue Zwischenstand muss eine _Kopie_ des aktuellen sein,
			# weil 'move()' den neuen Zwischenstand verändert
			# und der aktuelle dabei _nicht_ mitverändert werden darf.
			new_state = current_state.deepcopy();
			result = new_state.move(dir, Mode.NONE);
			if result is None: 
				continue # In diese Richtung zu ziehen, ist nicht möglich
			new_node = new_state.chilly_loc
			
			if not new_node in graph:
				graph[new_node] = set()
				# Diesen Ort kennen wir bisher nicht, wir werden ihn noch 
				# untersuchen müssen
				unexplored.append(new_state)
			
			graph[node].add(new_node)
		
	return graph


def search_solution():
	""" Systematisch nach nach längsten Zugfolgen suchen
	
		Return - None, wenn es keine solche Zugfolge gibt
		       - die längste gefundene Zugfolge, in allen anderen Fällen 
	"""
	
	# Anfangsstand. Zum Aufbau, siehe die Klassendefinition von 'State'
	init_state = State(CHILLY_LOC, set(), EGGS)
	
	# Lexikon der bisher gefundenen Zwischenstände
	# Zu jedem Zwischenstand will ich als Info nachhalten,
	# 	- wie viele Züge der bisher längste Weg hat, der hierhin geführt hat
	# 	- welche Richtung Chilly zuletzt genommen hat, um zu diesem
	#   		Zwischenstand auf dem längsten Weg zu gelangen
	#   - von welchem Zwischenstand Chilly zuletzt kam
	# In diesem Lexikon würden Zwischenstände die Schlüssel der 
	# Einträge bilden, wenn denn Python erlauben würde, dass Objekte 
	# Lexikon-Schlüssel sind. Erlaubt Python aber nicht.
	# Daher wird vor dem Eintragen oder Nachschlagen im Lexikon jeder 
	# Zwischenstand in eine Form gebracht, die ein Lexikon-Schlüssel sein kann.
	state_data = { init_state.to_dict_key() : (0, None, None) }
	
	# Alle noch nicht untersuchten Zwischenstände
	# Am Anfang der Suche ist das nur der Anfangsstand
	unexplored = [ init_state ]
	
	# Der Endstand mit der längsten Anzahl an Zügen
	# Am Anfang der Suche gibt es noch keinen. 
	best_winner_so_far = None
	best_winner_move_count_so_far = -1
	
	while unexplored:
		current_state = unexplored.pop();
		current_state_key = current_state.to_dict_key()
		# Länge des bisher längsten Wegs zum aktuellen Zwischenstand
		current_move_count = state_data[current_state_key][0]
		
		if current_state.chilly_loc == EXIT_LOC:
			# Dieser Zwischenstand ist ein Endstand 
			if current_state.eggs:
				# Keine Lösung: Nicht alle Eier eingesammelt
				continue
			if current_move_count > best_winner_move_count_so_far:
				# Bessere Zugfolge gefunden als bisher bekannt.
				best_winner_so_far = current_state
				best_winner_move_count_so_far = current_move_count
			continue
		
		
		# Generell ist es beim Durchkämmen von Suchräumen wichtig,
		# Zwischenstände so früh wie möglich auszuscheiden, 
		# wenn klar und sicher ist, dass sie nicht mehr zum Ziel 
		# führen können. Ansonsten verschwendet das Programm viel 
		# Aufwand mit dem Ausforschen von Sackgassen.
		# Den aktuellen Zwischenstand können wir ausscheiden, 
		# wenn es keinen Weg mehr von Chilly zum Endpunkt gibt
		if not current_state.does_path_exist({ EXIT_LOC }):
			continue
					
		# Diesen Zwischenstand können wir auch ausscheiden, wenn es
		# keinen Weg von Chilly zu jedem verbliebenen Ei mehr gibt.
		# Eier liegen nicht immer auf Haltepunkten, ersatzweise
		# bestimme ich dann alle Haltepunkte, die vom jeweiligen Ei
		# aus in gerader Linie erreichbar sind. Um das jeweilige Ei 
		# zu erreichen, muss Chilly nämlich einen solchen Haltepunkt
		# passieren. Dieses Ersatzkriterium ist zwar eine Unschärfe, 
		# aber die nehme ich inkauf.
		reached_dead_end = False
		for egg in current_state.eggs:
			near_nodes = ( { egg } if egg in GRAPH 
						   else current_state.get_near_nodes(egg) )
			if not current_state.does_path_exist(near_nodes):
				reached_dead_end = True
				break
		if reached_dead_end:
			continue
				
		# Alle Zugmöglichkeiten von diesem Zwischenstand aus durchgehen 
		new_move_count = current_move_count + 1
		for dir in Dir:
			# Eine schlichte Zuweisung des aktuellen Zwischenstands
			# an den neuen reicht hier nicht.
			# Der neue Zwischenstand muss eine _Kopie_ des aktuellen sein,
			# weil 'move()' den neuen Zwischenstand verändert
			# und der aktuelle dabei _nicht_ mitverändert werden darf.
			new_state = current_state.deepcopy();
			result = new_state.move(dir);
			if result is None: 
				continue # In diese Richtung zu ziehen, ist nicht möglich
			
			# Wie lang war der bisher gefundene längste Weg zum 
			# neuen Zwischenstand
			new_state_key = new_state.to_dict_key();
			try:
				cached_count = 	state_data[new_state_key][0]
			except KeyError:
				# Diesen Zwischenstand haben wir bis jetzt noch nie gesehen.
				# Wir werden ihn später untersuchen müssen.
				unexplored.append(new_state)
				# Die 'bisher bekannte' längste Anzahl Züge auf einen so 
				# kleinen Wert setzen, dass der neu berechnete Wert 
				# auf jeden Fall höher sein muss 
				cached_count = -1
			
			if cached_count < new_move_count:
				state_data[new_state_key] = (new_move_count, dir, current_state_key)
		
	# Alle Zwischenstände sind jetzt abgearbeitet
	if best_winner_so_far is None:
		return None # Es gibt keine Zugfolge zum Ziel
		
	# Die Züge vom Gewinner bis zum Anfangsstand rückverfolgen
	# 'state_data[A] == (_, dir, B)', das bedeutet:
	# Wenn man aus B kommt und in Richtung dir zieht, gelangt man nach A
	state_key = best_winner_so_far.to_dict_key()
	moves = "" # sammelt die Zugrichtungen auf
	while True:
		(count, dir, state_key) = state_data[state_key]
		if count == 0:
			break; # Anfangsstand erreicht
		moves = f"{dir}{moves}"
		(cl, f, e) = state_key
		s = State(cl, f, e)
		reached_dead_end = False
		for egg in s.eggs:
			near_nodes = ( { egg } if egg in GRAPH 
						   else s.get_near_nodes(egg) )
			if not s.does_path_exist(near_nodes):
				reached_dead_end = True
				print (cl, f, e, f"NICHT ERREICHBAR: {egg}")
				break
		
		
	return moves
	
################################################################################
################################################################################
# Hauptprogramm

# Je nach Aufgabe die zugehörige Funktion entkommentieren:
#init_game1()	# Level 1
#init_game2()	# Level 2
init_game3()	# Level 3

breakpoint()
GRAPH = construct_graph()
print_board(EGGS, CHILLY_LOC)
SOLUTION = search_solution()

if SOLUTION is None:
	print("🐧 Chilly schmollt. Er konnte keine Lösung bestimmen")
else:
	print(f"🐧 Chilly fand eine Lösung mit {len(SOLUTION)} Zügen.");
	print(f"Sie lautet: {SOLUTION}")
	