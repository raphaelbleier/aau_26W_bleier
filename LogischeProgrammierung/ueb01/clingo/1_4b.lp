num(1).
num(2).
num(3).
lucky(X) :- num(X), not unlucky(X).
unlucky(X) :- num(X), not lucky(X).
p :- unlucky(X), not p.
