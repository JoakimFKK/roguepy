### Gå igennem hver eneste `tile` i `game_map`

Understående var skrevet inde i [engine.py](engine.py "Engine filen."), og går igennem hver eneste tile i `game_map.tiles`.  
Hvad der sker er at der blive importeret `random` for at sætte en `tile`s til enten en `wall` eller `floor`.
 
~~~
    import tile_types
    import random
    for i, x in enumerate(self.game_map.tiles):
        for ii, _ in enumerate(x):
            self.game_map.tiles[i, ii] = random.choice((tile_types.floor, tile_types.wall))
~~~
Denne måde skal dog ikke bruges præcis som der står skrevet her, da det ville sætte chancen for enten eller til 50% hver gang.  
En bedre måde at gøre det på ville være noget i retning af følgende;

~~~
import tile_types
import random

for i, x in enumerate(self.game_map.tiles):
    for ii, _ in enumerate(x):
        if random.random() < 0.55:
            new_tile_value = tile_types.floor
        else:
            new_tile_value = tile_types.floor
        self.game_map.tiles[i, ii] = new_tile_value
~~~
Dette sikre os mere kontrol over det endelige resultat, og giver os mulighed for at udvide systemet senere uden at tilføje/ændre alt for meget kode.


### Tileset, og valg af grafik

Der bliver tilsat et tileset (også kaldet tilesheet, men for at undgå misforståelser vil jeg fortsætte med at kalde dem "tilesets" uden for kode-syntax)
inde i [main](main.py)'s `main()` funktion.  
```
tcod.tileset.load_tilesheet(path, columns, rows, charmap)
```

`path` er tilesettets lokation, hvor `columns` og `rows` refererer til antallet af hver især i tilesettet. _(For reference, vores nuværende [tileset](resources/Vidumec_15x15.png) er 16x16.)_

`charmap` refererer til hvordan `tileset` objektet finder det rigtige symbol når det skal "tegnes" i konsolen.  
Vores nuværende [tileset](resources/Vidumec_15x15.png) bruger [Code page 437](https://en.wikipedia.org/wiki/Code_page_437 "Wikipedia: Code page 437"),
hvilket vil sige, fra top venstre hjørne til top højre hjørne, at hvert symbol har en værdi som bliver kaldt ved at give `tcod` en Unicode værdi tilsværende til hvad der skal bruges.

Dette ville ikke være vigtigt nok at nævne hvis det ikke var fordi at vi har flere måder at pege på positioner i tilesettet i vores kode.  
Inde i [Entity Factories](entity_factories.py) udprinter vi symbolet på række 5, kolonne 1, på følgende måde:
~~~
player = Actor(
    char='@',
    ...
)
~~~
Og i [Tile Types](tile_types.py) bliver der brugt funktionen `ord()` for at gøre _essentielt_ det samme som ovenstående:

~~~
floor = new_tile(
    ...
    dark=(
        ord('.'),
    ...
    ),
    ...
)
~~~

`ord(c)` bliver givet en string som repræsenterer en enkel Unicode karakter, og returnerer integer værdien af den.  
`ord('.')` vil så returnerer `46` hvilket svarer til række 15, kolonne 3.

Grunden til at der er en forskel mellem [Entity Factories](entity_factories.py) og [Tile Types](tile_types.py) er måden `tile_types` er sat op, som kan ses her:
```
graphic_dt = np.dtype(
    [
        ('ch', np.int32),
        ('fg', '3B'),
        ('bg', '3B'),
    ]
)
```
`fg` og `bg` står for "Fore"- og "Background", og forventer en tuple med 3 værdier til RGB.  
`ch` forventer en integer, hvilket vil sige at vi skal konverterer symbolet vi vil bruge til at repræsenterer den tile til Unicode.

Den sidste ting jeg vil nævne her er forskellen mellem Wikipedias tabel over CHARMAP_CP437 og hvordan det rent faktisk bliver brugt i `tcod`.  
I Wikipedias tabel bliver symbolerne vist i den rigtige rækkefølge, med _Alt code_ direkte under, og derefter Unicode værdien, hvor den starter fra 0, og op til 255.

Men i `tcod` er det således:
```
[0, 9786, 9787, 9829, 9830, 9827, 9824, 8226, 9688, 9675, 9689, 9794, 9792, 9834, 9835, 9788,
9658, 9668, 8597, 8252, 182, 167, 9644, 8616, 8593, 8595, 8594, 8592, 8735, 8596, 9650, 9660,
32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47,
48,49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
...
]
``` 