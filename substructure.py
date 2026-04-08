from argparse import ArgumentParser
from multiprocessing import Pool
from aiomultiprocess import Pool as aPool
from concurrent.futures import ThreadPoolExecutor
import os.path as op
import numpy as np
import asyncio
import shutil
import csv
import os

from rdkit import Chem
from rdkit.Chem.Draw import rdMolDraw2D

from timestamp import shanghai_time, to_timestamp


class Substructure:
    def __init__(self, args):
        self.args = args
        self.mol = None

    # --- sync ----------------------
    async def flatting(self, indices, future):
        for fut in future:
            indices.append(fut)

    def chunk(self, line):
        try:
            m = Chem.MolFromSmiles(line[0])
            if m.HasSubstructMatch(self.mol, useChirality=True):
                return line[-1]
            else: return -1
        except: return -1

    def calc_bulk(self, partitions):
        # e = ThreadPoolExecutor(max_workers=1000)
        e = ThreadPoolExecutor() # max_workers = min(32, (os.cpu_count() or 1) + 4)
        return list(e.map(self.chunk, partitions)) # return list
    
    # --- async ---------------------
    async def chunk_async(self, line):
        try:
            m = Chem.MolFromSmiles(line[0])
            if m.HasSubstructMatch(self.mol, useChirality=True):
                return line[-1]
            else: return -1
        except: return -1

    async def calc_bulk_async(self, partitions):
        return await asyncio.gather(*[self.chunk_async(partition) for partition in partitions])

    async def make_png(self, png, mol):
        hit_ats = list(mol.GetSubstructMatch(self.mol))
        hit_bonds = []
        for bond in self.mol.GetBonds():
            aid1 = hit_ats[bond.GetBeginAtomIdx()]
            aid2 = hit_ats[bond.GetEndAtomIdx()]
            hit_bonds.append(mol.GetBondBetweenAtoms(aid1,aid2).GetIdx())

        # d = rdMolDraw2D.MolDraw2DSVG(300, 300) # svg
        d = rdMolDraw2D.MolDraw2DCairo(300, 300) # png
        rdMolDraw2D.PrepareAndDrawMolecule(d, mol, highlightAtoms=hit_ats, highlightBonds=hit_bonds)
        d.WriteDrawingText(png) # e.g: 'test.png'

    async def run(self):
        is_need_pngs = self.args.is_need_pngs
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
        
        self.mol = Chem.MolFromSmarts(smile)

        # Open File -----------------
        if is_show_time_open_file:
            start_time_open_file = shanghai_time()
            ts_start_open_file = int(to_timestamp(start_time_open_file))

        # with Manager() as manager:
        #     indices = manager.list() # shared list
        header, smiles = None, []
        with open(lib, 'r') as f:
            i = 0
            for line in f:
                _line = line.rstrip().split()
                if ',' in line:
                    _line = line.rstrip().split(',')
                if '\t' in line:
                    _line = line.rstrip().split('\t')
                if line.startswith(('SMILE', 'Smile', 'smile')):
                    _line.append('-')
                    _line[0] = 'Smiles'
                    header = _line
                    continue
                # _line.extend([i, indices]) # _line[0] is smiles, _line[-2] is index, _line[-1] is shared list
                _line.append(i)
                smiles.append(_line)
                i += 1

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
        indices = []
        len_smiles = len_partitions

        # We use Parallel Sync when the smiles less than 1.200.000
        if len_smiles < 1200000:
            pool = Pool(split)
            futures = pool.map(self.calc_bulk, parts)
            pool.close()
            pool.join()
            parts = None
            await asyncio.gather(*[self.flatting(indices, future) for future in futures])
            futures = None

        # or We use Parallel Async
        else:
            async with aPool(split) as pool:
                async for result in pool.map(self.calc_bulk_async, parts):
                    indices.extend(result)
            result, parts = None, None

        # ----------------------------
        indices = np.array(indices)
        indices = indices[indices != -1]
        indices = indices[:rank]

        len_indices = len(indices)

        # ----------------------------
        if not len_indices:
            # Not find substructure in the library, then clear the candidate result file(s)/directory(s)
            if op.exists(save_to):
                os.remove(save_to)

            pngs_dir = op.join(path, 'pngs')
            if op.exists(pngs_dir):
                shutil.rmtree(pngs_dir, ignore_errors=True)

            print("NOT FOUND SUBSTRUCTURE.")
            return


        if len_indices < rank:
            rank = len_indices

        # Save CSV
        if header is None:
            header = ['-' for _ in smiles[0]]
            header[0] = 'Smiles'

        # ----------------------------
        if is_need_pngs: mols_png = []

        with open(save_to, 'w', newline= '', errors='ignore') as f:
            writer = csv.writer(f)
            writer.writerow(header[:-1])

            for i in range(rank):
                line = smiles[indices[i]]
                writer.writerow(line[:-1])

                if is_need_pngs:
                    mol = Chem.MolFromSmiles(line[0])
                    png = op.join(pngs_dir, f'{str(i+1).zfill(4)}.png')
                    mols_png.append([png, mol])


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


"""
1. Simples (Without Result images .png)

   Example input:
      number cpu usage = 100
      top rank = 1000
      input query smile = "c1ccccc1Nc2ncnc(c23)cccc3"
      library dataset = "./example/CHEMBL29_part1-364620.smi"
      save result csv = "./result/substructure-result.csv"


      python substructure.py --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "c1ccccc1Nc2ncnc(c23)cccc3" --lib example/CHEMBL29_part1-364620.smi --save-to result/substructure-result.csv

      
2. Output contain .pngs (we limited maximum rank to 9999 rank molecules)

      python substructure.py --is-need-pngs --is-show-time-open-file --is-show-time-logic --cpu 100 --rank 1000 --smile "c1ccccc1Nc2ncnc(c23)cccc3" --lib example/CHEMBL29_part1-364620.smi --save-to result/substructure-result.csv
"""


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--is-need-pngs', action='store_true', dest='is_need_pngs')
    parser.add_argument('--is-show-time-open-file', action='store_true', dest='is_show_time_open_file')
    parser.add_argument('--is-show-time-logic', action='store_true', dest='is_show_time_logic')
    parser.add_argument('--cpu', type=int, required=True)
    parser.add_argument('--rank', type=int, required=True)
    parser.add_argument('--smile', type=str, required=True)
    parser.add_argument('--lib', type=str, required=True)
    parser.add_argument('--save-to', type=str, dest='save_to', required=True)

    args = parser.parse_args()

    asyncio.run(Substructure(args).run())

