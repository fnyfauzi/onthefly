from argparse import ArgumentParser
from multiprocessing import Pool
import os.path as op
import asyncio

from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers


class MakePdbs:
    def __init__(self, args):
        self.smiles = args.smiles
        self.pdbs_dir = args.pdbs_dir

    async def run(self):
        smiles = []
        for i, smile in enumerate(self.smiles.split(',')):
            smiles.append((i, smile))

        pool = Pool(16)
        pool.starmap(self.convert, smiles)
        pool.close()
        pool.join()

    def convert(self, i, smile):
        mol = Chem.MolFromSmiles(smile)
        pdb = op.join(self.pdbs_dir, f'{str(i+1).zfill(4)}.pdb')
        for pmol in EnumerateStereoisomers(Chem.MolFromSmiles(Chem.MolToSmiles(mol, isomericSmiles=False))):
            break
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



if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--smiles', type=str, required=True)
    parser.add_argument('--pdbs-dir', type=str, dest='pdbs_dir', required=True)

    args = parser.parse_args()

    asyncio.run(MakePdbs(args).run())

