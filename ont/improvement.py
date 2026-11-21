"""Offline policy improvement with held-out paired evaluations; never edits production."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


def evaluate(records, baseline, candidate, min_pairs=20, min_gain=0.02, confidence=0.95):
    """Paired bootstrap lower bound with independent safety and quality gates."""
    if min_pairs < 2 or not math.isfinite(min_gain) or min_gain < 0: raise ValueError('Invalid evaluation thresholds')
    if baseline == candidate: raise ValueError('Candidate must differ from baseline')
    if not 0.5 < confidence < 1: raise ValueError('Invalid confidence')
    pairs={}
    for r in records:
        if r['split']!='holdout' or r['policy'] not in (baseline,candidate):continue
        key=(r['task'],r['seed'])
        if r['policy'] in pairs.setdefault(key,{}):raise ValueError('Duplicate task/seed/policy')
        cost=float(r['cost']);latency=float(r['latency']);quality=float(r['quality'])
        if not all(math.isfinite(v) for v in (cost,latency,quality)) or cost<0 or latency<0 or not 0<=quality<=1:raise ValueError('Invalid metrics')
        if type(r['safe']) is not bool:raise ValueError('Safety must be boolean')
        pairs[key][r['policy']]=r
    complete=[p for p in pairs.values() if len(p)==2]
    if len(complete)!=len(pairs):raise ValueError('Unpaired holdout records')
    # Count independent tasks, not repeated seeds, as units of uncertainty.
    by_task={}
    for p in complete:
        b,c=p[baseline],p[candidate]
        reward=lambda r:r['quality']-0.1*min(r['cost']/10,1)-0.05*min(r['latency']/600,1)
        by_task.setdefault(b['task'],[]).append(reward(c)-reward(b))
    gains=[statistics.mean(v) for v in by_task.values()]
    safety=all(p[candidate]['safe'] for p in complete)
    quality=all(p[candidate]['quality']>=p[baseline]['quality'] for p in complete)
    rng=random.Random(0)
    samples=sorted(statistics.mean(rng.choices(gains,k=len(gains))) for _ in range(2000)) if gains else []
    lower=samples[int((1-confidence)*len(samples))] if samples else None
    eligible=len(gains)>=min_pairs and safety and quality and lower is not None and lower>=min_gain
    return {'baseline':baseline,'candidate':candidate,'independent_tasks':len(gains),'pairs':len(complete),
            'mean_gain':statistics.mean(gains) if gains else None,'lower_bound':lower,
            'confidence':confidence,'safety_passed':safety,'quality_passed':quality,
            'eligible_for_review':eligible,'promoted':False}


class Bandit:
    """Tabular UCB policy selector; a lightweight online RL primitive for evaluation only."""
    def __init__(self,arms):
        if not arms or len(set(arms))!=len(arms):raise ValueError('Unique arms required')
        self.stats={arm:[0,0.0] for arm in arms}
    def choose(self):
        for arm,(n,_) in self.stats.items():
            if not n:return arm
        total=sum(n for n,_ in self.stats.values())
        return max(self.stats,key=lambda a:self.stats[a][1]/self.stats[a][0]+math.sqrt(2*math.log(total)/self.stats[a][0]))
    def observe(self,arm,reward):
        if not math.isfinite(reward) or not -1<=reward<=1:raise ValueError('Reward must be finite in [-1,1]')
        self.stats[arm][0]+=1;self.stats[arm][1]+=reward


def main():
    p=argparse.ArgumentParser();p.add_argument('dataset');p.add_argument('--baseline',required=True);p.add_argument('--candidate',required=True)
    p.add_argument('--output',required=True);a=p.parse_args()
    raw=Path(a.dataset).read_bytes();records=json.loads(raw)
    report=evaluate(records,a.baseline,a.candidate)
    report['dataset_sha256']=hashlib.sha256(raw).hexdigest()
    Path(a.output).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
