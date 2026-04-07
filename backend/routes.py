from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from . import schemas, services, models, database
from typing import List

router = APIRouter()

@router.post("/generate", response_model=schemas.GenerateResponse)
async def generate_content(request: schemas.GenerateRequest):
    try:
        result = await services.generate_content(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/hook", response_model=schemas.HookResponse)
async def generate_hook(request: schemas.HookRequest):
    try:
        return await services.generate_hook(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calendar", response_model=schemas.CalendarResponse)
async def generate_calendar(request: schemas.CalendarRequest):
    try:
        return await services.generate_calendar(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/scripts", response_model=schemas.ScriptResponse)
def create_script(script: schemas.ScriptCreate, db: Session = Depends(database.get_db)):
    db_script = models.Script(**script.model_dump())
    db.add(db_script)
    db.commit()
    db.refresh(db_script)
    return db_script

@router.get("/scripts", response_model=List[schemas.ScriptResponse])
def get_scripts(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    scripts = db.query(models.Script).offset(skip).limit(limit).all()
    return scripts

@router.get("/export/pdf/{script_id}")
def export_pdf(script_id: int, db: Session = Depends(database.get_db)):
    script = db.query(models.Script).filter(models.Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
        
    pdf_buffer = services.generate_pdf(script.script_content)
    
    return StreamingResponse(
        iter([pdf_buffer.getvalue()]), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=script_{script_id}.pdf"}
    )

