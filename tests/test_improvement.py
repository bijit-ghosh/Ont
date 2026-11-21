import unittest
from ont.improvement import evaluate,Bandit

class ImprovementTests(unittest.TestCase):
    def records(self):
        return [dict(task=str(i),seed=0,split='holdout',policy=p,quality=q,cost=1,latency=10,safe=True) for i in range(25) for p,q in [('base',0.7),('new',0.9)]]
    def test_gain_requires_review(self):
        r=evaluate(self.records(),'base','new');self.assertTrue(r['eligible_for_review']);self.assertFalse(r['promoted'])
    def test_safety_blocks_reward(self):
        rows=self.records();rows[1]['safe']=False;self.assertFalse(evaluate(rows,'base','new')['eligible_for_review'])
    def test_small_sample_and_training_do_not_promote(self):
        rows=self.records()[:4];self.assertFalse(evaluate(rows,'base','new')['eligible_for_review'])
        rows=self.records()
        for r in rows:r['split']='train'
        self.assertFalse(evaluate(rows,'base','new')['eligible_for_review'])
    def test_quality_regression_blocks(self):
        rows=self.records();rows[1]['quality']=0;self.assertFalse(evaluate(rows,'base','new')['eligible_for_review'])
    def test_duplicates_and_unpaired_fail(self):
        rows=self.records()
        for bad in [rows+rows[:1],rows[:-1]]:
            with self.assertRaises(ValueError):evaluate(bad,'base','new')
    def test_bandit_learns_and_rejects_invalid_rewards(self):
        b=Bandit(['a','b'])
        for _ in range(200):
            a=b.choose();b.observe(a,0.8 if a=='b' else 0.1)
        self.assertGreater(b.stats['b'][0],b.stats['a'][0])
        with self.assertRaises(ValueError):b.observe('a',float('nan'))
