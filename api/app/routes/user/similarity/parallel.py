from __future__ import annotations
from collections import OrderedDict
from typing import List
import os.path as op
import subprocess
import logging
import asyncio
import shutil
import os

from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem import AllChem, rdMolAlign
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import *
from app.utils.timestamp import shanghai_time, to_timestamp, time_to_string

logger = logging.getLogger(__name__)

user_similarity_parallel_router = APIRouter(prefix="/user_similarity_parallel", tags=['user_similarity_parallel'])


def pipe(cmd):
    process = subprocess.Popen(cmd, shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
    out, err = process.communicate()

async def apipe(cmd):
    proc = await asyncio.create_subprocess_shell(cmd, shell=True,
                                                    stdout=asyncio.subprocess.PIPE,
                                                    stderr=asyncio.subprocess.PIPE,
                                                    universal_newlines=False)
    out, err = await proc.communicate()
    # return proc.returncode, out.decode()


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_parallel/files
class RequestModelFiles(BaseModel):
    offset: int
    limit: int

@user_similarity_parallel_router.get("/files", status_code=status.HTTP_200_OK)
async def getFiles(
    *,
    params: BaseModel = Depends(RequestModelFiles),
):
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: files.')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')
    sub_dirs = sorted(os.listdir(save_dir))

    # async.gather, later
    d = OrderedDict()
    for sub_dir in sub_dirs:
        files = op.join(save_dir, sub_dir)
        csv_file, pdb_file, png_file, smi_file = None, None, None, None
        lib_name = None,
        pngs, pdbs = None, None
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
            else: # dir, "pngs", "pdbs"
                if file == "pngs":
                    pngs_dir = op.join(save_dir, sub_dir, file)
                    pngs = sorted(os.listdir(pngs_dir))
                elif file == "pdbs":
                    pdbs_dir = op.join(save_dir, sub_dir, file)
                    pdbs = sorted(os.listdir(pdbs_dir))

        d[sub_dir] = [csv_file, pdb_file, png_file, smi_file, lib_name, pngs, pdbs]

    logger.debug('Success Similarity Parallel: files.')
    return d


# TODO: ----------------------------------------
# POST: http://10.168.1.14:4178/user_similarity_parallel/upload
@user_similarity_parallel_router.post("/upload", status_code=status.HTTP_200_OK)
async def upload(
    *,
    files: List[UploadFile] = File(None),
):
    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: upload.')

    curr_time = time_to_string(shanghai_time())

    isSmi = True
    for i, file in enumerate(files):
        try:
            sub_dir = f'{curr_time}_{i+1}'
            save_dir = op.join(settings.asset_dir, 'similarity', 'parallel', sub_dir)
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
                if line.startswith(('SMILE', 'Smile', 'smile')): continue
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
            save_dir = op.join(settings.asset_dir, 'similarity', 'parallel', sub_dir)
            if op.exists(save_dir):
                shutil.rmtree(save_dir, ignore_errors=True)
    
    logger.debug('Success Similarity Parallel: upload.')
    return ""


# TODO: ----------------------------------------
# DELETE: http://10.168.1.14:4178/user_similarity_parallel/{sub_dir}
@user_similarity_parallel_router.delete("/{sub_dir}", status_code=status.HTTP_200_OK)
async def delete(
    *,
    sub_dir: str,
):
    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: delete.')
    logger.debug(f'sub_dir: {sub_dir}')

    if sub_dir in ['datetime']:
        detail = "Abort, datetime is sample, unable to be deleted."
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')

    full_dir = op.join(save_dir, sub_dir)
    if not op.exists(full_dir):
        detail = f'Abort, {full_dir} does not exist.'
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    shutil.rmtree(full_dir, ignore_errors=True)
    logger.debug('Success Similarity Parallel: delete.')
    return ""


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_parallel/show-2d
def load_smi_with_props(filename, limit, loop_all=False):
    all_props, headers = [], []
    total_smile = 0 # ui pagination
    with open(filename, 'r') as f:
        for line in f:
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            if '\t' in line:
                _line = line.rstrip().split('\t')

            if line.startswith(('SMILE', 'Smile', 'smile')):
                headers = _line
            else:
                d = OrderedDict()
                for j, header in enumerate(headers):
                    d[header] = _line[j]

                if len(all_props) < limit:
                    all_props.append(d)

                total_smile += 1
                if len(all_props) == limit and not loop_all:
                    break

    return all_props, total_smile # props contain smiles

class RequestModelShow2D(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_parallel_router.get("/show-2d", status_code=status.HTTP_200_OK)
async def show2d(
    *,
    params: BaseModel = Depends(RequestModelShow2D),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: show-2d.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')
    full_dir = op.join(save_dir, sub_dir)

    # test.smi
    smi_file = op.join(full_dir, filename)
    test_props = []
    if op.exists(smi_file):
        test_props, _ = load_smi_with_props(smi_file, 1) # props contain smiles, without header

    # test.csv (result similarity)
    name, ext = op.splitext(filename)
    csv_file = op.join(full_dir, f'{name}.csv')
    result_props = []
    if op.exists(csv_file):
        result_props, total_smile = load_smi_with_props(csv_file, limit, loop_all=True)

    pngs_dir = op.join(full_dir, 'pngs')
    pngs = []
    if op.exists(pngs_dir):
        pngs = sorted(os.listdir(pngs_dir))

    logger.debug('Success Similarity Parallel: show-2d.')

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'test_props': test_props,
        'png': f'{name}.png',
        'result_props': result_props,
        'pngs': pngs,
        'total_smile': total_smile,
        'site': 'initial'
        })


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_parallel/show-2d-next-prev
def load_smi_with_props_next_prev(filename, offset, limit):
    all_props, headers = [], []
    total_smile = 0 # ui pagination
    with open(filename, 'r') as f:
        for line in f:
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            if '\t' in line:
                _line = line.rstrip().split('\t')

            if line.startswith(('SMILE', 'Smile', 'smile')):
                headers = _line
            else:
                d = OrderedDict()
                for j, header in enumerate(headers):
                    d[header] = _line[j]
                all_props.append(d)
                total_smile += 1

    # return all_props # props contain smiles
    return all_props[offset:offset+limit], total_smile # props contain smiles

async def make_png(i, prop, pngs_dir):
    # try:
    png = op.join(pngs_dir, f'{str(i+1).zfill(4)}.png')
    mol = Chem.MolFromSmiles(prop['Smiles'])
    # d = rdMolDraw2D.MolDraw2DSVG(300, 300) # svg
    d = rdMolDraw2D.MolDraw2DCairo(300, 300) # png
    rdMolDraw2D.PrepareAndDrawMolecule(d, mol)
    d.WriteDrawingText(png) # e.g: 'test.png'
    # except: pass

class RequestModelShow2DNextPrev(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_parallel_router.get("/show-2d-next-prev", status_code=status.HTTP_200_OK)
async def show2d_next_prev(
    *,
    params: BaseModel = Depends(RequestModelShow2DNextPrev),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: show-2d-next-prev.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')
    full_dir = op.join(save_dir, sub_dir)

    # test.smi
    smi_file = op.join(full_dir, filename)
    test_props, _ = load_smi_with_props(smi_file, 1) # props contain smiles, without header

    # test.csv (result substructure)
    name, ext = op.splitext(filename)
    csv_file = op.join(full_dir, f'{name}.csv')
    result_props, total_smile = load_smi_with_props_next_prev(csv_file, offset, limit)

    # Make png
    pngs_dir = op.join(full_dir, 'pngs-next-prev')
    if len(result_props) and op.exists(pngs_dir):
        shutil.rmtree(pngs_dir, ignore_errors=True)
    os.makedirs(pngs_dir, exist_ok=True)
   
    await asyncio.gather(*[make_png(i, prop, pngs_dir) for i, prop in enumerate(result_props)])

    pngs = sorted(os.listdir(pngs_dir))

    logger.debug('Success Similarity Parallel: show-2d-next-prev.')

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        'test_props': test_props,
        'png': f'{name}.png',
        'result_props': result_props,
        'pngs': pngs,
        'total_smile': total_smile,
        'site': 'next-prev'
        })


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_parallel/show-3d
class RequestModelShow3D(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_parallel_router.get("/show-3d", status_code=status.HTTP_200_OK)
async def show3d(
    *,
    params: BaseModel = Depends(RequestModelShow3D),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: show-3d.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')
    full_dir = op.join(save_dir, sub_dir)

    # test.smi
    # smi_file = op.join(full_dir, filename)
    test_props = []
    # if op.exists(smi_file):
    #     test_props, _ = load_smi_with_props(smi_file, 1) # props contain smiles, without header

    # test.csv (result similarity)
    name, ext = op.splitext(filename)
    csv_file = op.join(full_dir, f'{name}.csv')
    result_props = []
    if op.exists(csv_file):
        result_props, total_smile = load_smi_with_props(csv_file, limit, loop_all=True)
    
    pdbs_dir = op.join(full_dir, 'pdbs')
    pdbs = []
    if op.exists(pdbs_dir):
        pdbs = sorted(os.listdir(pdbs_dir))
    
    logger.debug('Success Similarity Parallel: show-3d.')
    # return pdbs[0:limit] if len(pdbs) else []
    return JSONResponse(status_code=status.HTTP_200_OK, content={
        # 'pdbs': pdbs[0:limit] if len(pdbs) else [],
        # 'test_props': test_props,
        # 'pdb': pdb,
        # 'result_props': result_props,
        'pdbs': pdbs,
        'total_smile': total_smile,
        'site': 'initial'
        })


# TODO: ----------------------------------------
# GET: http://10.168.1.14:4178/user_similarity_parallel/show-3d-next-prev
async def make_pdb(i, prop, pdbs_dir):
    smile = prop['Smiles']
    mol = Chem.MolFromSmiles(smile)
    pdb = op.join(pdbs_dir, f'{str(i+1).zfill(4)}.pdb')
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

class RequestModelShow3DNextPrev(BaseModel):
    sub_dir: str
    filename: str
    offset: int
    limit: int

@user_similarity_parallel_router.get("/show-3d-next-prev", status_code=status.HTTP_200_OK)
async def show3d_next_prev(
    *,
    params: BaseModel = Depends(RequestModelShow3DNextPrev),
    # user: User = Depends(get_current_user),
):
    sub_dir = params.sub_dir
    filename = params.filename
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: show-3d-next-prev.')
    logger.debug(f'sub_dir: {sub_dir}')
    logger.debug(f'filename: {filename}')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel')
    full_dir = op.join(save_dir, sub_dir)

    # test.smi
    # smi_file = op.join(full_dir, filename)
    # test_props, _ = load_smi_with_props(smi_file, 1) # props contain smiles, without header

    # test.csv (result similarity)
    name, ext = op.splitext(filename)
    csv_file = op.join(full_dir, f'{name}.csv')
    result_props, total_smile = load_smi_with_props_next_prev(csv_file, offset, limit)

    pdbs_dir = op.join(full_dir, 'pdbs-next-prev')
    if len(result_props) and op.exists(pdbs_dir):
        shutil.rmtree(pdbs_dir, ignore_errors=True)
    os.makedirs(pdbs_dir, exist_ok=True)

    # Slow ----------
    # await asyncio.gather(*[make_pdb(i, prop, pdbs_dir) for i, prop in enumerate(result_props)])
    #
    exec = op.join(settings.base_dir, 'utils', 'make_pdb.py')
    smiles = [prop['Smiles'] for prop in result_props]
    smiles = ','.join(smiles)
    cmd = f'{settings.py} {exec} --smiles "{smiles}" --pdbs-dir {pdbs_dir}'
    logger.debug(cmd)
    await apipe(cmd)
    # pipe(cmd)

    pdbs = sorted(os.listdir(pdbs_dir))

    logger.debug('Success Similarity Parallel: show-3d-next-prev.')

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        # 'test_props': test_props,
        # 'pdb': f'{name}.pdb',
        # 'result_props': result_props,
        'pdbs': pdbs,
        'total_smile': total_smile,
        'site': 'next-prev'
        })


# TODO: ----------------------------------------
# POST: http://10.168.1.14:4178/user_similarity_parallel/parent
class RequestModelParent(BaseModel):
    cpu: int
    rank: int
    sub_dir: str
    smi_file: str
    smilib: str

@user_similarity_parallel_router.post("/parent", status_code=status.HTTP_200_OK)
async def parent(
    *,
    # files: List[UploadFile] = File(None),
    params: BaseModel = Depends(RequestModelParent),
):
    cpu = params.cpu
    rank = params.rank
    sub_dir = params.sub_dir
    smi_file = params.smi_file
    smilib = params.smilib

    logger.debug('----------------------------')
    logger.debug('Similarity Parallel: parent.')
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
    save_dir = op.join(settings.asset_dir, 'similarity', 'parallel', sub_dir)
    smi_filepath = op.join(save_dir, smi_file)
    with open(smi_filepath, 'r') as f:
        for line in f:
            if line.startswith(('SMILE', 'Smile', 'smile')): continue
            _line = line.rstrip().split()
            if ',' in line:
                _line = line.rstrip().split(',')
            elif '\t' in line:
                _line = line.rstrip().split('\t')
            smi = _line[0]
            break

    lib = op.join(settings.asset_dir, 'similarity', 'libraries', smilib)

    # ----------------
    # Run similarity
    start_time = shanghai_time()
    ts_start = int(to_timestamp(start_time))

    name, ext = op.splitext(smi_file)
    result_csv = f'{name}.csv'
    save_to = op.join(save_dir, result_csv)

    exec = op.join(settings.base_dir, 'utils', 'parallel_tanimoto.py')

    # with generate PDB 3D
    cmd = f'{settings.py} {exec} --is-need-pngs --is-need-pdbs --cpu {cpu} --rank {rank} --smile "{smi}" --lib {lib} --save-to {save_to}'
    # without generate PDB 3D
    # cmd = f'{settings.py} {exec} --cpu {cpu} --rank {rank} --smile "{smi}" --lib {lib} --save-to {save_to}'

    logger.debug(cmd)
    # out = await apipe(cmd)
    # scores = json.loads(out)
    # logger.debug(f'len(scores): {len(scores)}')
    await apipe(cmd)

    lib_file = op.join(save_dir, 'lib.txt')
    with open(lib_file, 'w') as f:
        f.write(smilib)

    end_time = shanghai_time()
    ts_end = int(to_timestamp(end_time))
    logger.debug(f'start_time: {start_time}')
    logger.debug(f'end_time: {end_time}')
    logger.debug(f'consume_time: {ts_end-ts_start} secs.')

    logger.debug('Success Similarity Parallel: parent.')

    return f'http://10.168.1.14:4178/assets/similarity/parallel/{sub_dir}/{result_csv}'

