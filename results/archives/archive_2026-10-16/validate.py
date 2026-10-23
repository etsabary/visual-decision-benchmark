"""Verify the public packet offline. Validation is not an independent key audit."""
from collections import Counter, defaultdict
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
import re
from benchmark import ROOT, MODELS, rows, payload, canonical, parse_saved_choice, cost


def validate(root=ROOT,verify_payloads=True):
    seal=json.loads((root/'checksums.json').read_text())
    for name,expected in seal['files'].items():
        path=root/name
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=expected:raise ValueError('Checksum mismatch: '+name)
    questions={q['candidate_id']:q for q in rows(root/'data/questions.jsonl')}
    assets={a['asset_id']:a for a in rows(root/'data/assets.jsonl')}
    attempts=rows(root/'data/attempts.jsonl');probes=rows(root/'data/compatibility_probes.jsonl')
    plan=rows(root/'data/request_plan.jsonl');summary=json.loads((root/'results/summary.json').read_text())
    assert len(questions)==200 and len(assets)==227 and len(plan)==1000 and len(attempts)==1003 and len(probes)==4
    assert Counter(q['family_id'] for q in questions.values())==Counter({f'V{i:02d}':10 for i in range(1,21)})
    assert len([a for a in assets.values() if a['path']])==221
    assert sum(a['path'] is None for a in assets.values())==6
    assert sum('third-party source terms not independently cleared' in a['license_id'] for a in assets.values())==6
    for a in assets.values():
        if not a['path']:continue
        raw=(root/a['path']).read_bytes()
        assert len(raw)==a['bytes'] and sha256(raw).hexdigest()==a['sha256']
    signatures=[(r['source_phase'],r['request_index'],r['attempt']) for r in attempts]
    assert len(signatures)==len(set(signatures))
    first=[r for r in attempts if r['attempt']==1]
    assert len(first)==len({(r['candidate_id'],r['model_requested']) for r in first})==1000
    assert Counter(r['model_requested'] for r in first)==Counter({m:200 for m in MODELS})
    task_by_pair={(p['candidate_id'],p['model_requested']):p for p in plan}
    assert len(task_by_pair)==1000
    for a in attempts:
        q=questions[a['candidate_id']];task=task_by_pair[(a['candidate_id'],a['model_requested'])]
        assert a['image_sha256']==[assets[aid]['sha256'] for aid in q['asset_ids']]
        assert all(a[k]==task[k] for k in ('request_payload_sha256','request_body_bytes','image_sha256'))
        choice=parse_saved_choice(a,{o['id'] for o in q['options']})
        assert (choice is not None)==(a['status']=='ok')
        if choice is not None:assert choice==a['choice']
        assert a.get('reported_reasoning_tokens') in (None,0) and not a.get('reasoning_text_present',False)
    replayed=0;unavailable=0
    if verify_payloads:
        for p in plan:
            q=questions[p['candidate_id']]
            if any(assets[aid]['path'] is None for aid in q['asset_ids']):unavailable+=1;continue
            body=canonical(payload(q,assets,p['model_requested'],root))
            assert sha256(body).hexdigest()==p['request_payload_sha256']
            assert len(body)==p['request_body_bytes']
            replayed+=1
    for m in MODELS:
        d=summary['models'][m];rr=[a for a in attempts if a['model_requested']==m]
        money=cost(rr)
        assert Decimal(money['known_usd'])==Decimal(d['core_cost']['exact_decimal_usd'])
        assert money['missing_records']==d['core_cost']['missing_records']
        assert sum(a['status']=='ok' for a in first if a['model_requested']==m)==d['usable_first']
        assert d['correct_first']==sum(v['correct_first'] for v in d['groups']['family_id'].values())
        assert d['correct_first']==sum(v['correct_first'] for v in d['groups']['analysis_subset'].values())
        assert 0<=d['correct_first']<=d['usable_first']<=200
    forbidden={'correct_option_id','correct_first','correct_eventual','choice_first','choice_eventual'}
    for name in ('questions','assets','provenance','attempts','request_plan','compatibility_probes'):
        for r in rows(root/f'data/{name}.jsonl'):assert not forbidden.intersection(r),name
    for path in root.rglob('*'):
        if not path.is_file() or '.git' in path.parts or '__pycache__' in path.parts:continue
        assert not ('PRIVATE' in path.name or path.name.startswith('.env'))
        if path.suffix in ('.json','.jsonl','.md','.html','.svg','.csv','.py'):
            text=path.read_text()
            # Matches runtime home paths without embedding one in this source.
            assert not re.search(r'/(?:Users|home)/[A-Za-z0-9_]',text),str(path)
    return {'status':'PASS','questions':200,'primary_results':1000,'core_attempts':1003,
            'images_included':221,'images_withheld':6,'exact_payloads_reproduced':replayed,
            'payloads_requiring_withheld_images':unavailable,'gold_key_in_public_packet':False,
            'note':'Published accuracy is checked for internal consistency, not independently re-scored without the external key.'}


if __name__=='__main__':print(json.dumps(validate(),indent=2))
