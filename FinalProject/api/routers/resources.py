from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies.database import get_db
from ..controllers.resources import (
    create_resource, get_resources, update_resource, delete_resource,
    get_resource, update_resource_amount, get_low_stock_resources
)
from ..schemas.resources import ResourceCreate, ResourceUpdate, ResourceOut

router = APIRouter(prefix="/resources", tags=["resources"])


@router.post("/", response_model=ResourceOut)
def create_resource_endpoint(resource: ResourceCreate, db: Session = Depends(get_db)):
    return create_resource(db, resource)


@router.get("/", response_model=List[ResourceOut])
def list_resources(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_resources(db, skip=skip, limit=limit)


@router.get("/{resource_id}", response_model=ResourceOut)
def get_resource_endpoint(resource_id: int, db: Session = Depends(get_db)):
    resource = get_resource(db, resource_id)
    return ResourceOut.model_validate(resource.__dict__)


@router.put("/{resource_id}", response_model=ResourceOut)
def update_resource_endpoint(resource_id: int, resource: ResourceUpdate, db: Session = Depends(get_db)):
    return update_resource(db, resource_id, resource)


@router.delete("/{resource_id}")
def delete_resource_endpoint(resource_id: int, db: Session = Depends(get_db)):
    return delete_resource(db, resource_id)


@router.patch("/{resource_id}/amount", response_model=ResourceOut)
def update_resource_amount_endpoint(
    resource_id: int, 
    amount_change: int = Query(..., description="Amount to add/subtract from current stock"),
    db: Session = Depends(get_db)
):
    return update_resource_amount(db, resource_id, amount_change)


@router.get("/low-stock/", response_model=List[ResourceOut])
def get_low_stock_resources_endpoint(
    threshold: int = Query(10, description="Stock level threshold for low stock alert"),
    db: Session = Depends(get_db)
):
    return get_low_stock_resources(db, threshold)
