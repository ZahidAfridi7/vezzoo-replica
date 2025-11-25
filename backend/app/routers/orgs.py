from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from .. import models, schemas, database
from .auth import get_current_user

router = APIRouter(
    prefix="/orgs",
    tags=["organizations"],
)

@router.post("/", response_model=schemas.Organization)
async def create_org(org: schemas.OrganizationCreate, current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(database.get_db)):
    new_org = models.Organization(name=org.name)
    db.add(new_org)
    
    # Add user to org
    new_org.users.append(current_user)
    
    await db.commit()
    await db.refresh(new_org)
    return new_org

@router.get("/", response_model=List[schemas.Organization])
async def list_orgs(current_user: models.User = Depends(get_current_user), db: AsyncSession = Depends(database.get_db)):
    # In a real app, we would filter by user association. 
    # For now, since we have the relationship loaded, we can just return current_user.organizations
    # But we need to make sure it's loaded.
    # Alternatively, query the association.
    
    # Re-fetch user with organizations eagerly loaded if needed, or just query orgs joined with user
    result = await db.execute(
        select(models.Organization)
        .join(models.user_org_association)
        .where(models.user_org_association.c.user_id == current_user.id)
    )
    return result.scalars().all()
