from argparse import ArgumentParser
# from multiprocessing import Pool
from aiomultiprocess import Pool
import asyncio
import pickle
import json
import sys

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem


class Tanimoto:
    def __init__(self, args):
        self.args = args
        self.fp = None
        self.nBits = 2048

    async def scoring_chunk(self, i, fps, indices_error, line):
        try:
            m = Chem.MolFromSmiles(line[0])
            _fp = AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=self.nBits, useFeatures=True)
        except:
            indices_error.append(i)
            return
        fps.append(_fp)

    # def calc_bulk(self, partitions):
    async def calc_bulk(self, partitions):
        scores, fps = [], []
        indices_error = []

        await asyncio.gather(*[self.scoring_chunk(i, fps, indices_error, line) for i, line in enumerate(partitions)])
        # for i, line in enumerate(partitions):
        #     try:
        #         m = Chem.MolFromSmiles(line[0])
        #         _fp = AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=self.nBits, useFeatures=True)
        #     except:
        #         indices_error.append(i)
        #         continue
        #     fps.append(_fp)

        if len(fps):
            try: scores = DataStructs.BulkTanimotoSimilarity(self.fp, fps)
            except: scores = [0.0 for _ in fps]
        fps = None
        if len(indices_error):
            for index in indices_error:
                scores.insert(index, 0.0)
        return scores

    # async def scoring(self, scores, future):
    #     for fut in future:
    #         scores.append(fut)

    async def run(self):
        cpu = self.args.cpu
        smile = self.args.smile
        pkl = self.args.pkl

        self.fp = AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(smile), radius=2, nBits=self.nBits, useFeatures=True)

        with open(pkl, 'rb') as f:
            # partitions = pickle.load(f) # [(index, smiles), (..., ...), ...]
            partitions = pickle.load(f) # [smiles, ...]
        
        # ----------------------------
        # pool = Pool(cpu)
        # futures = pool.map(self.calc_bulk, partitions)
        # pool.close()
        # pool.join()
        scores = []
        async with Pool(cpu) as pool:
            async for result in pool.map(self.calc_bulk, partitions):
                scores.extend(result)
        # for future in futures:
        #     for fut in future:
        #         scores.append(fut)
        # await asyncio.gather(*[self.scoring(scores, future) for future in futures])

        sys.stdout.write(json.dumps(scores))


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--cpu', type=int, required=True)
    parser.add_argument('--smile', type=str, required=True)
    parser.add_argument('--pkl', type=str, required=True)

    args = parser.parse_args()

    asyncio.run(Tanimoto(args).run())
