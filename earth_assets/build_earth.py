from pathlib import Path
import base64
root=Path(__file__).resolve().parents[1]
assets=root/'earth_assets'
source=Path(__file__).with_name('earth_template.template').read_text(encoding='utf-8')
source=source.replace('__THREE__',(assets/'three.min.js').read_text(encoding='utf-8'))
for key,name in [('__EARTH__','earth_8k.jpg'),('__NORMAL__','earth_normal.jpg'),('__SPECULAR__','earth_specular.jpg')]:
    source=source.replace(key,'data:image/jpeg;base64,'+base64.b64encode((assets/name).read_bytes()).decode())
out=root/'抗战历史沉浸式课堂.html'
out.write_text(source,encoding='utf-8')
print(str(out).encode('unicode_escape').decode(),out.stat().st_size)
