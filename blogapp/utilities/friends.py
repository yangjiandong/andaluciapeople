from os.path import dirname
import pickle

relations = {
    'me':           1,

    #friendship*
    'contact':      2,
    'acquaintance': 4,
    'friend':       8,

    #physical
    'met':          16,

    #professional
    'co-worker':    32,
    'colleague':    64,

    #geographical*
    'co-resident':  128,
    'neighbour':    256,

    #family*
    'child':        512,
    'parent':       1024,
    'sibling':      2048,
    'spouse':       4096,
    'kin':          8192,

    #romantic
    'muse':         16384,
    'crush':        32768,
    'date':         65536,
    'sweatheart':   131072
}

def get_list():
    f = open(dirname(__file__)+'/friends')
    friends = pickle.load(f)
    f.close()
    return friends

def rel_encode(rel_str):
    out = 0
    rel_lst = rel_str.split(' ')
    for rel in rel_lst:
        if rel:
            out = out + relations[rel]
    return out

def rel_decode(rel_int):
    out = ''
    rel_int = int(rel_int)
    for value in relations.keys():
        if (rel_int & relations[value]):
            out = out + value + ' '
    return out.rstrip()