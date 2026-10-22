num(1).
num(2).
num(3).
lucky(1) :- num(1), not unlucky(1).
unlucky(1) :- num(1), not lucky(1).
lucky(2) :- num(2), not unlucky(2).
unlucky(2) :- num(2), not lucky(2).
lucky(3) :- num(3), not unlucky(3).
unlucky(3) :- num(3), not lucky(3).
p :- unlucky(1), not p.
p :- unlucky(2), not p.
p :- unlucky(3), not p.
