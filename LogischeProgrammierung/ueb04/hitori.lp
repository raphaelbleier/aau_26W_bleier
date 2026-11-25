{ shaded(R,C) } :- cell(R,C,_).
white(R,C) :- cell(R,C,_), not shaded(R,C).

% Rechte und untere Nachbarn reichen, um jedes Paar einmal zu prüfen.
:- shaded(R,C), shaded(R,C+1).
:- shaded(R,C), shaded(R+1,C).

:- white(R,C1), white(R,C2), cell(R,C1,V), cell(R,C2,V), C1 < C2.
:- white(R1,C), white(R2,C), cell(R1,C,V), cell(R2,C,V), R1 < R2.

% Reihenfolge: zuerst die Zeile, dann die Spalte.
earlier(R,C) :- white(R,C), white(R0,_), R0 < R.
earlier(R,C) :- white(R,C), white(R,C0), C0 < C.
start(R,C) :- white(R,C), not earlier(R,C).
has_start :- start(_,_).
:- not has_start.

% Für die Suche sind Nachbarn in allen vier Richtungen erlaubt.
reach(R,C) :- start(R,C).
reach(R,C) :- white(R,C), reach(R-1,C).
reach(R,C) :- white(R,C), reach(R+1,C).
reach(R,C) :- white(R,C), reach(R,C-1).
reach(R,C) :- white(R,C), reach(R,C+1).
:- white(R,C), not reach(R,C).

#show shaded/2.
