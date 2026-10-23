"""Named, readable figures for the expanded native-image cohort. Offline only."""
from decimal import Decimal
import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'native_images_2026-10-20'
BLUE='#2176ae';INK='#182f43'

def speed_color(ms):
    return '#32916b' if ms<=500 else '#c49b26' if ms<=1000 else '#c56c35' if ms<=2000 else '#b54558'

def cost_color(v):
    return '#32916b' if v<=.05 else '#c49b26' if v<=.15 else '#c56c35' if v<=.5 else '#b54558'

def save(fig,name):
    for ext in ('png','svg'):fig.savefig(DATA/(name+'.'+ext),dpi=175,bbox_inches='tight',facecolor='white')
    svg=DATA/(name+'.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(fig)

def plot():
    d=json.loads((DATA/'summary.json').read_text());order=d['rank_order'];ss=[d['models'][m] for m in order]
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.hashsalt':'visual-decision-oct20'})
    fig,ax=plt.subplots(1,3,figsize=(16,1.8+len(ss)*.43),sharey=True,gridspec_kw={'width_ratios':[1.2,1,1.35]})
    y=np.arange(len(ss));labels=[s['label']+(' †' if s['reused'] else '') for s in ss]
    ax[0].barh(y,[100*s['accuracy'] for s in ss],color=BLUE,height=.65)
    ax[0].set_yticks(y,labels);ax[0].set_xlim(0,106);ax[0].invert_yaxis()
    ax[0].axvline(100*d['random_uniform_baseline'],color='#9aa7af',linestyle=':',linewidth=1)
    ax[0].set_title('Accuracy · all 200 questions',loc='left',fontweight='bold')
    for i,s in enumerate(ss):ax[0].text(100*s['accuracy']+1,i,f"{s['correct']}/200 · {s['accuracy']:.1%}",va='center',fontsize=9)
    ax[1].barh(y,[s['median_ms'] for s in ss],color=[speed_color(s['median_ms']) for s in ss],height=.65)
    ax[1].set_xlim(0,max(s['median_ms'] for s in ss)*1.45);ax[1].set_title('Median complete response · ms',loc='left',fontweight='bold')
    for i,s in enumerate(ss):ax[1].text(s['median_ms']+8,i,f"{s['median_ms']:.0f}",va='center',fontsize=9)
    paid=[float(s['core_cost_per_1000_known_usd']) for s in ss if not s['public_free_access']]
    xmax=max(paid)*1.60
    for i,s in enumerate(ss):
        if s['public_free_access']:
            ax[2].text(.01*xmax,i,'Free public access · not a metered $0 price',va='center',fontsize=8.5,color='#506479')
        else:
            v=float(s['core_cost_per_1000_known_usd']);missing=s['core_cost']['missing_api_records']
            ax[2].barh(i,v,color=cost_color(v),height=.65)
            ax[2].text(v+.012*xmax,i,f"${v:.4f}"+(' *' if missing else ''),va='center',fontsize=9)
    ax[2].set_xlim(0,xmax);ax[2].set_title('Known core cost / 1,000 questions · USD',loc='left',fontweight='bold')
    for a in ax:
        a.spines[['top','right','left']].set_visible(False);a.tick_params(axis='y',length=0)
        a.grid(axis='x',alpha=.13);a.set_axisbelow(True)
    fig.suptitle(f"Image-grounded decisions · {len(ss)} specialized models · 200 questions each",x=.05,y=1.03,ha='left',fontsize=19,fontweight='bold',color=INK)
    fig.text(.05,.01,'Tested Oct 20, 2026; † original Oct 15 measurement reused. Same question bank and exact image bytes.\n'
        'Cost / 1,000 normalizes actual 200-question runs; * missing error charges make this a known lower bound.\n'
        'Green speed ≤500 ms; yellow ≤1 s; orange ≤2 s. Cost green ≤$0.05; yellow ≤$0.15; orange ≤$0.50; red above, per 1,000.\n'
        'Span-02 stopped above 2 s median; ScaleDown image route rejected input. Partial/excluded runs are not ranked.',fontsize=9,color='#4e6477',va='bottom')
    fig.tight_layout(rect=(0,.12,1,.97),w_pad=3);save(fig,'overview')
    cmap=LinearSegmentedColormap.from_list('accuracy',['#fff4d0','#d5ebce','#77c5c8','#338bac','#183f7a'])
    family_order=list(d['families'])
    sections=['Objects, space and routes','Transformations, rules and state','Reasoning from diagrams and documents','Comparison, perspective and uncertainty']
    for block in range(4):
        families=family_order[5*block:5*block+5]
        values=np.array([[s['families'][f]['correct']/10 for f in families] for s in ss])
        fig,a=plt.subplots(figsize=(12.5,2+len(ss)*.4))
        im=a.imshow(values,vmin=0,vmax=1,cmap=cmap,aspect='auto')
        a.set_yticks(range(len(ss)),labels);a.set_xticks(range(5),['\n'.join(textwrap.wrap(d['families'][f]['name'],24))+f'\n({f}, n=10)' for f in families])
        a.tick_params(length=0,pad=8)
        for i in range(len(ss)):
            for j in range(5):a.text(j,i,f'{int(values[i,j]*10)}/10',ha='center',va='center',fontsize=11,color='white' if values[i,j]>=.7 else INK)
        for spine in a.spines.values():spine.set_visible(False)
        bar=fig.colorbar(im,ax=a,pad=.025,fraction=.025);bar.set_ticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
        fig.suptitle(sections[block],x=.05,y=1.01,ha='left',fontsize=18,fontweight='bold',color=INK)
        fig.text(.05,-.025,'Same model order throughout. Every cell is correct / 10; a one-answer difference is ten percentage points.\n'
            'Small selected samples, not reliability guarantees. † Original Oct 15 measurement reused.',fontsize=9,color='#4e6477')
        fig.tight_layout();save(fig,'abilities_'+str(block+1))

if __name__=='__main__':plot()
