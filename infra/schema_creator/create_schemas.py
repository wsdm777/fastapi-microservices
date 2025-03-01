import os
import asyncio
import asyncpg

DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
ORGANIZATIONS = os.getenv("ORGANIZATIONS", "").split(",")
SERVICES = os.getenv("SERVICES", "").split(",")

DB_URL = f"postgresql://{DB_USER}:{DB_PASS}@db:5432/{DB_NAME}"

print(f"orgs: {ORGANIZATIONS}", flush=True)
print(f"services: {SERVICES}", flush=True)


async def wait_for_db():
    while True:
        try:
            conn = await asyncpg.connect(DB_URL)
            await conn.close()
            break
        except Exception:
            print(f"Failed to connect {DB_URL}")
            await asyncio.sleep(2)


async def create_schemas():
    conn = await asyncpg.connect(DB_URL)

    for org in ORGANIZATIONS:
        for service in SERVICES:
            schema_name = f"{org}_{service}"
            await conn.execute(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"')

    await conn.close()


async def main():
    await wait_for_db()
    await create_schemas()


if __name__ == "__main__":
    asyncio.run(main())
