#!/usr/bin/env python3
"""Measure the draft's declared opaque sRGB pairs; no UI compliance inferred."""
import json
from pathlib import Path

def luminance(color):
    values=[int(color[i:i+2],16)/255 for i in (1,3,5)]
    values=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in values]
    return sum(v*w for v,w in zip(values,(.2126,.7152,.0722)))

def ratio(a,b):
    x,y=sorted((luminance(a),luminance(b)))
    return (y+.05)/(x+.05)

if __name__=='__main__':
    root=Path(__file__).resolve().parent
    tokens=json.loads((root/'tokens.json').read_text())
    pairs=[(fg,bg,4.5) for fg in ('text','textSecondary','primary','accent','danger','success','warning')
           for bg in ('canvas','surface')]
    pairs += [('text','outgoing',4.5),('textSecondary','outgoing',4.5),
              ('onPrimary','primary',4.5),('onPrimary','primaryPressed',4.5),
              ('disabledText','surfaceMuted',4.5),('border','canvas',3),('border','surface',3),
              ('focus','canvas',3),('focus','surface',3)]
    results=[]
    for theme in ('light','dark'):
        for fg,bg,minimum in pairs:
            actual=ratio(tokens[theme][fg],tokens[theme][bg])
            results.append(dict(theme=theme,foreground=fg,background=bg,ratio=round(actual,4),
                                minimum=minimum,passes=actual>=minimum))
    output=dict(scope='declared opaque sRGB token pairs; no runtime or accessibility certification',
                status='PASS' if all(x['passes'] for x in results) else 'FAIL',pairs=results)
    print(json.dumps(output,indent=2))
    raise SystemExit(0 if output['status']=='PASS' else 1)
