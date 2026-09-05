"""Release manifest validation shared by web UI and the privileged updater."""
import hashlib
import json
import re
import urllib.parse
import urllib.request
import zipfile
from pathlib import PurePosixPath

VERSION_RE = re.compile(r'^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$')
MAX_ARCHIVE = 80 * 1024 * 1024

def version(value):
    if not isinstance(value,str) or not VERSION_RE.fullmatch(value):
        raise ValueError('Ungültige Versionsnummer; erwartet wird beispielsweise 0.5.0.')
    return tuple(map(int,value.split('.')))

def https_url(value):
    if not isinstance(value,str):raise ValueError('Ungültige Update-Adresse.')
    parsed=urllib.parse.urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
        raise ValueError('Updates benötigen eine HTTPS-Adresse ohne Zugangsdaten.')
    return value

def manifest(url):
    https_url(url)
    request=urllib.request.Request(url,headers={'User-Agent':'RikasFarbenzauber-Updater','Accept':'application/json'})
    with urllib.request.urlopen(request,timeout=15) as response:
        https_url(response.url)
        raw=response.read(256*1024+1)
    if len(raw)>256*1024:raise ValueError('Die Update-Beschreibung ist zu groß.')
    data=json.loads(raw)
    if not isinstance(data,dict):raise ValueError('Ungültige Update-Beschreibung.')
    version(data.get('version'))
    https_url(data.get('url'))
    if not isinstance(data.get('sha256'),str) or not re.fullmatch('[a-f0-9]{64}',data['sha256']):
        raise ValueError('Die SHA-256-Prüfsumme fehlt oder ist ungültig.')
    return {key:data[key] for key in ['version','url','sha256']} | {'notes':str(data.get('notes',''))[:6000]}

def download(release,destination):
    request=urllib.request.Request(https_url(release['url']),headers={'User-Agent':'RikasFarbenzauber-Updater'})
    digest=hashlib.sha256();size=0
    with urllib.request.urlopen(request,timeout=30) as response,open(destination,'xb') as target:
        https_url(response.url)
        while chunk:=response.read(1024*1024):
            size+=len(chunk)
            if size>MAX_ARCHIVE:raise ValueError('Update-Archiv überschreitet 80 MB.')
            digest.update(chunk);target.write(chunk)
    if digest.hexdigest()!=release['sha256']:raise ValueError('Prüfsumme stimmt nicht. Update wurde abgebrochen.')

def unpack(archive,destination,expected_version):
    version(expected_version)
    with zipfile.ZipFile(archive) as bundle:
        entries=bundle.infolist()
        if len(entries)>5000 or sum(e.file_size for e in entries)>160*1024*1024:
            raise ValueError('Update-Archiv ist zu groß.')
        seen=set()
        for entry in entries:
            path=PurePosixPath(entry.filename)
            if path.is_absolute() or '..' in path.parts or '\\' in entry.filename or not path.parts or path.parts[0] in {'.env','data','.venv','.git'}:
                raise ValueError('Unsicherer Dateipfad im Update.')
            if path in seen:raise ValueError('Doppelter Dateipfad im Update.')
            seen.add(path)
            mode=(entry.external_attr>>16)&0o170000
            if mode not in (0,0o100000,0o040000):raise ValueError('Links oder Spezialdateien sind in Updates nicht erlaubt.')
        bundle.extractall(destination)
    if (destination/'VERSION').read_text().strip()!=expected_version:
        raise ValueError('Archiv und angekündigte Version stimmen nicht überein.')
    for name in ['manage.py','requirements.txt','scripts/build.sh','config/wsgi.py']:
        if not (destination/name).is_file():raise ValueError('Unvollständiges Update-Archiv.')
