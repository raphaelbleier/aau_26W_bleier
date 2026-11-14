% Please provide the names of your (up to three) group members:
% - Raphael Bleier
% - Fabio Schmickl
% - Devis Mele

% vorabversion nach der session am 11.11., nur task 1 und 2 sind drin
% task 3 und 4 kommen bis zur finalen abgabe, deswegen gibts aktuell noch viele models

% AUXILIARY PREDICATES

% We use the value "-1" to represent that a cloud is assigned to a cell, and the value "1" for a star.

value(-1;1).

% The indexes refer to the rows and columns of a square grid of size "Z".

index(1..Z) :- size(Z).

% IMPLEMENTATION TASKS: Please add rules encoding each of the below conditions.

% (1) Define a predicate "cell(X,Y)" such that the indexes "X" and "Y" refer to an empty cell, which is not occupied by any planet. In the ASP Chef visualization (see below), the "cell(X,Y)" atoms will be indicated by a white background.

% cell = alles im gitter wo kein planet sitzt, die richtung vom planet ist egal deswegen _ _ _
cell(X,Y) :- index(X), index(Y), not planet(X,Y,_,_,_).

% (2) Add choice rules that generate a predicate "assign(X,Y,V)" representing that an empty cell at the indexes "X" and "Y" contains a cloud ("V" is "-1") or a star ("V" is "1"). There must be exactly one cloud and one star per row or column, respectively. Moreover, the same cell cannot contain both a cloud and a star, which should be expressed by an integrity constraint.
% The format of choice rules and integrity constraints is illustrated by the Sudoku encoding that can be viewed here: https://moodle.aau.at/mod/url/view.php?id=1509241

% value(V) aus dem template nutzen, dann reichen zwei choice rules statt vier:
% pro zeile X und pro wert V (wolke -1 / stern 1) genau ein assign, gleiches nochmal pro spalte Y
1 = { assign(X,Y,V) : cell(X,Y) } :- index(X), value(V).
1 = { assign(X,Y,V) : cell(X,Y) } :- index(Y), value(V).

% stern und wolke nicht auf der gleichen zelle
:- assign(X,Y,-1), assign(X,Y,1).

% (3) Starting from facts "planet(X,Y,DX,DY,S)", specifying whether a planet at the indexes "X" and "Y" is dark ("S" is "-1") or illuminated ("S" is "1") in the direction indicated by "DX" and "DY", add rules that define a predicate "reach(X,Y,DX,DY,S,X',Y')" representing visible (empty) cells, which are not covered by any cloud in that direction. Such visible cells at indexes "X' = X + n*DX" and "Y' = Y + n*DY", for some positive integer "n", may be iteratively derived starting from planets (one rule) and then continuing (using a second rule) in case the cell at the indexes "X'" and "Y'" does not contain a cloud. The derived "reach(X,Y,DX,DY,S,X',Y')" atoms will be indicated by red arrows in the ASP Chef visualization (see below).

% TODO task 3: reach/7 vom planet aus starten und weiterlaufen solange keine wolke kommt

% (4) Add any required auxiliary predicate(s) and integrity constraints making sure that dark sides of planets are not illuminated by a star, i.e., "assign(X',Y',1)" must not be true if "reach(X,Y,DX,DY,-1,X',Y')" holds, and some star is visible for illuminated sides, i.e., "assign(X',Y',1)" must be true for some cell such that "reach(X,Y,DX,DY,1,X',Y')" holds.

% TODO task 4: dunkle seiten kein stern sichtbar, helle seiten mind. ein stern

% Once your encoding is complete, you may uncomment the below "#show" statement to restrict the output to atoms of the predicate "assign/3", while auxiliary predicates will then no longer be indicated in the ASP Chef visualization.

% #show assign/3.  -> erst wenn encoding fertig ist, sonst sieht man in asp chef cell/2 nicht

% TEST REPORT

% After completing the encoding, record the number of "Models" and "Conflicts" reported by clingo calls of the form "clingo instanceXX.lp starlight.lp 0 --stats" in the table:
%*
---------------------------------------------
| Instance      | Size | Models | Conflicts |
|--------------------------------------------
| instance01.lp |    4 |        |           |
| instance02.lp |    4 |        |           |
| instance03.lp |    4 |        |           |
| instance04.lp |    4 |        |           |
| instance05.lp |    5 |        |           |
| instance06.lp |    5 |        |           |
| instance07.lp |    6 |        |           |
| instance08.lp |    6 |        |           |
| instance09.lp |    7 |        |           |
| instance10.lp |    7 |        |           |
| instance11.lp |    8 |        |           |
| instance12.lp |    8 |        |           |
| instance13.lp |    9 |        |           |
| instance14.lp |    9 |        |           |
---------------------------------------------
*%

% ASP CHEF VISUALIZATION

% An ASP Chef visualization, which can be used to develop the encoding step by step, is available here: https://asp-chef.alviano.net/#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%21
