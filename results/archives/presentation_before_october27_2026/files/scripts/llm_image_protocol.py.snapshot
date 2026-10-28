"""Answer-free reconstruction of the four image LLM request profiles; no network."""
import base64

MODELS={'sol':'openai/gpt-6-sol','sonnet':'anthropic/claude-sonnet-5.5',
        'opus':'anthropic/claude-opus-5','qwen':'qwen3.8-max'}


def payload(mid,q,images):
    text=q['question']+'\n\nRules: '+q['rules']+'\n\nOptions:\n'
    text+='\n'.join(o['id']+': '+o['text'] for o in q['options'])
    text+='\n\nReturn only the numeric option ID, without explanation.'
    encoded=[base64.b64encode(raw).decode() for raw in images]
    if mid in ('sonnet','opus'):
        content=[dict(type='text',text=text)]+[dict(type='image',source=dict(type='base64',media_type='image/png',data=x)) for x in encoded]
        body=dict(model=MODELS[mid],messages=[dict(role='user',content=content)],max_tokens=16,stream=False,
            thinking={'type':'between_tools' if mid=='sonnet' else 'disabled'},
            output_config=dict(effort='high',format=dict(type='json_schema',schema={
                'type':'object','properties':{'choice':{'type':'string','enum':[o['id'] for o in q['options']]}},
                'required':['choice'],'additionalProperties':False})),
            provider={'only':['anthropic'],'allow_fallbacks':False,'require_parameters':True})
        if mid=='opus':body['provider']['ignore']=['anthropic/fast']
        return body
    content=[dict(type='text',text=text)]+[dict(type='image_url',image_url={'url':'data:image/png;base64,'+x}) for x in encoded]
    body=dict(model=MODELS[mid],messages=[dict(role='user',content=content)],max_tokens=16,stream=False)
    if mid=='qwen':body['reasoning_effort']='none'
    else:body.update(usage={'include':True},reasoning={'enabled':False,'effort':'none'},service_tier='default',
        provider={'only':['openai'],'ignore':['openai/flex','openai/fast'],'allow_fallbacks':False,'require_parameters':True})
    return body
