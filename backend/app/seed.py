"""One-time seed of the single pilot restaurant.

Modeled on the shape of a restaurant record in El Libro (name only, for this
slice); there is no runtime dependency on El Libro (FR12/13).

Assumes the schema already exists (`alembic upgrade head`) — this script
only inserts data, it never creates tables.
"""

import asyncio

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import Restaurant

PILOT_RESTAURANT_NAME = "La Terraza Azul"


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        existing = await session.scalar(
            select(Restaurant).where(Restaurant.name == PILOT_RESTAURANT_NAME)
        )
        if existing is not None:
            print(f"Restaurant already seeded: {existing.name} (id={existing.id})")
            return

        restaurant = Restaurant(name=PILOT_RESTAURANT_NAME)
        session.add(restaurant)
        await session.commit()
        await session.refresh(restaurant)
        print(f"Seeded restaurant: {restaurant.name} (id={restaurant.id})")


if __name__ == "__main__":
    asyncio.run(seed())
