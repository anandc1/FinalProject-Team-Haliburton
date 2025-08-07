from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..models.resources import Resource
from ..schemas.resources import ResourceCreate, ResourceUpdate, ResourceOut


def create_resource(db: Session, resource: ResourceCreate) -> ResourceOut:
    db_resource = Resource(
        name=resource.name,
        description=resource.description,
        amount=resource.amount,
        unit=resource.unit,
        is_active=resource.is_active
    )
    try:
        db.add(db_resource)
        db.commit()
        db.refresh(db_resource)
        return ResourceOut.from_orm(db_resource)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Resource name already exists")


def get_resources(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Resource).filter(Resource.is_active == True).offset(skip).limit(limit).all()


def get_resource(db: Session, resource_id: int) -> Resource:
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


def update_resource(db: Session, resource_id: int, resource: ResourceUpdate) -> ResourceOut:
    db_resource = get_resource(db, resource_id)
    
    if resource.name is not None:
        db_resource.name = resource.name
    if resource.description is not None:
        db_resource.description = resource.description
    if resource.amount is not None:
        db_resource.amount = resource.amount
    if resource.unit is not None:
        db_resource.unit = resource.unit
    if resource.is_active is not None:
        db_resource.is_active = resource.is_active
    
    try:
        db.commit()
        db.refresh(db_resource)
        return ResourceOut.from_orm(db_resource)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Resource name already exists")


def delete_resource(db: Session, resource_id: int):
    db_resource = get_resource(db, resource_id)
    db_resource.is_active = False
    db.commit()
    return {"message": "Resource deleted"}


def update_resource_amount(db: Session, resource_id: int, amount_change: int):
    """Update resource amount (for inventory management)"""
    db_resource = get_resource(db, resource_id)
    db_resource.amount += amount_change
    
    if db_resource.amount < 0:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    db.commit()
    db.refresh(db_resource)
    return ResourceOut.from_orm(db_resource)


def get_low_stock_resources(db: Session, threshold: int = 10):
    """Get resources with low stock levels"""
    return db.query(Resource).filter(
        Resource.is_active == True,
        Resource.amount <= threshold
    ).all()
