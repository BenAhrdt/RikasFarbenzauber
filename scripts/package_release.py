"""Produce a distributable ZIP and latest.json, without data or secrets."""
import argparse
import hashlib
import json
import zipfile
from pathlib import Path
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('--url',required=True,help='Final HTTPS download URL of the zip')
parser.add_argument('--notes',default='')
parser.add_argument('--output',default=str(root/'dist'))
args=parser.parse_args()
import sys
sys.path.insert(0,str(root))
from deployment.releases import https_url, version
https_url(args.url)
v=(root/'VERSION').read_text().strip();version(v)
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
archive=out/f'rikas-farbenzauber-{v}.zip'
# Explicit source allowlist excludes local data, environment, credentials and caches.
folders=['config','studio','static','templates','scripts','deployment','deploy']
files=['install.sh','update.sh','DEVELOPMENT.md','manage.py','VERSION','requirements.txt','requirements-dev.txt','README.md','LICENSE','CHANGELOG.md','ROADMAP.md','.env.example','.gitignore']
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as bundle:
    for name in files:bundle.write(root/name,name)
    for folder in folders:
        for path in sorted((root/folder).rglob('*')):
            if path.is_file() and not path.is_symlink() and '__pycache__' not in path.parts and path.suffix!='.pyc':bundle.write(path,path.relative_to(root))
release={'version':v,'url':args.url,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'notes':args.notes}
(out/'latest.json').write_text(json.dumps(release,ensure_ascii=False,indent=2)+'\n')
print(archive)
print(out/'latest.json')
