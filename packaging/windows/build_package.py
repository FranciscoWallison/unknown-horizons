"""Build the portable Windows package of Unknown Horizons.

The package needs no installer and no Python on the player's machine:

    UnknownHorizons-<tag>/
        python/                  embeddable CPython + tkinter + site-packages (FIFE, Pillow, ...)
        unknown-horizons/        the game (tracked files of this checkout, minus dev-only folders)
        Jogar Unknown Horizons.bat
        Unknown Horizons (depurar).bat
        LEIA-ME.txt, LICENCAS.txt

Run it with the CPython 3.13 that matches the FIFE wheel (64 bit). The script copies
tkinter from that interpreter, because the embeddable distribution lacks it and the
game needs it for the atlas generation window and its error dialogs.

    python packaging/windows/build_package.py --tag win-v1 --fife-wheel libfife-...whl --out dist
"""
import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))

# Tracked paths that only matter for development, CI or other platforms.
EXCLUDE_PREFIXES = (
	'.github/', 'development/', 'packaging/', 'tests/',
	'.editorconfig', '.gitattributes', '.gitignore', 'MANIFEST.in', 'pyproject.toml',
	'run_gui_tests.sh', 'setup.cfg', 'setup.py', 'setup_mac.py', 'stage_build_mac.py',
	'unknown-horizons.wpr', 'uv.lock',
)
TRANSLATION_DOMAINS = (('unknown-horizons', 'po/uh'), ('unknown-horizons-server', 'po/uh-server'))
LAUNCHER = '@start "" "%~dp0python\\pythonw.exe" "%~dp0unknown-horizons\\run_uh.py" %*\r\n'
DEBUG_LAUNCHER = (
	'@echo off\r\n'
	'echo Unknown Horizons em modo de depuracao. O log vai para Documentos\\My Games\\unknown-horizons\\log\r\n'
	'"%~dp0python\\python.exe" "%~dp0unknown-horizons\\run_uh.py" --debug-log-only %*\r\n'
	'pause\r\n'
)


def log(msg):
	print(f'==> {msg}', flush=True)


def git(*args):
	return subprocess.check_output(['git', '-C', REPO, *args], text=True).strip()


def sha256(path):
	h = hashlib.sha256()
	with open(path, 'rb') as f:
		for block in iter(lambda: f.read(1 << 20), b''):
			h.update(block)
	return h.hexdigest()


def fetch_embed_python(cache_dir):
	version = '{}.{}.{}'.format(*sys.version_info[:3])
	name = f'python-{version}-embed-amd64.zip'
	path = os.path.join(cache_dir, name)
	if not os.path.exists(path):
		os.makedirs(cache_dir, exist_ok=True)
		url = f'https://www.python.org/ftp/python/{version}/{name}'
		log(f'Downloading {url}')
		urllib.request.urlretrieve(url, path)
	return path, version


def build_python(stage, embed_zip, fife_wheel):
	pydir = os.path.join(stage, 'python')
	with zipfile.ZipFile(embed_zip) as z:
		z.extractall(pydir)

	# sys.path of the embedded interpreter: stdlib zip, its own folder, the copied
	# tkinter (Lib), the dependencies (Lib/site-packages) and the game itself.
	# No "import site": none of the dependencies needs .pth files, and site would add
	# the player's own user site-packages to the game's path.
	pth = [f for f in os.listdir(pydir) if f.endswith('._pth')][0]
	with open(os.path.join(pydir, pth), 'w', newline='\r\n') as f:
		f.write('python{}{}.zip\n.\nLib\nLib\\site-packages\n..\\unknown-horizons\n'
		        .format(*sys.version_info[:2]))

	log('Copying tkinter from ' + sys.base_prefix)
	base = sys.base_prefix
	shutil.copytree(os.path.join(base, 'Lib', 'tkinter'), os.path.join(pydir, 'Lib', 'tkinter'),
	                ignore=shutil.ignore_patterns('test', '__pycache__'))
	for dll in ('_tkinter.pyd', 'tcl86t.dll', 'tk86t.dll', 'zlib1.dll'):
		src = os.path.join(base, 'DLLs', dll)
		if os.path.exists(src):
			shutil.copy2(src, pydir)
	shutil.copytree(os.path.join(base, 'tcl'), os.path.join(pydir, 'tcl'),
	                ignore=shutil.ignore_patterns('*.lib', '*.sh', 'nmake', 'demos'))

	log('Installing dependencies into python/Lib/site-packages')
	subprocess.check_call([
		sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check', '--no-compile',
		'--only-binary', ':all:', '--target', os.path.join(pydir, 'Lib', 'site-packages'),
		'-r', os.path.join(HERE, 'requirements.txt'), fife_wheel,
	])
	shutil.rmtree(os.path.join(pydir, 'Lib', 'site-packages', 'bin'), ignore_errors=True)


def copy_game(stage):
	gamedir = os.path.join(stage, 'unknown-horizons')
	files = git('ls-files', '-z').split('\0')
	count = 0
	for rel in files:
		if not rel or rel.startswith(EXCLUDE_PREFIXES):
			continue
		dst = os.path.join(gamedir, rel)
		os.makedirs(os.path.dirname(dst), exist_ok=True)
		shutil.copy2(os.path.join(REPO, rel), dst)
		count += 1
	log(f'{count} game files copied')
	return gamedir


def compile_translations(gamedir):
	"""Same result as `setup.py build_i18n`, but with polib instead of GNU msgfmt."""
	import json

	import polib

	stats = {}
	for domain, po_dir in TRANSLATION_DOMAINS:
		po_dir = os.path.join(REPO, po_dir)
		for name in sorted(os.listdir(po_dir)):
			if not name.endswith('.po'):
				continue
			lang = name[:-3]
			mo_dir = os.path.join(gamedir, 'content', 'lang', lang, 'LC_MESSAGES')
			os.makedirs(mo_dir, exist_ok=True)
			po = polib.pofile(os.path.join(po_dir, name))
			po.save_as_mofile(os.path.join(mo_dir, domain + '.mo'))
			if domain == 'unknown-horizons':
				stats[lang] = po.percent_translated()
	with open(os.path.join(gamedir, 'content', 'lang', 'stats.json'), 'w') as f:
		json.dump(stats, f)
	log(f'{len(stats)} languages compiled (pt_BR {stats.get("pt_BR")}%)')


def write_text(path, text):
	with open(path, 'w', encoding='utf-8', newline='\r\n') as f:
		f.write(text)


def main():
	ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
	ap.add_argument('--tag', required=True, help='release name, e.g. win-v1')
	ap.add_argument('--fife-wheel', required=True, help='libfife cp3xx win_amd64 wheel')
	ap.add_argument('--fife-commit', default='', help='FIFE commit the wheel was built from')
	ap.add_argument('--out', default='dist')
	ap.add_argument('--cache', default=os.path.join('dist', 'cache'))
	args = ap.parse_args()

	if sys.platform != 'win32' or sys.maxsize <= 2**32:
		sys.exit('Run this with 64 bit CPython on Windows.')

	commit = git('rev-parse', '--short=9', 'HEAD')
	name = f'UnknownHorizons-{args.tag}'
	out = os.path.abspath(args.out)
	stage = os.path.join(out, name)
	if os.path.exists(stage):
		shutil.rmtree(stage)
	os.makedirs(stage)

	embed_zip, py_version = fetch_embed_python(os.path.abspath(args.cache))
	build_python(stage, embed_zip, os.path.abspath(args.fife_wheel))
	gamedir = copy_game(stage)
	compile_translations(gamedir)
	write_text(os.path.join(gamedir, 'content', 'gitversion.txt'), f'{args.tag} ({commit})\n')

	write_text(os.path.join(stage, 'Jogar Unknown Horizons.bat'), LAUNCHER)
	write_text(os.path.join(stage, 'Unknown Horizons (depurar).bat'), DEBUG_LAUNCHER)
	info = {
		'tag': args.tag, 'commit': commit, 'python': py_version,
		'fife_wheel': os.path.basename(args.fife_wheel), 'fife_wheel_sha256': sha256(args.fife_wheel),
		'fife_commit': args.fife_commit or 'desconhecido',
	}
	for doc in ('LEIA-ME.txt', 'LICENCAS.txt'):
		with open(os.path.join(HERE, doc), encoding='utf-8') as f:
			write_text(os.path.join(stage, doc), f.read().format(**info))

	zip_path = os.path.join(out, f'{name}-win64.zip')
	log('Writing ' + zip_path)
	with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
		for root, dirs, files in os.walk(stage):
			dirs.sort()
			for fn in sorted(files):
				full = os.path.join(root, fn)
				z.write(full, os.path.relpath(full, out))
	digest = sha256(zip_path)
	write_text(zip_path + '.sha256', f'{digest}  {os.path.basename(zip_path)}\n')
	log(f'SHA256 {digest}')
	log(f'{os.path.getsize(zip_path) / 2**20:.1f} MB')


if __name__ == '__main__':
	main()
