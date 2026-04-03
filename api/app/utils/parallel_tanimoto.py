from argparse import ArgumentParser
from multiprocessing import Pool
from aiomultiprocess import Pool as aPool
import os.path as op
import numpy as np
import asyncio
import shutil
import csv
import os

from rdkit import Chem, DataStructs
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem, rdMolAlign
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers

try: from app.utils.timestamp import shanghai_time, to_timestamp
except ImportError: from timestamp import shanghai_time, to_timestamp


class Similarity:
    def __init__(self, args):
        self.args = args
        self.fp = None
        self.nBits = 2048

    # --- sync ----------------------
    async def flatting(self, scores, future):
        for fut in future:
            scores.append(fut)

    def calc_bulk(self, partitions):
        scores, fps = [], []
        indices_error = []
        for i, line in enumerate(partitions):
            try:
                m = Chem.MolFromSmiles(line[0])
                _fp = AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=self.nBits, useFeatures=True)
            except:
                indices_error.append(i)
                continue
            fps.append(_fp)
        if len(fps):
            try: scores = DataStructs.BulkTanimotoSimilarity(self.fp, fps)
            except: scores = [0.0 for _ in fps]
        fps = None
        if len(indices_error):
            for index in indices_error:
                scores.insert(index, 0.0)
        return scores

    # --- async ---------------------
    async def scoring_chunk(self, i, fps, indices_error, line):
        try:
            m = Chem.MolFromSmiles(line[0])
            _fp = AllChem.GetMorganFingerprintAsBitVect(m, radius=2, nBits=self.nBits, useFeatures=True)
        except:
            indices_error.append(i)
            return
        fps.append(_fp)

    # async def await_calc_bulk(self, partitions, fps, indices_error):
    #     await asyncio.gather(*[self.scoring_chunk(i, fps, indices_error, line) for i, line in enumerate(partitions)])

    async def calc_bulk_async(self, partitions):
        scores, fps = [], []
        indices_error = []

        # https://stackoverflow.com/questions/62469183/multithreading-inside-multiprocessing-in-python
        # asyncio.run(self.await_calc_bulk(partitions, fps, indices_error))
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

    # https://www.rdkit.org/docs/GettingStartedInPython.html
    async def make_png(self, png, mol):
        # d = rdMolDraw2D.MolDraw2DSVG(300, 300) # svg
        d = rdMolDraw2D.MolDraw2DCairo(300, 300) # png
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
        d.WriteDrawingText(png) # e.g: 'test.png'

    # def make_pdb(self, pdb, pmol):
    async def make_pdb(self, pdb, pmol):
        mol = Chem.AddHs(pmol)
        cids = AllChem.EmbedMultipleConfs(mol, numConfs=1, pruneRmsThresh=0.5, randomSeed=42)
        mp = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant='MMFF94s')

        res = []
        for cid in cids:
            ff = AllChem.MMFFGetMoleculeForceField(mol, mp, confId=cid)
            if ff:
                e = ff.CalcEnergy()
                res.append((cid, e))
        if len(res):
            sorted_res = sorted(res, key=lambda x:x[1])
            rdMolAlign.AlignMolConformers(mol)
            for cid, e in sorted_res:
                # for k, v in props.items():
                #     mol.SetProp(k, str(v))
                mol.SetProp('Conf_Energy', str(e))
                mol.SetProp('Conf_idx', str(cid))
        else:
            # for k, v in props.items():
            #     mol.SetProp(k, str(v))
            mol.SetProp('Conf_Energy', '-')
            mol.SetProp('Conf_idx', '-')

        Chem.MolToPDBFile(mol, pdb)


    async def run(self):
        is_need_pngs = self.args.is_need_pngs
        is_need_pdbs = self.args.is_need_pdbs
        is_show_time_open_file = self.args.is_show_time_open_file
        is_show_time_logic = self.args.is_show_time_logic
        cpu = self.args.cpu
        rank = self.args.rank
        smile = self.args.smile
        lib = self.args.lib
        save_to = self.args.save_to

        path, _ = op.split(save_to)

        if is_need_pngs:
            pngs_dir = op.join(path, 'pngs')
            if op.exists(pngs_dir):
                shutil.rmtree(pngs_dir, ignore_errors=True)
            os.makedirs(pngs_dir, exist_ok=True)

        if is_need_pdbs:
            pdbs_dir = op.join(path, 'pdbs')
            if op.exists(pdbs_dir):
                shutil.rmtree(pdbs_dir, ignore_errors=True)
            os.makedirs(pdbs_dir, exist_ok=True)

        self.fp = AllChem.GetMorganFingerprintAsBitVect(Chem.MolFromSmiles(smile), radius=2, nBits=self.nBits, useFeatures=True)

        # Open File -----------------
        if is_show_time_open_file:
            start_time_open_file = shanghai_time()
            ts_start_open_file = int(to_timestamp(start_time_open_file))

        header, smiles = None, []
        with open(lib, 'r') as f:
            for line in f:
                _line = line.rstrip().split()
                if ',' in line:
                    _line = line.rstrip().split(',')
                if '\t' in line:
                    _line = line.rstrip().split('\t')
                if line.startswith(('SMILE', 'Smile', 'smile')):
                    header = _line
                    header[0] = 'Smiles'
                    continue
                smiles.append(_line) # _line[0] is smiles

        if is_show_time_open_file:
            end_time_open_file = shanghai_time()
            ts_end_open_file = int(to_timestamp(end_time_open_file))

            print(f'start_time_open_file: {start_time_open_file}')
            print(f'end_time_open_file: {end_time_open_file}')
            print(f'consume_time_open_file: {ts_end_open_file-ts_start_open_file} secs.')

        # ----------------------------
        if is_show_time_logic:
            start_time_logic = shanghai_time()
            ts_start_logic = int(to_timestamp(start_time_logic))            

        # ----------------------------
        len_partitions = len(smiles)
        if len_partitions < rank:
            rank = len_partitions

        partitions_numpy = np.array(smiles, dtype=object)
        split = cpu if len_partitions >= cpu else len_partitions
        parts = np.array_split(partitions_numpy, split)
        partitions_numpy = None

        # ----------------------------
        scores = []
        len_smiles = len_partitions
        if len_smiles < 1200000:
            pool = Pool(split)
            futures = pool.map(self.calc_bulk, parts)
            pool.close()
            pool.join()
            parts = None #!NEW, not try
            await asyncio.gather(*[self.flatting(scores, future) for future in futures])
            futures = None
        else:
            async with aPool(split) as pool:
                async for result in pool.map(self.calc_bulk_async, parts):
                    scores.extend(result)
            result = None
            parts = None

        len_scores = len(scores)

        # print(f'len(smiles): {len(smiles)}')
        # print(f'len(scores): {len(scores)}')

        # ----------------------------
        # sorted_indices = sorted(range(len_scores), key=lambda i: scores[i])
        # reversed_indices = list(reversed(sorted_indices))
        # reversed_indices = reversed_indices[:rank]
        reversed_indices = sorted(range(len_scores), key=lambda i: scores[i], reverse=True)
        reversed_indices = reversed_indices[:rank]

        # Save CSV
        if header is None:
            header = ['-' for _ in smiles[0]]
            header[0] = 'Smiles'
            header.insert(1, 'Scores')
        else:
            header.insert(1, 'Scores')

        # ----------------------------
        if is_need_pngs: mols_png = []
        if is_need_pdbs: mols_pdb = []

        with open(save_to, 'w', newline= '', errors='ignore') as f:
            writer = csv.writer(f)
            writer.writerow(header)

            for i in range(rank):
                index = reversed_indices[i]
                line = smiles[index]
                line.insert(1, str(scores[index]))
                writer.writerow(line)

                if (is_need_pngs or is_need_pdbs) and i < 16:
                    mol = Chem.MolFromSmiles(line[0])

                if is_need_pngs and i < 16:
                    png = op.join(pngs_dir, f'{str(i+1).zfill(4)}.png')
                    mols_png.append([png, mol])

                if is_need_pdbs and i < 16:
                    pdb = op.join(pdbs_dir, f'{str(i+1).zfill(4)}.pdb')
                    # props = mol.GetPropsAsDict()

                    for pmol in EnumerateStereoisomers(Chem.MolFromSmiles(Chem.MolToSmiles(mol, isomericSmiles=False))):
                        # tmp_mol = [(prop, mol.GetProp(prop)) for prop in mol.GetPropNames()]
                        # tmp_mol.insert(0, ('_Name', mol.Get))
                        # tmp_mol.insert(0, pmol)
                        # mols.append(tmp_mol)
                        mols_pdb.append([pdb, pmol])

        if is_show_time_logic:
            end_time_logic = shanghai_time()
            ts_end_logic = int(to_timestamp(end_time_logic))

            print(f'start_time_logic: {start_time_logic}')
            print(f'end_time_logic: {end_time_logic}')
            print(f'consume_time_logic: {ts_end_logic-ts_start_logic} secs.')

        if is_need_pngs:
            async with aPool(split) as pool:
                async for result in pool.starmap(self.make_png, mols_png):
                    pass

        if is_need_pdbs:
            # pool = Pool(split)
            # futures = pool.starmap_async(self.make_pdb, mols)
            # pool.close()
            # pool.join()
            async with aPool(split) as pool:
                async for result in pool.starmap(self.make_pdb, mols_pdb):
                    pass

        # sys.stdout.write(json.dumps(scores))


#! python parallel_tanimoto.py --is-need-pngs --is-need-pdbs --cpu 100 --rank 1000 --smile "CCCOc1ccc(OC(=O)c2cccc([N+](=O)[O-])c2)cc1" --lib /share1-100G/fanny/storage/api/app/assets/similarity/libraries/CHEMBL29_part1-364620.smi --save-to /share1-100G/fanny/storage/api/app/assets/similarity/parallel/20251126_110218_1/example-1.csv
#! python parallel_tanimoto.py --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "CCCOc1ccc(OC(=O)c2cccc([N+](=O)[O-])c2)cc1" --lib /share1-100G/fanny/storage/api/app/assets/similarity/libraries/CHEMBL29_part1-364620.smi --save-to /share1-100G/fanny/storage/api/app/assets/similarity/parallel/20251126_110218_1/example-1.csv

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--is-need-pngs', action='store_true', dest='is_need_pngs')
    parser.add_argument('--is-need-pdbs', action='store_true', dest='is_need_pdbs')
    parser.add_argument('--is-show-time-open-file', action='store_true', dest='is_show_time_open_file')
    parser.add_argument('--is-show-time-logic', action='store_true', dest='is_show_time_logic')
    parser.add_argument('--cpu', type=int, required=True)
    parser.add_argument('--rank', type=int, required=True)
    parser.add_argument('--smile', type=str, required=True)
    parser.add_argument('--lib', type=str, required=True)
    parser.add_argument('--save-to', type=str, dest='save_to', required=True)

    args = parser.parse_args()

    asyncio.run(Similarity(args).run())

