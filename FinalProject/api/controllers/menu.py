from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from ..models.categories import Category
from ..models.dishes import Dish
from ..schemas.categories import CategoryCreate, CategoryUpdate, CategoryOut
from ..schemas.dishes import DishCreate, DishUpdate, DishOut


def create_category(db: Session, category: CategoryCreate) -> CategoryOut:
    db_category = Category(
        name=category.name,
        description=category.description
    )
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return CategoryOut.from_orm(db_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category name already exists")


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Category).filter(Category.is_active == True).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: int) -> Category:
    category = db.query(Category).filter(Category.id == category_id).first()
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> CategoryOut:
    db_category = get_category(db, category_id)
    
    if category.name is not None:
        db_category.name = category.name
    if category.description is not None:
        db_category.description = category.description
    if category.is_active is not None:
        db_category.is_active = category.is_active
    
    try:
        db.commit()
        db.refresh(db_category)
        return CategoryOut.from_orm(db_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Category name already exists")


def delete_category(db: Session, category_id: int):
    db_category = get_category(db, category_id)
    db_category.is_active = False
    db.commit()
    return {"message": "Category deleted"}


def create_dish(db: Session, dish: DishCreate) -> DishOut:
    # Verify category exists
    category = db.query(Category).filter(Category.id == dish.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db_dish = Dish(
        name=dish.name,
        description=dish.description,
        price_cents=dish.price_cents,
        category_id=dish.category_id,
        is_active=dish.is_active
    )
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return DishOut.from_orm(db_dish)


def get_dishes(db: Session, skip: int = 0, limit: int = 100, category_id: int = None):
    query = db.query(Dish).filter(Dish.is_active == True)
    if category_id:
        query = query.filter(Dish.category_id == category_id)
    return query.offset(skip).limit(limit).all()


def get_dish(db: Session, dish_id: int) -> Dish:
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if dish is None:
        raise HTTPException(status_code=404, detail="Dish not found")
    return dish


def update_dish(db: Session, dish_id: int, dish: DishUpdate) -> DishOut:
    db_dish = get_dish(db, dish_id)
    
    if dish.name is not None:
        db_dish.name = dish.name
    if dish.description is not None:
        db_dish.description = dish.description
    if dish.price_cents is not None:
        db_dish.price_cents = dish.price_cents
    if dish.category_id is not None:
        # Verify category exists
        category = db.query(Category).filter(Category.id == dish.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        db_dish.category_id = dish.category_id
    if dish.is_active is not None:
        db_dish.is_active = dish.is_active
    
    db.commit()
    db.refresh(db_dish)
    return DishOut.from_orm(db_dish)


def delete_dish(db: Session, dish_id: int):
    db_dish = get_dish(db, dish_id)
    db_dish.is_active = False
    db.commit()
    return {"message": "Dish deleted"}
