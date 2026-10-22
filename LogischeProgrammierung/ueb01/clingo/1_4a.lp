canary(tweety).
penguin(tux).
bird(X) :- canary(X).
bird(X) :- penguin(X).
injured(X) :- bird(X), not ok(X).
ok(X) :- bird(X), not injured(X).
flies(X) :- ok(X), not penguin(X).
