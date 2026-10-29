# Les Arrondissements de San Francisco

San Francisco has more than a hundred neighborhoods, many only a few blocks wide. This project adds one layer above them: **16 numbered arrondissements**, inspired by those of Paris, bounded by the big avenues everyone already knows and organized around Downtown into three rings that fan out from the center.

**Open `index.html`** for the interactive map. It is a single self-contained page: pan and zoom the city, switch between neighborhoods, boundary streets and rings, search any neighborhood, and compare the arrondissements by area and population.

| Ring | Arrondissements |
|---|---|
| Ring 1 | 1 Downtown · 2 Northport · 3 NoMa · 4 SoMa |
| Ring 2 | 5 Pacific · 6 Ashbury · 7 The Valleys · 8 The Mission · 9 Potrero |
| Ring 3 | 10 Federal · 11 The Richmond · 12 The Sunset · 13 Oceanview · 14 The Hills · 15 Southside · 16 Bayview |

Sizes roughly double ring by ring, a loosely fractal guide: about ½ sq mi for the 1st, 1 sq mi for the rest of Ring 1, 2 for Ring 2 and 4 for Ring 3.

Golden Gate Park is part of the 11th, The Richmond.

Arrondissements with a prominent hill of their own take that hill's name: Pacific, Ashbury, Potrero and Bayview. The central heights give the 14th its name, The Hills. The 2nd holds two celebrated hills, Telegraph and Russian, and in fairness to both it is called Northport.

## Repository layout

```
index.html            the website (built, ready to open or host)
build/                everything used to make it
  spec.py, build.py   arrondissement boundaries, snapped to street centerlines  -> arr.json
  gen.py, post.py     map layers, street classes, colors                         -> mapdata.json
  gaz.py,             neighborhood gazetteer: splits, renames, custom polygons
  gaz_build.py        and floating labels                                        -> gaz.json, floats.json
  gaz_apply.py        merges neighborhoods, rings and populations into mapdata.json
  v3.py               revision: Golden Gate Park joins the 11th; Sunset and Parkside merge; the 9th gains Golden Gate Heights, Forest Hill and West Portal, bounded on the west by 17th Ave (north of Rivera) and 15th Ave (south of Rivera), and on the north by Lawton St and 7th Ave; everything east of 7th Ave is the new neighborhood Parnassus Piedmont (reads arr_v5.json)
  v4.py               revision: a new 1st, Downtown (Financial District with Union Square east of Kearny, Embarcadero, New Montgomery east of 3rd St, East Cut, Rincon Hill); Jackson Square and Golden Gateway join Northport; renumbering to 16 (reads arr_v6.json)
  stickers.py         estimate of border-crossing stickers per arrondissement    -> sticker_points.json
  template.html       page template (HTML, CSS, JS)
  assemble.py         template.html + mapdata.json -> ../index.html
  *.json, *.geojson   source and intermediate data
```

To rebuild the page after editing the template or the data:

```
cd build
pip install shapely pyproj networkx
python gaz_apply.py     # only if neighborhoods changed
python assemble.py
```

## Data

- Street centerlines and neighborhood boundaries: [DataSF](https://datasf.org) (City and County of San Francisco)
- Population: 2020 U.S. Census, counted by block
- Parks, water and place names: © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors (ODbL)

The boundaries are a draft for discussion and carry no official status. Suggestions for more neighborhoods and labels are welcome: open an issue.
