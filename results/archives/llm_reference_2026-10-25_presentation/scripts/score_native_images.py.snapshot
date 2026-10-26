"""Re-score public native-image evidence using the external frozen reference key."""
from repo_layout import repo_file, frozen_file
import argparse
from collections import defaultdict
from hashlib import sha256
import json
from pathlib import Path

from benchmark import ROOT,rows
from score import load_key

def score(path):
    data=repo_file('native_images_2026-10-20', root=ROOT);summary=json.loads((data/'summary.json').read_text())
    assert sha256(Path(path).read_bytes()).hexdigest()==summary['audit']['key_sha256']
    key=load_key(path);questions={q['candidate_id']:q for q in rows(repo_file('data/questions.jsonl', root=ROOT))}
    assert set(key)==set(questions)
    records=rows(data/'attempts.jsonl');old=rows(repo_file('data/attempts.jsonl', root=ROOT));result={}
    for mid in summary['rank_order']:
        s=summary['models'][mid]
        rr=[r for r in (old if s['reused'] else records) if r['model_requested']==s['model_requested'] and r['attempt']==1]
        assert len(rr)==len({r['candidate_id'] for r in rr})==200
        correct=sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in rr)
        assert correct==s['correct'],mid
        families={}
        for fid in summary['families']:
            n=sum(r['status']=='ok' and r['choice']==key[r['candidate_id']] for r in rr if questions[r['candidate_id']]['family_id']==fid)
            assert n==s['families'][fid]['correct'];families[fid]=n
        result[mid]={'correct':correct,'questions':200,'families':families}
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--answer-key',type=Path,required=True)
    print(json.dumps(score(p.parse_args().answer_key),indent=2))
