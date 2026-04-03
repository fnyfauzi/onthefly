from __future__ import annotations
from collections import OrderedDict
from typing import List
import os.path as op
import logging
import shutil
import os

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import *

logger = logging.getLogger(__name__)

user_similarity_libraries_router = APIRouter(prefix="/user_similarity_libraries", tags=['user_similarity_libraries'])


class RequestModelLibs(BaseModel):
    offset: int
    limit: int

@user_similarity_libraries_router.get("/libs", status_code=status.HTTP_200_OK)
async def libs(
    *,
    params: BaseModel = Depends(RequestModelLibs),
):
    offset = params.offset
    limit = params.limit

    logger.debug('----------------------------')
    logger.debug('Similarity Libraries: libs')
    logger.debug(f'offset: {offset}')
    logger.debug(f'limit: {limit}')

    save_dir = op.join(settings.asset_dir, 'similarity', 'libraries')
    files = sorted(os.listdir(save_dir))

    filenames = []
    for file in files:
        dir_or_file = op.join(save_dir, file)
        if file in ["ZINC.smi"]:
            continue
        if op.isfile(dir_or_file):
            name, ext = op.splitext(file)
            if ext.endswith('.smi'):
                filenames.append(file)

    files = None
    filenames = filenames[offset:limit]

    libs = []
    for filename in filenames:
        size = op.getsize(op.join(save_dir, filename))
        libs.append([filename, size])

    logger.debug('Success Similarity Libraries: libs')
    return libs # [[filename, size], [filename, size], ...]


# --------------------
class RequestModelChunk(BaseModel):
    filename: str
    isInitial: bool
    totalChunk: int
    indexChunk: int

@user_similarity_libraries_router.post("/chunk", status_code=status.HTTP_200_OK)
async def chunk(
    *,
    files: List[UploadFile] = File(None),
    params: BaseModel = Depends(RequestModelChunk),
):
    filename = params.filename
    isInitial = params.isInitial
    totalChunk = params.totalChunk
    indexChunk = params.indexChunk

    logger.debug('----------------------------')
    logger.debug('Similarity Libraries: chunk')
    logger.debug(f'filename: {filename}')
    logger.debug(f'isInitial: {isInitial}')
    logger.debug(f'totalChunk: {totalChunk}')
    logger.debug(f'indexChunk: {indexChunk}')

    # validation
    name, ext = op.splitext(filename)

    if ext != ".smi":
        detail = f'Abort, Only .smi file.'
        logger.info(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)        

    if filename == 'ZINC.smi':
        detail = f'Abort, Not allowed to overwrite ZINC.smi'
        logger.info(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
        
    if name in ['ZINC_npy', 'ZINC_smi', 'ZINC_pkl']:
        detail = f'Abort, Not allowed to overwrite ZINC_npy, ZINC_smi, ZINC_pkl'
        logger.info(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    if isInitial:
        file = op.join(settings.asset_dir, 'similarity', "libraries", filename)
        if op.exists(file):
            detail = f'Abort, "{name}" is exist. Rename your file or delete the existing library.'
            logger.info(detail)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

        # We delete the unfinished upload.
        dir = op.join(settings.asset_dir, 'similarity', "libraries", name)
        if op.isdir(dir):
            shutil.rmtree(dir, ignore_errors=True)

    chunk_dir = op.join(settings.asset_dir, 'similarity', "libraries", name)
    if isInitial:
        if op.exists(chunk_dir):
            shutil.rmtree(chunk_dir, ignore_errors=True)
        os.makedirs(chunk_dir, exist_ok=True)

    for file in files:
        part = f'{indexChunk}'.zfill(6)
        save_to = op.join(chunk_dir, f'{filename}_{part}')
        with open(save_to, 'wb') as f:
            shutil.copyfileobj(file.file, f)
        file.close()
        logger.debug(f'save_to: {save_to}')
    
    if indexChunk == totalChunk - 1:
        save_to = op.join(settings.asset_dir, 'similarity', "libraries", filename)
        with open(save_to, 'wb') as f:
            for i in range(0, totalChunk):
                part = f'{i}'.zfill(6)
                part = op.join(chunk_dir, f'{filename}_{part}')
                with open(part, 'rb') as ff:
                    f.write(ff.read())
                os.remove(part)
        if op.isdir(chunk_dir):
            shutil.rmtree(chunk_dir, ignore_errors=True)

        logger.debug('Success Similarity Libraries - chunk ensemble.')
        return f'http://10.168.1.14:4178/assets/similarity/libraries/{filename}'

    return ""


@user_similarity_libraries_router.delete("/{filename}", status_code=status.HTTP_200_OK)
async def delete(
    *,
    filename: str,
):
    logger.debug('----------------------------')
    logger.debug('Similarity Libraries: delete')
    logger.debug(f'filename: {filename}')

    if filename in ['ZINC', 'ZINC_npy', 'ZINC_smi', 'ZINC_pkl']:
        detail = "Abort, ZINC Not allowed to be deleted."
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)

    save_dir = op.join(settings.asset_dir, 'similarity', 'libraries')

    lib = op.join(save_dir, filename)
    if not op.exists(lib):
        detail = f'Abort, {filename} does not exist.'
        logger.debug(detail)
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)
    
    os.remove(lib)
    logger.debug('Success Similarity Libraries: delete.')
    return ""
