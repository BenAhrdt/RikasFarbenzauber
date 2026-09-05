"""CLI equivalent of the web button, using the root-owned installed source."""
import json
import os
import uuid
from pathlib import Path
from releases import manifest, version
config=json.loads(Path('/etc/rikas-updater.json').read_text())
release=manifest(config['manifest_url'])
current=(Path(config['root'])/'current/VERSION').read_text().strip()
if version(release['version'])<=version(current):raise SystemExit('Die aktuelle Version ist bereits installiert.')
state=Path(config['state'])
if (state/'active').exists():raise SystemExit('Ein Update läuft bereits.')
job=str(uuid.uuid4());temporary=state/f'.request-{job}'
with temporary.open('x') as stream:json.dump({'job':job,'version':release['version'],'sha256':release['sha256']},stream)
try:os.link(temporary,state/'request.json')
finally:temporary.unlink(missing_ok=True)
print('Update angefordert. Fortschritt: Verwaltung → Updates oder journalctl -u rikas-updater.service')
