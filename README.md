# Les Arrondissements de San Francisco

San Francisco has more than a hundred neighborhoods, many only a few blocks wide. This project adds one layer above them: **16 numbered arrondissements**, inspired by those of Paris, bounded by the big avenues everyone already knows and organized into three rings that fan out from the center.

**Open `index.html`** for the interactive map. It is a single self-contained page: pan and zoom the city, switch between neighborhoods, boundary streets and rings, search any neighborhood, and compare the arrondissements by area and population.

| Ring | Arrondissements |
|---|---|
| Ring 1 | 1 Northside · 2 NoMa · 3 SoMa |
| Ring 2 | 4 Pacific · 5 Western · 6 The Valleys · 7 Mission · 8 Sunrise · 9 The Hills |
| Ring 3 | 10 Federal · 11 Richmond · 12 Sunset · 13 Parkside · 14 Merced · 15 Southside · 16 Bayview |

Golden Gate Park belongs to the whole city and sits outside the numbering.

## Repository layout

```
index.html            the website (built, ready to open or host)
build/                everything used to make it
  spec.py, build.py   arrondissement boundaries, snapped to street centerlines  -> arr.json
  gen.py, post.py     map layers, street classes, colors                         -> mapdata.json
  gaz.py,             neighborhood gazetteer: splits, renames, custom polygons
  gaz_build.py        and floating labels                                        -> gaz.json, floats.json
  gaz_apply.py        merges neighborhoods, rings and populations into mapdata.json
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
