import json,re,sys,glob,os
def toks(s): return sorted(re.findall(r'\{[0-9A-F]{2}\}|%[0-9]*d[0-9]%|\{%[a-z_]+\}',s))
def check(chunk,out):
    src=json.load(open(chunk,encoding='utf-8'));o=json.load(open(out,encoding='utf-8'))
    errs=[]
    for e in src:
        k=str(e['i']);jp=e['jp']
        if k not in o: errs.append((k,'missing'));continue
        ko=o[k]
        if toks(jp)!=toks(ko): errs.append((k,'tokens',jp,ko))
        if re.search(r'[぀-ヺヽ-ヿ一-鿿]',ko): errs.append((k,'jp-left',ko))
        jl=max(len(x) for x in jp.split('\n'));kl=max(len(re.sub(r'\{[0-9A-F]{2}\}','',x)) for x in ko.split('\n'))
        if '\n' in jp and kl>jl+1: errs.append((k,'long-line',jl,kl,ko))
    return errs
if __name__=='__main__':
    for c in sys.argv[1:]:
        n=os.path.basename(c);e=check('chunks/'+n,'out/'+n) if os.path.exists('out/'+n) else [('-','no output')]
        print(n,len(e));[print('  ',x) for x in e[:15]]
