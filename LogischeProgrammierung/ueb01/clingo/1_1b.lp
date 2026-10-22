likes(kate,fish).
likes(kate,soup).
likes(mike,beef).
likes(mike,cake).
likes(paul,duck).
likes(paul,pork).
likes(tina,beef).
likes(tina,soup).

order(beef) :- likes(mike,beef), likes(tina,beef).
order(soup) :- likes(kate,soup), likes(tina,soup).

happy(kate) :- likes(kate,fish), order(fish).
happy(kate) :- likes(kate,soup), order(soup).
happy(mike) :- likes(mike,beef), order(beef).
happy(mike) :- likes(mike,cake), order(cake).
happy(paul) :- likes(paul,duck), order(duck).
happy(paul) :- likes(paul,pork), order(pork).
happy(tina) :- likes(tina,beef), order(beef).
happy(tina) :- likes(tina,soup), order(soup).
