Der Solver, den ich für das Osterrätsel 2025 der c't programmiert habe.

Der Solver geht die Zwischenstände systematisch durch, die Chilly auf seinem Weg vom Start zum Ziel durchrutscht. 
Die Zwischenstände werden nach einem gemischten Kriterium bewertet, in das die bisher vollzogenen Rutsche positiv 
und die Anzahl der schon gesammelten Eier negativ eingeht - da Chilly zwischen den Eier-Einsammlungen ja möglichst 
viel rutschen soll. Immer wieder arbeitet der Solver den jeweils bestbewerteten Zwischenstand aus und bestimmt 
dabei alle Zwischenstände, die hieraus entstehen können.

Für jeden neu gefundenen Zwischenstand versucht der Solver sofort zu erkennen, ob es eine Sackgasse ist, d.h. ob 
Chilly ab diesem Zwischenstand keine Chance mehr hat, zu einem gültigen Ende zu kommen. Sicher erkannte Sackgassen 
scheidet der Solver aus und verfolgt sie nicht weiter. Wenn der Solver dagegen einen Endstand findet und dieser 
mit mehr vollzogenen Rutschen einhergeht als die bisher gefundenen Endstände, schreibt er ihn in eine Datei. 
Während des Laufs kann man also jederzeit in dieser Datei lesen, welchen längstmöglichen Endstand der Solver schon 
gefunden hat.

Vor dem eigentlichen Abarbeiten der Zwischenstände formt der Solver das Spielbrett in einen Graphen um, in dem 
Haltepunkte (Punkte, auf denen Chilly am Ende eines Rutsches zum Halten kommen kann) die Knoten bilden und Rutsche 
die Kanten. Jeder Rutsch ist mit der Richtung beschriftet, die Chilly nehmen muss, um ihn auszulösen, sowie mit 
den Eiern, die auf dem Rutsch liegen.

Für die o.g. Sackgassen-Erkennung wird die Auskunft benötigt, wie weit zwei Haltepunkte bzw. zwei Eier auseinander 
liegen, in Rutschen gerechnet. Dies ermittelt der Solver ebenfalls vorab, vor dem eigentlichen Abarbeiten der 
Zwischenstände.

Den Solver habe ich auf einem inzwischen ca. 15 Jahre alten Rechner ausgeführt, der aus einem c't-Selbstbau-Projekt 
entstanden ist. Versuche, den Solver zu parallelisieren, habe ich nicht unternommen. Das ist nicht so schlimm, wie 
es vielleicht wirkt. Denn jeder Zwischenstand führt beim Ausarbeiten im Schnitt zu mehr als einem Folge-Zwischenstand, 
und so schlägt bei der Suche eine exponentielle Explosion zu, die schnellere Rechenleistungen extrem schnell 
zunichte macht. Alles kommt also darauf an, dass der Solver möglichst früh einen "schönen" Endstand findet, und dass 
der Solver Sackgassen so früh wie möglich erkennt, damit jeder Zwischenstand _möglichst wenige_ Folge-Zwischenstände 
zur Folge hat. Auf die Rechnergeschwindigkeit kommt es nicht so sehr an. 

Das "Hauptprogramm" zum Programm steht am Ende der Datei.
