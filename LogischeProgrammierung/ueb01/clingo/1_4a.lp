canary(tweety).
penguin(tux).
bird(tweety) :- canary(tweety).
bird(tux) :- penguin(tux).
injured(tweety) :- bird(tweety), not ok(tweety).
ok(tweety) :- bird(tweety), not injured(tweety).
injured(tux) :- bird(tux), not ok(tux).
ok(tux) :- bird(tux), not injured(tux).
flies(tweety) :- ok(tweety), not penguin(tweety).
flies(tux) :- ok(tux), not penguin(tux).
