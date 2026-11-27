import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch
import pytest
from core.diagnostics import DEFAULT_SETTINGS, CRITICAL_FILES, diagnose, load_settings, repair_settings


def prepare(root):
    for name in CRITICAL_FILES:
        path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('pass\n',encoding='utf-8')


def test_diagnostics_is_read_only_and_reports_missing_source(tmp_path):
    (tmp_path/'config.json').write_text('{bad',encoding='utf-8')
    before={p.name:p.read_bytes() for p in tmp_path.iterdir()}
    report=diagnose(tmp_path)
    assert not report['ok'] and not report['settings_ok']
    assert any('Source file' in error for error in report['errors'])
    assert before=={p.name:p.read_bytes() for p in tmp_path.iterdir()}


def test_repair_keeps_exact_backup_and_leaves_music_untouched(tmp_path):
    original=b'{ invalid settings\xff'
    (tmp_path/'config.json').write_bytes(original)
    (tmp_path/'recording.mid').write_bytes(b'music data')
    result=repair_settings(tmp_path)
    assert result['changed']
    assert Path(result['backup']).read_bytes()==original
    assert load_settings(tmp_path)==DEFAULT_SETTINGS
    assert (tmp_path/'recording.mid').read_bytes()==b'music data'
    assert not list(tmp_path.glob('config-repair-*.tmp'))


def test_valid_custom_settings_are_not_reset(tmp_path):
    content='{"bpm": 88, "beats_per_bar": 3}'
    (tmp_path/'config.json').write_text(content,encoding='utf-8')
    assert not repair_settings(tmp_path)['changed']
    assert (tmp_path/'config.json').read_text(encoding='utf-8')==content
    assert not (tmp_path/'recovery-backups').exists()


def test_failed_replacement_does_not_destroy_original(tmp_path):
    (tmp_path/'config.json').write_text('bad',encoding='utf-8')
    with patch('core.diagnostics.os.replace',side_effect=OSError('write failed')):
        with pytest.raises(OSError):repair_settings(tmp_path)
    assert (tmp_path/'config.json').read_text(encoding='utf-8')=='bad'
    assert len(list((tmp_path/'recovery-backups').iterdir()))==1
    assert not list(tmp_path.glob('config-repair-*.tmp'))


@pytest.mark.parametrize('value',[{'bpm':0},{'bpm':float('nan')},{'bpm':True},{'beats_per_bar':2.5},{'width':3},[]])
def test_invalid_settings_are_detected_and_recoverable(tmp_path,value):
    (tmp_path/'config.json').write_text(json.dumps(value),encoding='utf-8')
    with pytest.raises(ValueError):load_settings(tmp_path)
    assert repair_settings(tmp_path)['changed']
    assert load_settings(tmp_path)==DEFAULT_SETTINGS


def test_missing_dependencies_are_reported_not_installed(tmp_path):
    prepare(tmp_path)
    with patch('core.diagnostics.importlib.util.find_spec',return_value=None):
        result=diagnose(tmp_path)
    assert not result['ok']
    assert all(not v for v in result['dependencies'].values())
    assert not (tmp_path/'config.json').exists()


@pytest.mark.parametrize('script',['main.py','run.py','preview.py','ui/window.py'])
def test_all_launchers_share_diagnostics(script):
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-B',script,'--diagnose'],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=20)
    assert result.returncode==0,result.stdout+result.stderr
    assert json.loads(result.stdout)['ok']


@pytest.mark.parametrize('script',['main.py','run.py','preview.py','ui/window.py'])
def test_all_launchers_complete_bounded_demo(script):
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'-B',script,'--headless','--demo','--frames','3'],cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=20)
    assert result.returncode==0,result.stdout+result.stderr
    assert 'shutdown completed' in result.stdout


def test_concurrent_settings_change_aborts_recovery(tmp_path):
    target=tmp_path/'config.json';target.write_text('bad',encoding='utf-8')
    original_read=Path.read_bytes
    reads=[0]
    def read(path):
        if path==target:
            reads[0]+=1
            if reads[0]==2:
                target.write_text('{"bpm": 99}',encoding='utf-8')
        return original_read(path)
    with patch.object(Path,'read_bytes',read):
        with pytest.raises(ValueError,match='changed during recovery'):
            repair_settings(tmp_path)
    assert json.loads(target.read_text())['bpm']==99


def test_repair_rejects_symlinked_settings(tmp_path):
    target=tmp_path/'outside.json';target.write_text('bad')
    path=tmp_path/'config.json'
    # Exercise the refusal without relying on Windows symlink privileges.
    original=Path.is_symlink
    with patch.object(Path,'is_symlink',lambda p: p==path or original(p)):
        with pytest.raises(ValueError):repair_settings(tmp_path)
    assert target.read_text()=='bad'
