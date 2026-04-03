from __future__ import annotations
from typing import List
import os.path as op
import logging
import asyncio
import shutil
import os

from rdkit import Chem

from fastapi import APIRouter, Depends, HTTPException, status, Request, File, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app import *
from app.routes.user.user import get_current_user

logger = logging.getLogger(__name__)

user_converter_sdf2smi_router = APIRouter(prefix="/user_converter_sdf2smi", tags=['user_converter_sdf2smi'])
