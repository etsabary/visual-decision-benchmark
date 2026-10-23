"""Offline data helpers, exact historical payload construction and external-key scoring.

This module has no transport or credential handling and never makes API calls.
"""
from collections import Counter, defaultdict
from decimal import Decimal
from hashlib import sha256
import base64
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
DECISION_MODELS=('typesafe/jev-1.14','openai/gpt-6-luna-decisions')
LLM_MODELS=('openai/gpt-6-luna','openai/gpt-5.4-nano','google/gemini-2.5-flash-lite')
MODELS=DECISION_MODELS+LLM_MODELS
PROVIDERS={LLM_MODELS[0]:'openai',LLM_MODELS[1]:'openai',LLM_MODELS[2]:'google-ai-studio'}


def rows(path):return [json.loads(s) for s in Path(path).read_text().splitlines() if s.strip()]
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(value):return sha256(canonical(value)).hexdigest()


def payload(question,assets,model,root=ROOT):
    if model not in MODELS:raise ValueError('Unlisted model')
    images=[]
    for aid in question['asset_ids']:
        asset=assets[aid]
        if not asset['path']:raise FileNotFoundError('Withheld tested image: '+aid)
        raw=(root/asset['path']).read_bytes()
        if sha256(raw).hexdigest()!=asset['sha256']:raise ValueError('Changed image: '+aid)
        images.append({'type':'image_url','image_url':{'url':'data:'+asset['mime']+';base64,'+base64.b64encode(raw).decode('ascii')}})
    if model in DECISION_MODELS:
        return {'model':model,'state':images,'questions':{'decision':{
            'type':'choice','instructions':question['question']+'\n\nRules: '+question['rules'],
            'criteria':{o['id']:o['text'] for o in question['options']}}}}
    text=question['question']+'\n\nRules: '+question['rules']+'\n\nOptions:\n'
    text+='\n'.join(o['id']+': '+o['text'] for o in question['options'])
    text+='\n\nReturn only the numeric option ID, without explanation.'
    result={'model':model,'messages':[{'role':'user','content':[{'type':'text','text':text}]+images}],
            'max_tokens':32,'stream':False,'usage':{'include':True},'reasoning':{'enabled':False},
            'provider':{'only':[PROVIDERS[model]],'allow_fallbacks':False,'require_parameters':True}}
    if model.startswith('openai/'):result['reasoning']['effort']='none'
    return result


def cost(records):
    values=[Decimal(str(r['reported_cost_usd'])) for r in records if r.get('reported_cost_usd') is not None]
    return {'known_usd':str(sum(values,Decimal(0))),'known_records':len(values),'missing_records':len(records)-len(values)}


def parse_saved_choice(record,allowed):
    if record['http_status']!=200:return None
    if record['model_requested'] in DECISION_MODELS:
        return record['choice'] if record['choice'] in allowed else None
    text=(record.get('output_text') or '').strip()
    return text if record.get('finish_reason')=='stop' and text in allowed else None


def score(answer_key,root=ROOT):
    questions={q['candidate_id']:q for q in rows(root/'data/questions.jsonl')}
    if set(answer_key)!=set(questions):raise ValueError('Key must cover exactly the frozen 200 IDs')
    for qid,key in answer_key.items():
        if key not in {o['id'] for o in questions[qid]['options']}:raise ValueError('Invalid key option: '+qid)
    groups=defaultdict(list)
    for r in rows(root/'data/attempts.jsonl'):groups[(r['candidate_id'],r['model_requested'])].append(r)
    assert len(groups)==1000
    models={}
    for model in MODELS:
        first=[];eventual=[];all_attempts=[];families=Counter()
        for qid,q in questions.items():
            aa=sorted(groups[(qid,model)],key=lambda r:r['attempt'])
            assert [r['attempt'] for r in aa] in ([1],[1,2])
            allowed={o['id'] for o in q['options']}
            choice=parse_saved_choice(aa[0],allowed)
            first.append((choice,choice==answer_key[qid]));all_attempts+=aa
            eventual.append(parse_saved_choice(aa[-1],allowed)==answer_key[qid])
            families[q['family_id']]+=choice==answer_key[qid]
        models[model]={'correct_first':sum(c for _,c in first),'usable_first':sum(c is not None for c,_ in first),
                       'eventual_correct':sum(eventual),'cost':cost(all_attempts),'families':dict(families)}
    return models


def confidence_profile(answer_key,records,scheduled=200,thresholds=(.5,.8,.9,.95,.99,1.0)):
    result={}
    for model in DECISION_MODELS:
        first=[r for r in records if r['model_requested']==model and r['attempt']==1 and r['status']=='ok']
        result[model]={}
        for threshold in thresholds:
            rr=[r for r in first if type(r.get('confidence')) in (int,float) and 0<=r['confidence']<=1 and r['confidence']>=threshold]
            correct=sum(r['choice']==answer_key[r['candidate_id']] for r in rr)
            result[model][str(threshold)]={'retained':len(rr),'correct':correct,
                                         'accuracy_retained':correct/len(rr) if rr else None,
                                         'coverage_scheduled':len(rr)/scheduled}
    return result
