import os
from random import shuffle

pixels = list(range(322200))
shuffle(pixels)
open('pixels', 'w').write('\n'.join([str(_) for _ in pixels]))

open('exceptions', 'w').write('')

os.system('cp static/img/map2-empty.png static/img/map2.png')