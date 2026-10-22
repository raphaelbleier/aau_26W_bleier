likes(kate,fish).
likes(kate,soup).
likes(mike,beef).
likes(mike,cake).
likes(paul,duck).
likes(paul,pork).
likes(tina,beef).
likes(tina,soup).

order(Z) :- likes(X,Z), likes(Y,Z), X != Y.
happy(X) :- likes(X,Y), order(Y).
