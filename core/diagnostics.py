"""Read-only startup checks and explicit, backed-up settings recovery.

Recovery never downloads code, edits Python files, removes recordings or runs a shell.
"""
import ast
from datetime import datetime, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import sys
import tempfile
import uuid

DEFAULT_SETTINGS = {'bpm':120.0,'beats_per_bar':4,'width':1280,'height':820}
CRITICAL_FILES = ('main.py','ui/application.py','core/app_controller.py',
                  'core/track_system.py','core/notation_processor.py',
                  'core/playback_engine.py','midi_input/message_parser.py',
                  'midi_input/midi_listener.py')


def validate_settings(data):
    if not isinstance(data,dict):
        raise ValueError('Settings must be a JSON object')
    result = dict(DEFAULT_SETTINGS)
    result.update(data)
    for key,low,high in [('bpm',20,400),('beats_per_bar',1,32),
                         ('width',1280,3840),('height',820,2160)]:
        value = result[key]
        if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value):
            raise ValueError(f'Invalid setting: {key}')
        if not low <= value <= high or (key != 'bpm' and int(value) != value):
            raise ValueError(f'Out-of-range setting: {key}')
    return result


def load_settings(root):
    path = Path(root)/'config.json'
    if not path.exists():
        return dict(DEFAULT_SETTINGS)
    return validate_settings(json.loads(path.read_text(encoding='utf-8')))


def diagnose(root):
    root = Path(root).resolve()
    errors = []
    dependencies = {}
    for module in ('pygame','mido','rtmidi'):
        dependencies[module] = importlib.util.find_spec(module) is not None
        if not dependencies[module]:
            errors.append('Missing Python library: '+module)
    if sys.version_info < (3,10):
        errors.append('Python 3.10+ required')
    for name in CRITICAL_FILES:
        path = root/name
        try:
            ast.parse(path.read_text(encoding='utf-8-sig'),filename=name)
        except (OSError,SyntaxError,UnicodeError) as error:
            errors.append(f'Source file {name}: {error}')
    settings_ok = True
    try:
        load_settings(root)
    except (ValueError,OSError,UnicodeError) as error:
        settings_ok = False
        errors.append('Invalid config.json: '+str(error))
    return {'ok':not errors,'python':sys.version.split()[0],
            'dependencies':dependencies,'settings_ok':settings_ok,
            'settings_file_exists':(root/'config.json').exists(),
            'errors':errors,
            'repair_scope':'Only config.json can be restored explicitly; code and recordings are not modified.'}


def repair_settings(root):
    """Restore defaults only for missing/invalid settings, after retaining exact bytes."""
    root = Path(root).resolve()
    target = root/'config.json'
    if target.is_symlink():
        raise ValueError('Refusing to replace a symlinked configuration')
    if target.exists():
        try:
            load_settings(root)
            return {'changed':False,'reason':'Settings are valid; no repair needed','backup':None}
        except (ValueError,UnicodeError):
            pass
    backup = None
    original = None
    if target.exists():
        original = target.read_bytes()
        directory = root/'recovery-backups'
        directory.mkdir(exist_ok=True)
        if directory.is_symlink():
            raise ValueError('Refusing a symlinked backup directory')
        backup = directory/('config-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex+'.json.bak')
        with backup.open('xb') as stream:
            stream.write(original)
            stream.flush()
            os.fsync(stream.fileno())
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=root,
                                         prefix='config-repair-',suffix='.tmp',delete=False) as stream:
            temp_path = Path(stream.name)
            json.dump(DEFAULT_SETTINGS,stream,indent=2,allow_nan=False)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        validate_settings(json.loads(temp_path.read_text(encoding='utf-8')))
        if target.exists():
            if original is None or target.read_bytes() != original:
                raise ValueError('Settings changed during recovery; no replacement made')
        elif original is not None:
            raise ValueError('Settings disappeared during recovery; no replacement made')
        os.replace(temp_path,target)
        temp_path = None
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
    return {'changed':True,'reason':'Default settings restored','backup':str(backup) if backup else None}
