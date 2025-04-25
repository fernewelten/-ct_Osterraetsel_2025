#Solver für das c't Osterrätsel April 2025

import pdb # Anweisung ist nur zum Debuggen nötig
from enum import Enum, auto

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
		
	Tiles = auto() # Nicht zweimal auf dem gleichen Feld zum Stehen kommen
	Edges = auto() # Nicht zweimal entlang der gleichen Kante laufen

MODE = None 	# Zugregel
BOARD = None	# Start-Spielbrett
CHILLY_LOC = None 	# Chillys Start-Standort
EGGS = None		# Standorte der Eier auf dem Start-Spielbrett
PORTALS = None 	# Von wo nach wo die Portale führen

################################################################################
# Initialisierungen

def init_game1():
	# Chillys Zugregel
	global MODE
	MODE = Mode.Edges

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
	global EXIT
	EXIT = (0, 1)
	
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
	MODE = Mode.Tiles

	global BOARD
	#        Y →  0      1      2      3      4      5     			  X X
	#        Y →    6      7      8      9      10     11  	 		  ↓ ↓
	BOARD = [   [ False, False, False, False, True,  True,         #  0
					False, True,  False, False, True,  False,  ],  #    0	
				[ True,  True,  False, True,  True,  False,        #  1
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
	MODE = Mode.Edges
	global BOARD
	BOARD[11][8] = True

################################################################################

def board2str(eggs = set(), chilly_loc = (-1, -1)):
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
				output += "#"
			elif (x, y) in PORTALS:
				output += "∆"
			elif (x, y) in eggs:
				output += "O"
			elif (x, y) == EXIT:
				output += "^"
			else:
				output += "_"
			output += "C" if chilly_loc == (x, y) else "_"
			output += " "
		output += f" ← {y}\n"
	print(output)
	return 

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
		- alle Züge bzw. Orte, die Chilly wegen voriger Züge verboten sind
		. die Lage der noch nicht eingesammelten Eier.
	"""
	
	chilly_loc = None	# Chillys Standort
	forbidden = set()	# Züge bzw. Felder, die Chilly nicht mehr betreten darf
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
		""" Chilly 1 Schritt weit in die übergebene Richtung ziehen
			
			dir - 	 Eine Richtung, in die Chilly gezogen werden soll
			Return - None, wenn der Zug nicht erlaubt oder möglich ist
			       - True, wenn Chilly stoppen muss
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
		
		if (self.chilly_loc) == EXIT:
			return True 
		
		# Chilly durchs Portal schicken, wenn dies ansteht 
		try:
			self.chilly_loc = PORTALS[self.chilly_loc]
		except KeyError:
			return False	# Kein Portalzug
		return True	# Portalzug
		
			
	def move(self, dir):
		""" Chilly so weit wie möglich in die übergebene Richtung ziehen
			
			dir - Eine Richtung, in die Chilly gezogen werden soll
			Return - None, wenn der Zug nicht möglich ist
			True, in allen anderen Fällen
		"""
		
		# Erster Schritt
		start_loc = self.chilly_loc
		outcome = self.one_step(dir)
		if outcome is None:
			return None # Dieser Zug war nicht möglich
		
		# Weitere Schritte in die gleiche Richtung
		while outcome == False:
			outcome = self.one_step(dir)
			
		if MODE == Mode.Tiles: 
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
		elif MODE == Mode.Edges: 
			# Chilly ist also von 'start_loc' nach 'self.chilly_loc' gezogen.
			# Diesen Weg darf Chilly vorher noch nicht gezogen sein
			current_edge = (start_loc, self.chilly_loc)
			if current_edge in self.forbidden:
				return None
			# Diesen Weg will Chilly nie wieder nehmen
			self.forbidden.add(current_edge)
		return False

################################################################################


def search_solution():
	""" Systematisch nach nach längsten Zugfolgen suchen
	
		Return - None, wenn es keine Zugfolge gibt, die alle Eier einsammelt
		       - die längste gefundene Zugfolge, in allen anderen Fällen 
	"""
	
	# Anfangsstand. Zum Aufbau, siehe die Klassendefinition
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
		# Länge des bisher längster Wegs zum aktuellen Zwischenstand
		current_move_count = state_data[current_state_key][0]
		
		if current_state.chilly_loc == EXIT:
			# Dieser Zwischenstand ist ein Endstand 
			if current_state.eggs:
				# Keine Lösung: Nicht alle Eier eingesammelt
				continue
			if current_move_count > best_winner_move_count_so_far:
				# Bessere Zugfolge gefunden als bisher bekannt.
				best_winner_so_far = current_state
				best_winner_move_count_so_far = current_move_count
			continue
		
		# Alle Zugmöglichkeiten von diesem Zwischenstand aus durchgehen 
		new_move_count = current_move_count + 1
		for dir in [Dir.R, Dir.D, Dir.L, Dir.U]:
			# Eine schlichte Zuweisung des aktuellen Zwischenstands
			# reicht hier nicht.
			# Der neue Zwischenstand muss eine _Kopie_ des aktuellen sein,
			# weil move() den neuen Zwischenstand verändert
			# und der aktuelle dabei _nicht_ mitverändert werden darf.
			new_state = current_state.deepcopy();
			result = new_state.move(dir);
			if result is None: 
				continue # In diese Richtung zu ziehen, ist nicht möglich
			
			# Bereits gefundene Info über den neuen Zwischenstand holen
			new_state_key = new_state.to_dict_key();
			try:
				(cached_count, cached_dir, cached_state) = \
					state_data[new_state_key]
			except KeyError:
				# Diesen Zwischenstand haben wir bis jetzt noch nie gesehen.
				# Den 'bisherigen' move count auf einen so kleinen Wert setzen,
				# dass der neu berechnete auf jeden Fall höher sein muss 
				(cached_count, cached_dir, cached_state) = (-1, None, None)
				# Wir werden den Zwischenstand später untersuchen müssen.
				unexplored.append(new_state)
			
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
		
	return moves
	
################################################################################
################################################################################
# Hauptprogramm

# Je nach Aufgabe die zugehörige Funktion entkommentieren:
init_game1()	# Level 1
#init_game2()	# Level 2
#init_game3()	# Level 3

board2str(EGGS, CHILLY_LOC)

solution = search_solution();

if solution is None:
	print("🐧 Chilly schmollt. Er konnte keine Lösung bestimmen")
else:
	move_count = len(solution)
	print(f"🐧 Chilly fand eine Lösung mit {move_count} Zügen.");
	print(f"Sie lautet: {solution}")
	