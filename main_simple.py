import glob
import fugashi
import re
import multiprocessing
import csv


tagger = fugashi.Tagger()
is_head = re.compile(r'^-+\n', flags=re.DOTALL|re.M)

phonemes = {t[0]:t[1].strip() for t in [a.split('\t') for a in list(open('phonemes.txt', encoding='utf-8', mode='r'))]}


def kana_to_phonemes(s: str):
    p = list("".join(phonemes[c] for c in s))
    for i in range(0, len(p)):
        if p[i] == 'N':
            if i+1 >= len(p):
                # 文末の「ん」はNとする
                break
            elif p[i+1] in 'kg':
                # 軟口蓋音の前の「ん」はng
                p[i] = 'G'
            elif p[i+1] in 'ztcdnr':
                # 歯茎音の前の「ん」はn、ただしサ行の前はN
                p[i] = 'n'
            elif p[i+1] in 'YZC':
                # 硬口蓋音の前の「ん」はY (nj)
                p[i] = 'Y'
            elif p[i+1] in 'pbmv':
                # 両唇音の前の「ん」はm ※なお日本語にfは認めません(めんどいから・・・)
                p[i] = 'm'
            elif p[i+1] in 'aiueojhwsSN':
                # 母音、半母音、サ行、は行の前の「ん」は鼻母音化のNとする
                # N の前のNは面倒なのでNのままにする
                pass
            else:
                raise # 想定できてない場合エラーに
    return p


def to_kana(lines: list):
    result = ""
    for s in lines:
        parsed = tagger(s)
        result += "".join(w.feature.pron or "" for w in tagger(s))
    return result

def clean(lines: list):
    in_header = True
    sep = False

    for line in lines:
        if sep and line == '\n' and in_header:
            in_header = False
            continue

        sep = is_head.match(line) is not None

        if not in_header:
            if line.startswith('底本'):
                return
            yield line



def parse(file: str):
    count = {}
    try:
        with open(file, mode='r', encoding='cp932') as f:
            lines = list(clean(list(f)))
            kana = to_kana(lines)
            phonemes = kana_to_phonemes(kana)
            for p in phonemes:
                if p in 'aiueo':
                    continue
                count[p] = count.get(p, 0) + 1
    except UnicodeDecodeError:
        # 文字コードエラーで開けないファイルは諦める
        pass

    return count        

def main():
    global total
    
    files = list(glob.glob('/aozorabunko_text/**/*.txt', recursive=True))
    pools = multiprocessing.Pool()
    total = len(files)

    results = pools.map(parse, files)

    count = {}

    for result in results:
        for k, v in result.items():
            if k not in count:
                count[k] = v
            else:
                count[k] += v
    
    with open('result.txt', 'w') as f:
        cw = csv.writer(f)
        cw.writerow(['phoneme', 'count'])
        for k, v in count.items():
            print(f'{k}\t{v}')
            cw.writerow([k, v])
   

if __name__ == "__main__":
    main()