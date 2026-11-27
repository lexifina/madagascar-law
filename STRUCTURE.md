# Structure du dépôt / Repository layout

Noms en français, la langue des textes publiés par CNLEGIS. / Names in French, the language of the texts as CNLEGIS publishes them.

```
constitution/                         la Constitution (versions de 1998, 2007, 2009 et 2010), un fichier par article
codes/<code>/                         un code (« portant Code … ») : codes/code-du-travail/, codes/code-des-assurances/ …
lois/<année>/<numéro>-<objet>/        lois, lois organiques et lois constitutionnelles : lois/2014/2014-006-lutte-contre-la-cybercriminalite/
ordonnances/<année>/<numéro>-<objet>/ ordonnances : ordonnances/1960/60-146-relative-au-regime-foncier-de-l-immatriculation/
decrets/<année>/<numéro>-<objet>/     décrets (réglementaires ; les nominations et autres mesures individuelles sont exclues)
decrets/<année>/<mois>/<numéro>-<objet>/  les années de plus de 900 décrets sont réparties par mois (≤ 1 000 entrées par dossier)
arretes/<année>/<numéro>-<objet>/     arrêtés (réglementaires)
data/  tools/  visualisations/  vulnerabilities/
corpus.json                           la liste des textes ajoutés depuis CNLEGIS (mg/national/acts)
```

Dans le dossier d’un texte / Inside an act's folder:

- `README.md` : intitulé, fiche CNLEGIS, Journal officiel, date d’entrée en vigueur et sa justification, état selon CNLEGIS ;
- `visas.md` : en-tête, visas et formule de promulgation ;
- `art-001.md`, `art-002.md`, `art-012-bis.md` … : un fichier par article (`art-001` = « Article premier ») ;
- `structure.md` : livres, titres, chapitres et sections, avec l’article qu’ils précèdent ;
- `signatures.md` : lieu, date et signatures ;
- `texte-integral.md` : le texte en un seul fichier, quand aucun article n’est repéré.

<année> est l’année du numéro du texte (loi n° 2014-038 → lois/2014/, même si elle est datée du 9 janvier 2015) ; quand
le numéro et la date de la fiche CNLEGIS se contredisent, l’année de la date.
