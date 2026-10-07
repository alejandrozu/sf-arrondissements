"""Build ../index.html from template.html + mapdata.json."""
import json
d = json.load(open('mapdata.json'))
page = open('template.html').read().replace('__DATA__', json.dumps(d, separators=(',', ':')).replace('</', '<\\/'))
i = page.index('</style>') + 8
head, body = page[:i], page[i:]
doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
       + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
open('../index.html', 'w').write(doc)
print('wrote ../index.html')
