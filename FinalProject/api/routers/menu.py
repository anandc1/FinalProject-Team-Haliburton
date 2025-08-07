from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..dependencies.database import get_db
from ..controllers.menu import (
    create_category, get_categories, update_category, delete_category,
    create_dish, get_dishes, get_dish, update_dish, delete_dish
)
from ..schemas.categories import CategoryCreate, CategoryUpdate, CategoryOut
from ..schemas.dishes import DishCreate, DishUpdate, DishOut

router = APIRouter(prefix="/menu", tags=["menu"])


# Category endpoints
@router.post("/categories", response_model=CategoryOut)
def create_category_endpoint(category: CategoryCreate, db: Session = Depends(get_db)):
    return create_category(db, category)


@router.get("/categories", response_model=List[CategoryOut])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_categories(db, skip=skip, limit=limit)


@router.put("/categories/{category_id}", response_model=CategoryOut)
def update_category_endpoint(category_id: int, category: CategoryUpdate, db: Session = Depends(get_db)):
    return update_category(db, category_id, category)


@router.delete("/categories/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    return delete_category(db, category_id)


# Dish endpoints
@router.post("/dishes", response_model=DishOut)
def create_dish_endpoint(dish: DishCreate, db: Session = Depends(get_db)):
    return create_dish(db, dish)


@router.get("/dishes", response_model=List[DishOut])
def list_dishes(
    skip: int = 0, 
    limit: int = 100, 
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    return get_dishes(db, skip=skip, limit=limit, category_id=category_id)


@router.get("/dishes/{dish_id}", response_model=DishOut)
def get_dish_endpoint(dish_id: int, db: Session = Depends(get_db)):
    dish = get_dish(db, dish_id)
    return DishOut.from_orm(dish)


@router.put("/dishes/{dish_id}", response_model=DishOut)
def update_dish_endpoint(dish_id: int, dish: DishUpdate, db: Session = Depends(get_db)):
    return update_dish(db, dish_id, dish)


@router.delete("/dishes/{dish_id}")
def delete_dish_endpoint(dish_id: int, db: Session = Depends(get_db)):
    return delete_dish(db, dish_id)
