from urllib.parse import urlsplit

def origin(value):
    value=value.strip().rstrip('/')
    if not value.startswith('https://'):value='https://'+value
    parsed=urlsplit(value)
    if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password or parsed.path or parsed.query or parsed.fragment:
        raise ValueError('Bitte eine HTTPS-Adresse ohne Pfad oder Zugangsdaten angeben.')
    host=parsed.hostname.encode('idna').decode('ascii').lower()
    import re
    if not re.fullmatch(r'(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?',host):
        raise ValueError('Bitte einen vollständigen Domainnamen angeben.')
    port=parsed.port
    return 'https://'+host+(f':{port}' if port and port!=443 else '')
