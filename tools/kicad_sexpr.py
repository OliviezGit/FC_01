"""Small lossless s-expression reader for KiCad structural validation (not ERC/DRC)."""
import re,json
class Atom(str):
    def __new__(cls,v,raw=None,start=-1,end=-1):
        x=str.__new__(cls,v);x.raw=raw if raw is not None else json.dumps(v,ensure_ascii=False);x.start=start;x.end=end;return x
class Node(list):pass
def parse(text):
    stack=[];roots=[]
    for m in re.finditer(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',text):
        t=m.group()
        if t=='(':
            n=Node();n.start=m.start()
            (stack[-1] if stack else roots).append(n);stack.append(n)
        elif t==')':
            if not stack:raise ValueError('Unexpected closing bracket')
            stack.pop().end=m.end()
        else:
            if not stack:raise ValueError('Token outside expression')
            v=json.loads(t,strict=False) if t.startswith('"') else t
            stack[-1].append(Atom(v,t,m.start(),m.end()))
    if stack or len(roots)!=1:raise ValueError('Unbalanced or multiple roots')
    return roots[0]
def children(n,k):return [x for x in n if isinstance(x,list) and x and x[0]==k]
def child(n,k,default=None):return next(iter(children(n,k)),default if default is not None else [k,''])
def props(n):return {x[1]:x[2] for x in children(n,'property')}
def q(s):return Atom(str(s))
def a(s):return Atom(str(s),str(s))
def dump(n,level=0):
    if not isinstance(n,list):return n.raw if isinstance(n,Atom) else json.dumps(n,ensure_ascii=False)
    if all(not isinstance(x,list) for x in n):return '('+' '.join(dump(x) for x in n)+')'
    out='('; first=True
    for x in n:
        out+=('' if first else '\n'+'  '*(level+1) if isinstance(x,list) else ' ')+dump(x,level+1);first=False
    return out+')'
def replace(text,edits):
    last=len(text)+1
    for start,end,value in sorted(edits,reverse=True):
        if end>last:raise ValueError('Overlapping edits')
        text=text[:start]+value+text[end:];last=start
    return text
def pin_nodes(n, unit=1, style=1):
    result=[]
    for s in children(n,'symbol'):
        tail=str(s[1]).rsplit('_',2)
        if len(tail)==3 and tail[1].isdigit() and tail[2].isdigit():
            if int(tail[1]) not in (0,unit) or int(tail[2]) not in (0,style):continue
        result.extend(children(s,'pin'))
    return result
def get_lib(c,libs):return libs.get(child(c,'lib_name')[1] or child(c,'lib_id')[1])
