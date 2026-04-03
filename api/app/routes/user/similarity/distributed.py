from __future__ import annotations
from collections import OrderedDict
from typing import List
import os.path as op
import numpy as np
import logging
import asyncio
import pickle
import shutil
import json
import csv
import os

from rdkit import Chem
from rdkit.Chem import Draw, AllChem, rdMolAlign
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import *
from app.utils.async_sender import async_send
from app.utils.timestamp import shanghai_time, to_timestamp, time_to_string

logger = logging.getLogger(__name__)

user_similarity_distributed_router = APIRouter(prefix="/user_similarity_distributed", tags=['user_similarity_distributed'])


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_distributed/files
class RequestModelFiles(BaseModel):
    offset: int
    limit: int

@user_similarity_distributed_router.get("/files", status_code=status.HTTP_200_OK)
async def getFiles(
    *,
    params: BaseModel = Depends(RequestModelFiles),
):
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Distributed: files.')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'distributed')
    sub_dirs = sorted(os.listdir(save_dir))

    # async.gather, later
    d = OrderedDict()
    for sub_dir in sub_dirs:
        files = op.join(save_dir, sub_dir)
        csv_file, pdb_file, png_file, smi_file = None, None, None, None
        lib_name = None,
        pdbs = None
        for file in sorted(os.listdir(files)):
            filepath = op.join(save_dir, sub_dir, file)
            if op.isfile(filepath):
                name, ext = op.splitext(file)
                if ext == ".csv":
                    csv_file = file
                elif ext == ".pdb":
                    pdb_file = file
                elif ext == ".png":
                    png_file = file
                elif ext == ".smi":
                    smi_file = file
                elif ext == ".txt":
                    lib_file = op.join(save_dir, sub_dir, 'lib.txt')
                    with open(lib_file, 'r') as f:
                        lib_name = f.read()
            else: # dir, "pdbs"
                pdbs_dir = op.join(save_dir, sub_dir, file)
                pdbs = sorted(os.listdir(pdbs_dir))
        d[sub_dir] = [csv_file, pdb_file, png_file, smi_file, lib_name, pdbs]

    logger.debug('Success Similarity Distributed: files.')
    return d


# TODO: ----------------------------------------
# POST: http://10.168.1.14:4178/user_similarity_distributed/upload
@user_similarity_distributed_router.post("/upload", status_code=status.HTTP_200_OK)
async def upload(
    *,
    files: List[UploadFile] = File(None),
):
    logger.debug('----------------------------')
    logger.debug('Similarity Distributed: upload.')
    # logger.debug(f'user.id: {user.id}')
    # logger.debug(f'user.username: {user.username}')

    curr_time = time_to_string(shanghai_time())

    isSmi = True
    for i, file in enumerate(files):
        try:
            sub_dir = f'{curr_time}_{i+1}'
            save_dir = op.join(settings.asset_dir, 'similarity', 'distributed', sub_dir)
            if op.exists(save_dir):
                shutil.rmtree(save_dir, ignore_errors=True)
            os.makedirs(save_dir, exist_ok=True)
            save_to = op.join(save_dir, file.filename)
            name, ext = op.splitext(file.filename)
            if ext != '.smi':
                isSmi = False
                break
            with open(save_to, 'wb') as f:
                shutil.copyfileobj(file.file, f)
            logger.debug(f'{i+1}. save_to: {save_to}')
        except Exception:
            logger.debug('Error saving file')
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Error saving file')
        finally:
            file.file.close()

        # Create PNG
        with open(save_to, 'r') as f:
            for line in f:
                if line.startswith(('SMILE', 'Smile', 'smile', 'Smiles', 'smiles')): continue
                _line = line.rstrip().split()
                if ',' in line:
                    _line = line.rstrip().split(',')
                elif '\t' in line:
                    _line = line.rstrip().split('\t')
                smile = _line[0]
                break
        im = Draw.MolToImage(Chem.MolFromSmiles(smile), size=(300,300), fitImage=True)
        save_to = op.join(save_dir, f'{name}.png')
        im.save(save_to)


    if not isSmi:
        for i, file in enumerate(files):
            sub_dir = f'{curr_time}_{i+1}'
            save_dir = op.join(settings.asset_dir, 'similarity', 'distributed', sub_dir)
            if op.exists(save_dir):
                shutil.rmtree(save_dir, ignore_errors=True)
    
    logger.debug('Success Similarity Distributed: upload.')
    return ""


# TODO: ----------------------------------------
# DELETE: http://10.168.1.14:4178/user_similarity_distributed/{sub_dir}
@user_similarity_distributed_router.delete("/{sub_dir}", status_code=status.HTTP_200_OK)
async def delete(
    *,
    sub_dir: str,
):
    logger.debug('----------------------------')
    logger.debug('Similarity Distributed: delete.')
    logger.debug(f'sub_dir: {sub_dir}')

    if sub_dir in ['datetime']:
        detail = "Abort, datetime is sample, unable to be deleted."
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    save_dir = op.join(settings.asset_dir, 'similarity', 'distributed')

    full_dir = op.join(save_dir, sub_dir)
    if not op.exists(full_dir):
        detail = f'Abort, {full_dir} does not exist.'
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    shutil.rmtree(full_dir, ignore_errors=True)
    logger.debug('Success Similarity Distributed: delete.')
    return ""


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_distributed/show-2d
def load_smi_with_props(filename, limit):
    all_props, headers = [], []
    with open(filename, 'r') as f:
        for line in f:
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            if '\t' in line:
                _line = line.rstrip().split('\t')

            if line.startswith(('SMILE', 'Smile', 'smile', 'Smiles', 'smiles')):
                headers = _line
            else:
                d = OrderedDict()
                for j, header in enumerate(headers):
                    d[header] = _line[j]
                all_props.append(d)

                if len(all_props) == limit:
                    break

    return all_props # props contain smiles

class RequestModelShow2D(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_distributed_router.get("/show-2d", status_code=status.HTTP_200_OK)
async def show2d(
    *,
    params: BaseModel = Depends(RequestModelShow2D),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Distributed: show-2d.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'distributed')
    full_dir = op.join(save_dir, sub_dir)

    # test.smi
    smi_file = op.join(full_dir, filename)
    test_props = []
    if op.exists(smi_file):
        test_props = load_smi_with_props(smi_file, 1) # props contain smiles, without header

    # test.csv (result similarity)    
    name, ext = op.splitext(filename)
    csv_file = op.join(full_dir, f'{name}.csv')
    result_props = []
    if op.exists(csv_file):
        result_props = load_smi_with_props(csv_file, limit)

    pdbs_dir = op.join(full_dir, 'pdbs')
    pdbs = []
    if op.exists(pdbs_dir):
        pdbs = sorted(os.listdir(pdbs_dir))
    
    logger.debug('Success Similarity Distributed: show-2d.')

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'test_props': test_props,
        'result_props': result_props,
        'pdbs': pdbs
        })


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_distributed/show-3d
class RequestModelShow3D(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_distributed_router.get("/show-3d", status_code=status.HTTP_200_OK)
async def show3d(
    *,
    params: BaseModel = Depends(RequestModelShow3D),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Distributed: show-3d.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'distributed')
    full_dir = op.join(save_dir, sub_dir)

    pdbs_dir = op.join(full_dir, 'pdbs')
    pdbs = []
    if op.exists(pdbs_dir):
        pdbs = sorted(os.listdir(pdbs_dir))
    
    logger.debug('Success Similarity Distributed: show-3d.')
    return pdbs[0:limit] if len(pdbs) else []




# TODO: ----------------------------------------
# POST: http://10.168.1.14:4178/user_similarity_distributed/parent
async def isToNode(node, sub_dir, cpu, smi, parts):
    if node == 1: server_url = '10.168.1.11'
    elif node == 2: server_url = '10.168.1.12'
    elif node == 3: server_url = '10.168.1.14'
    server_port = 4178
    path_url = "/user_similarity_distributed/child"
    access_token = None

    json_data = {'node': node, 'sub_dir': sub_dir, 'cpu': cpu, 'smi': smi, 'parts': parts}
    func_coro = async_send(method="post", server_url=server_url, server_port=server_port, path_url=path_url,
                           json=json_data,
                           content_type="application/json",
                           access_token=access_token,
                           timeout=1000000000)
    r = await asyncio.create_task(func_coro)
    # logger.debug(r.status_code, content)
    return json.loads(r.content)


async def make_pdb(mol):
    pdb, pmol = mol
    mol = Chem.AddHs(pmol)
    cids = AllChem.EmbedMultipleConfs(mol, numConfs=1, pruneRmsThresh=0.5, randomSeed=42)
    mp = AllChem.MMFFGetMoleculeProperties(mol, mmffVariant='MMFF94s')

    res = []
    for cid in cids:
        ff = AllChem.MMFFGetMoleculeForceField(mol, mp, confId=cid)
        if ff:
            e = ff.CalcEnergy()
            res.append((cid, e))
    if res:
        sorted_res = sorted(res, key=lambda x:x[1])
        rdMolAlign.AlignMolConformers(mol)
        for cid, e in sorted_res:
            # for k, v in props.items():
            #     mol.SetProp(k, str(v))
            mol.SetProp('Conf_Energy', str(e))
            mol.SetProp('Conf_idx', str(cid))
    # else:
    #     for k, v in props.items():
    #         mol.SetProp(k, str(v))
    #     mol.SetProp('Conf_Energy', '-')
    #     mol.SetProp('Conf_idx', '-')

    Chem.MolToPDBFile(mol, pdb)


async def await_make_pdb(mols):
    await asyncio.gather(*[make_pdb(mol) for mol in mols]) # [[pdb,pmol], [pdb,pmol],...]

def create_pdb(mols):
    asyncio.run(await_make_pdb(mols))


class RequestModel(BaseModel):
    cpu: int
    rank: int
    sub_dir: str
    smi_file: str
    smilib: str

@user_similarity_distributed_router.post("/parent", status_code=status.HTTP_200_OK)
async def parent(
    *,
    # request: Request,
    # files: List[UploadFile] = File(None),
    params: BaseModel = Depends(RequestModel),
    # user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks,
):
    cpu = params.cpu
    rank = params.rank
    sub_dir = params.sub_dir
    smi_file = params.smi_file
    smilib = params.smilib

    is_need_pdbs = True

    logger.debug('----------------------------')
    logger.debug('Similarity Distributed - parent:')
    # logger.debug(f'user.id: {user.id}')
    # logger.debug(f'user.username: {user.username}')
    logger.debug(f'cpu: {cpu}')
    logger.debug(f'rank: {rank}')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'smi_file: {smi_file}')
    logger.debug(f'smilib: {smilib}')

    if smilib == "ZINC":
        logger.debug('Abort, Not Support ZINC.')
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Abort, Not Support ZINC.')
    
    # ----------------
    save_dir = op.join(settings.asset_dir, 'similarity', 'distributed', sub_dir)
    smi_filepath = op.join(save_dir, smi_file)
    with open(smi_filepath, 'r') as f:
        for line in f:
            if line.startswith(('SMILE', 'Smile', 'smile', 'Smiles', 'smiles')): continue
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            elif '\t' in line:
                _line = line.rstrip().split('\t')
            smi = _line[0]
            break

    lib = op.join(settings.asset_dir, 'similarity', 'libraries', smilib)
    header, smiles = None, []
    inhomogen_smiles = [] # original smiles
    with open(lib, 'r') as f:
        # index = 0
        for line in f:
            # if line.startswith('Smile'): continue
            # smiles.append(line[:-1])
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            elif '\t' in line:
                _line = line.rstrip().split('\t')
            if line.startswith(('SMILE', 'Smile', 'smile', 'Smiles', 'smiles')):
                header = _line
                continue
            # smiles.append(_line[0])
            smiles.append([_line[0]]) # try [[smile], [smile], ...]
            inhomogen_smiles.append(_line)
            # smiles.append(_line) # inhomogeneous shape after 1 dimensions / Some table sometimes 'None'
            # smiles.append(list(map(str, _line)))
            # this_line = []
            # for li in _line:
            #     if li is not None: this_line.append(li)
            #     else: this_line.append('-')
            # smiles.append(this_line)
            # smiles.append((index, _line[0]))
            # index += 1
    """
    import multiprocessing
    def multiply(a, b):
        return a * b
    if __name__ == "__main__":
        args_list = [(2, 3), (4, 5), (6, 7)]
        with multiprocessing.Pool(processes=2) as pool:
            results = pool.starmap(multiply, args_list)
        print(results)  # Output: [6, 20, 42]
    """

    logger.debug(f'len smiles: {len(smiles)}')

    start_time = shanghai_time()
    ts_start = int(to_timestamp(start_time))

    parts1, parts2, parts3 = [], [], []
    len_part = int(len(smiles) / 3)
    logger.debug(f'len_part: {len_part}')
    if len_part == 0:
        if len(smiles):
            parts1 = smiles
        else:
            logger.debug('Abort, No Smiles in smi library file.')
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail='Abort, No Smiles in smi library file.')
    elif len_part == 1:
        parts1 = smiles
    elif len_part == 2:
        parts1 = smiles[:3]
        parts2 = smiles[3:]
    elif len_part == 3:
        parts1, parts2, parts3 = smiles
    elif len_part > 3:
        parts1 = smiles[:len_part]
        parts2 = smiles[len_part:len_part*2]
        parts3 = smiles[len_part*2:]

    logger.debug(f'len parts1: {len(parts1)}')
    logger.debug(f'len parts2: {len(parts2)}')
    logger.debug(f'len parts3: {len(parts3)}')

    scores = []
    # p1, p2, p3 = [], [], []
    if len(parts3):
        r = await asyncio.gather(*[isToNode(i+1, sub_dir, cpu, smi, parts) for i, parts in enumerate([parts1, parts2, parts3])])
        # p1, p2, p3 = r
        # scores.extend(p1)
        # scores.extend(p2)
        # scores.extend(p3)
        scores.extend(r[0])
        scores.extend(r[1])
        scores.extend(r[2])
    elif len(parts2):
        r = await asyncio.gather(*[isToNode(i+1, sub_dir, cpu, smi, parts) for i, parts in enumerate([parts1, parts2])])
        if len(r) == 2:
            # p1, p2 = r
            # scores.extend(p1)
            # scores.extend(p2)
            scores.extend(r[0])
            scores.extend(r[1])
        else:
            # p1 = r
            # scores.extend(p1)
            scores.extend(r)
    else:
        r = await asyncio.gather(*[isToNode(i+1, sub_dir, cpu, smi, parts) for i, parts in enumerate([parts1])])
        # p1 = r
        # scores.extend(p1)
        scores.extend(r)

    # logger.debug(f'len(p1): {len(p1)}')
    # logger.debug(f'len(p2): {len(p2)}')
    # logger.debug(f'len(p3): {len(p3)}')

    len_scores = len(scores)
    logger.debug(f'len(smiles): {len(smiles)}')
    smiles = None #! Refersh memory
    logger.debug(f'len(scores): {len_scores}')

    if len_scores < rank:
        rank = len(scores)

    # sorted_indices = sorted(range(len(scores)), key=lambda i: scores[i])
    # reversed_indices = list(reversed(sorted_indices))
    reversed_indices = sorted(range(len_scores), key=lambda i: scores[i], reverse=True)
    reversed_indices = reversed_indices[:rank]

    # if files is not None:
    #     name, ext = op.splitext(files[0].filename)
    #     result_csv = f'{name}.csv'
    # else:
    #     result_csv = 'result.csv'
    # save_to = op.join(save_dir, result_csv)

    name, ext = op.splitext(smi_file)
    result_csv = f'{name}.csv'
    save_to = op.join(save_dir, result_csv)

    # Save CSV
    if is_need_pdbs:
        pdbs_dir = op.join(save_dir, 'pdbs')
        if op.exists(pdbs_dir):
            shutil.rmtree(pdbs_dir, ignore_errors=True)
        os.makedirs(pdbs_dir, exist_ok=True)
        mols = []


    if header is None:
        # header = ['-' for _ in smiles[0]]
        header = ['-' for _ in inhomogen_smiles[0]]
        header[0] = 'Smiles'
        header.insert(1, 'Scores')
    else:
        header.insert(1, 'Scores')
    with open(save_to, 'w', newline= '', errors='ignore') as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for i in range(rank):
            index = reversed_indices[i]
            # line = smiles[index]
            line = inhomogen_smiles[index]
            line.insert(1, str(scores[index]))
            writer.writerow(line)

            if is_need_pdbs and i < 16:
                pdb = op.join(pdbs_dir, f'{str(i+1).zfill(4)}.pdb')
                mol = Chem.MolFromSmiles(line[0])
                # props = mol.GetPropsAsDict()

                for pmol in EnumerateStereoisomers(Chem.MolFromSmiles(Chem.MolToSmiles(mol, isomericSmiles=False))):
                    # tmp_mol = [(prop, mol.GetProp(prop)) for prop in mol.GetPropNames()]
                    # tmp_mol.insert(0, ('_Name', mol.Get))
                    # tmp_mol.insert(0, pmol)
                    # mols.append(tmp_mol)
                    mols.append([pdb, pmol])

    lib_file = op.join(save_dir, 'lib.txt')
    with open(lib_file, 'w') as f:
        f.write(smilib)

    end_time = shanghai_time()
    ts_end = int(to_timestamp(end_time))
    logger.debug(f'start_time: {start_time}')
    logger.debug(f'end_time: {end_time}')
    logger.debug(f'consume time: {ts_end-ts_start} secs')

    if is_need_pdbs:
        # await asyncio.gather(*[make_pdb(mol) for mol in mols]) # [[pdb,pmol], [pdb,pmol],...]
        background_tasks.add_task(create_pdb, mols)

    logger.debug('Success Similarity Distributed - parent.')

    return f'http://10.168.1.14:4178/assets/similarity/distributed/{sub_dir}/{result_csv}'


@user_similarity_distributed_router.post("/child", status_code=status.HTTP_200_OK)
async def child(
    *,
    request: Request,
    # user: User = Depends(get_current_user),
):
    params = (await request.body()).decode()
    params = json.loads(params)
    node = params['node']
    sub_dir = params['sub_dir']
    cpu = params['cpu']
    smi = params['smi'] if 'smi' in params else None
    parts = params['parts']

    logger.debug('----------------------------')
    logger.debug(f'Similarity Distributed - child node{node}:')
    #logger.debug(f'user.id: {user.id}')
    #logger.debug(f'user.username: {user.username}')
    logger.debug(f'node: {node}')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'cpu: {cpu}')
    logger.debug(f'smi: {smi}')
    # logger.debug(f'parts: {parts}')
    logger.debug(f'len(parts): {len(parts)}')

    # ---------------------------------
    parts_numpy = np.array(parts)
    split = cpu if len(parts) >= cpu else len(parts)
    partitions = np.array_split(parts_numpy, split)

    exec = op.join(settings.base_dir, 'utils', 'distributed_tanimoto.py')

    storage = op.join(settings.asset_dir, 'similarity', 'distributed', sub_dir, f'node{node}')
    if op.exists(storage):
        shutil.rmtree(storage, ignore_errors=True)
    os.makedirs(storage, exist_ok=True)

    pkl = op.join(storage, 'lib.pkl')
    with open(pkl, 'wb') as f:
        pickle.dump(partitions, f)

    async def apipe(cmd):
        proc = await asyncio.create_subprocess_shell(cmd, shell=True,
                                                     stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE,
                                                     universal_newlines=False)
        out, err = await proc.communicate()
        # return proc.returncode, out.decode()
        return out.decode()

    cmd = f'{settings.py} {exec} --cpu {split} --smile "{smi}" --pkl {pkl}'
    logger.debug(cmd)
    out = await apipe(cmd)
    scores = json.loads(out)

    # logger.debug(f'scores: {scores}')
    # logger.debug(f'len(scores): {len(scores)}')
    logger.debug(f'Success Similarity Distributed - child node{node}.')

    return scores

