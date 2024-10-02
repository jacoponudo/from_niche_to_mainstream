In questa cartella si fa l'analisi esplorativa del cambio del comportamento degli utenti in base ai livelli di crescita dell'outreach di una pagina.
Per farlo:

- EXP/calculate_outreach_vs_interactions.ipynb: partendo dai like aggreaga per ogni pagina, in una finestra di 8 settimane tutti i like univoci che trova e definisce quello come livello di outreach per un post. Poi combina questo valore con l'interazione che può essere alpha o no.

- EXP/check_likes_consistency.ipynb: partendo dai like e dai post legge quanti like sono attesi per ciascuna pagina e quanti ne abbiamo contati nel database dei likes. Dal confronto emerge come ci sia un gap dovuto alla mancata presenza di quelli relativi alle pagine molto grandi.

-EXP/EXP_longitudinal.ipynb: per ciascuna pagina valuto come evolve l'interazione nel tempo in base a alpha e all'outreach.

-EXP/EXP_year_vs_len_vs_size.ipynb: su kaggle per diverse piattaforme fa il confronto dell'evoluzione di alpha rispetto al numero di utenti presenti in un thread.

-EXP/maps_of_pages.ipynb: per ciascuna pagina considero alcune caratteristiche della crescita nel tempo, come l'outreach.

-EXP/EXP_size_vs_behaviour.ipynb: fa un confronto tra numero di persone coinvolte in un thread e comportamento dell'utente (alpha).