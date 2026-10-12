# Konventionen

So werden neue Blätter in diesem Repo abgelegt.

## Struktur

```
<Kurs>/ueb<NN>/
```

`<Kurs>` ist der Kursordner in der Wurzel, `<NN>` die zweistellige Blattnummer (`ueb01`, `ueb02`, ...). Jeder Kursordner hat eine `README.md` mit einer Tabelle der Blätter (Blatt, Thema, Abgabe, Links zu Lösung und Erklärung).

## Inhalt eines Blattordners

Immer eine `README.md` mit der Aufgabenübersicht und der erklärten Lösung.

| Art | Dateien |
|---|---|
| Mathematik / Theorie | `loesung_blattNN.pdf`, `erklaerung_blattNN.pdf`, `blattNN.tex` |
| Code | Quellcode plus `README.md` mit Erklärung und Hinweisen zum Ausführen |

## Bestehende Abweichungen

Die Ordner dieses Semesters wurden bereits vor dieser Konvention angelegt und bleiben unverändert:

- `WebTechnologienUE/Assignment<NN>/` mit `ex<N>`-Unterordnern und `Antworten_Assignment<NN>.pdf`.
- `LinearOptimization/ueb<NN>/` mit `Bleier_sheet_<N>.tex` und `.pdf`.

## Sonstiges

- Keine `node_modules`, Build-Ordner, Archive oder Zugangsdaten committen (siehe `.gitignore`).
- Commits nach Conventional Commits, z.B. `docs(webtech): add assignment 9`.
