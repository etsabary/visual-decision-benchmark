"""Code-native SVG figures for the completed private five-way report."""
from html import escape
import json
from benchmark import ROOT
OUT = ROOT / "figures"
SAVED = json.loads((ROOT / "results/summary.json").read_text())
ALL_MODELS = tuple(SAVED["all_model_ids"])
FAMILIES = SAVED["families"]
SHORT = dict(zip(ALL_MODELS, ("Jev Decisions", "Luna Decisions", "Luna regular", "5.4 nano", "Gemini Flash-Lite")))


def label(x,y,value,size=17,anchor="start",fill="#182432",weight="400"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" text-anchor="{anchor}" fill="{fill}" font-weight="{weight}">{escape(str(value))}</text>'


def start(title,description):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="1220" height="1220" viewBox="0 0 1220 1220" role="img"><title>{escape(title)}</title><desc>{escape(description)}</desc><rect width="1220" height="1220" fill="#fff"/>'


def plot(s,out=OUT):
    svg=start("Twenty abilities, five configurations","Each cell is correct out of ten scheduled questions; test date 15 October 2026.")
    svg+=label(40,48,"Image-grounded decisions · 200 questions",30,weight="700")
    svg+=label(40,80,"15 October 2026 · same C1 images and frozen keys · correct / 10 per family",18)
    xs=[590,720,850,980,1110]
    for x,m in zip(xs,ALL_MODELS):
        name=SHORT[m].split()
        svg+=label(x,122,' '.join(name[:-1]),17,"middle",weight="700")
        svg+=label(x,145,name[-1],17,"middle",weight="700")
    for i,(fid,title) in enumerate(FAMILIES.items()):
        y=164+i*45
        svg+=label(40,y+28,f"{fid}  {title}",18)
        for x,m in zip(xs,ALL_MODELS):
            value=s["models"][m]["groups"]["family_id"][fid]["correct_first"]
            t=value/10
            rgb=tuple(round(a+(b-a)*t) for a,b in zip((244,238,232),(31,103,111)))
            color='#'+''.join(f'{v:02x}' for v in rgb)
            svg+=f'<rect x="{x-58}" y="{y}" width="116" height="40" rx="5" fill="{color}"/>'
            svg+=label(x,y+28,f"{value}/10",20,"middle","#fff" if value>=6 else "#182432",weight="700")
    svg+=label(40,1110,"Failures stay in the denominator. Small family samples describe this bank, not general reliability.",18)
    svg+=label(40,1140,"General LLMs: reasoning OFF, 32-token option-ID ceiling. Decisions use typed choices.",18)
    svg+=label(40,1170,"Luna endpoints may use different checkpoints; this is not a same-weights serving-mode experiment.",18)
    (out/"abilities.svg").write_text(svg+'</svg>')
    svg=start("Accuracy, latency and cost on two hundred image questions","Separate zero-based horizontal scales; latency is median full response and cost is known core total divided by 200.")
    svg+=label(40,48,"Quality, speed and cost · same 200 questions",30,weight="700")
    svg+=label(40,80,"15 October 2026 · first-attempt accuracy · route timings · returned USD",18)
    specs=[("Correct answers (%)",lambda d:d["accuracy_scheduled"]*100,100,lambda v:f"{v:.1f}%"),
           ("Median full response (seconds)",lambda d:d["latency_first_all_ms"]["median"]/1000,None,lambda v:f"{v:.3f} s"),
           ("Reported cost per 1,000 questions (USD)",lambda d:d["core_cost_per_scheduled_usd"]*1000,None,lambda v:f"${v:.4f}")]
    colors=["#246977","#4b8792","#6474b8","#a0754d","#739343"]
    for panel,(title,get,maximum,fmt) in enumerate(specs):
        y0=120+panel*320
        svg+=label(40,y0,title,22,weight="700")
        limit=maximum or max(get(s["models"][m]) for m in ALL_MODELS)*1.15
        for i,m in enumerate(ALL_MODELS):
            y=y0+28+i*43;d=s["models"][m];v=get(d);width=710*v/limit
            svg+=label(40,y+22,SHORT[m],18)
            svg+=f'<rect x="270" y="{y}" width="{width:.3f}" height="29" rx="4" fill="{colors[i]}"/>'
            star='*' if panel==2 and d["core_cost"]["missing_records"] else ''
            svg+=label(280+width,y+22,fmt(v)+star,18)
        svg+=label(270,y0+278,"0",15)
        svg+=label(980,y0+278,fmt(limit),15,"end")
    svg+=label(40,1110,"Cost is normalized for readability, not a 1,000-question projection or vendor list price.",18)
    svg+=label(40,1140,"* Missing error-response charges: known cost is a lower bound. Includes retries and cache writes.",18)
    svg+=label(40,1170,"Different routes/checkpoints and test sessions limit causal claims. General LLM reasoning was disabled.",18)
    (out/"tradeoffs.svg").write_text(svg+'</svg>')


if __name__ == "__main__":plot(json.loads((ROOT/"results/summary.json").read_text()))
