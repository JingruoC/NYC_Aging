import os
from contextlib import contextmanager

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/nyc_aging_menu",
)


engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def ensure_sqlite_schema() -> None:
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    if "recipes" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("recipes")}
        recipe_alterations = [
            ("ingredients", "ALTER TABLE recipes ADD COLUMN ingredients JSON NOT NULL DEFAULT '[]'"),
            ("instructions", "ALTER TABLE recipes ADD COLUMN instructions JSON NOT NULL DEFAULT '[]'"),
            ("serving_size", "ALTER TABLE recipes ADD COLUMN serving_size VARCHAR(100)"),
            ("yield_servings", "ALTER TABLE recipes ADD COLUMN yield_servings INTEGER NOT NULL DEFAULT 50"),
            ("scale_note", "ALTER TABLE recipes ADD COLUMN scale_note TEXT"),
            ("contributed_by", "ALTER TABLE recipes ADD COLUMN contributed_by VARCHAR(255)"),
            ("created_on", "ALTER TABLE recipes ADD COLUMN created_on DATE"),
            ("is_public", "ALTER TABLE recipes ADD COLUMN is_public BOOLEAN NOT NULL DEFAULT 1"),
            ("is_favorite", "ALTER TABLE recipes ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0"),
            ("is_dead", "ALTER TABLE recipes ADD COLUMN is_dead BOOLEAN NOT NULL DEFAULT 0"),
            ("nutrient_claims", "ALTER TABLE recipes ADD COLUMN nutrient_claims JSON NOT NULL DEFAULT '[]'"),
            ("vitamin_c_mg", "ALTER TABLE recipes ADD COLUMN vitamin_c_mg FLOAT NOT NULL DEFAULT 0"),
            ("calcium_mg", "ALTER TABLE recipes ADD COLUMN calcium_mg FLOAT NOT NULL DEFAULT 0"),
        ]
        with engine.begin() as conn:
            for column_name, ddl in recipe_alterations:
                if column_name not in existing_columns:
                    conn.execute(text(ddl))

    if "menus" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("menus")}
        menu_alterations = [
            ("contract_name", "ALTER TABLE menus ADD COLUMN contract_name VARCHAR(255)"),
            ("program_type", "ALTER TABLE menus ADD COLUMN program_type VARCHAR(100)"),
            ("meal_type", "ALTER TABLE menus ADD COLUMN meal_type VARCHAR(100)"),
            ("menu_coverage", "ALTER TABLE menus ADD COLUMN menu_coverage VARCHAR(100)"),
            ("diet_type", "ALTER TABLE menus ADD COLUMN diet_type VARCHAR(100)"),
            ("menu_format", "ALTER TABLE menus ADD COLUMN menu_format VARCHAR(100)"),
            ("menu_duration_type", "ALTER TABLE menus ADD COLUMN menu_duration_type VARCHAR(100)"),
            ("meal_served_format", "ALTER TABLE menus ADD COLUMN meal_served_format VARCHAR(150)"),
            ("menu_tags", "ALTER TABLE menus ADD COLUMN menu_tags JSON NOT NULL DEFAULT '[]'"),
            ("cycle", "ALTER TABLE menus ADD COLUMN cycle VARCHAR(100)"),
            ("cycle_start_date", "ALTER TABLE menus ADD COLUMN cycle_start_date DATE"),
            ("cycle_end_date", "ALTER TABLE menus ADD COLUMN cycle_end_date DATE"),
            ("contracts", "ALTER TABLE menus ADD COLUMN contracts JSON NOT NULL DEFAULT '[]'"),
            ("sample_menu_id", "ALTER TABLE menus ADD COLUMN sample_menu_id INTEGER"),
            ("completed_weeks", "ALTER TABLE menus ADD COLUMN completed_weeks JSON NOT NULL DEFAULT '[]'"),
            ("submitted_programs", "ALTER TABLE menus ADD COLUMN submitted_programs JSON NOT NULL DEFAULT '[]'"),
            ("status", "ALTER TABLE menus ADD COLUMN status VARCHAR(50) NOT NULL DEFAULT 'Draft'"),
            ("status_date", "ALTER TABLE menus ADD COLUMN status_date DATE"),
            ("submitted_to", "ALTER TABLE menus ADD COLUMN submitted_to VARCHAR(255)"),
            ("submitted_to_nyc_aging_on", "ALTER TABLE menus ADD COLUMN submitted_to_nyc_aging_on DATE"),
            ("nutrition_advisor", "ALTER TABLE menus ADD COLUMN nutrition_advisor VARCHAR(255)"),
            ("created_by", "ALTER TABLE menus ADD COLUMN created_by VARCHAR(255)"),
            ("start_date", "ALTER TABLE menus ADD COLUMN start_date DATE"),
            ("end_date", "ALTER TABLE menus ADD COLUMN end_date DATE"),
            ("days_per_week", "ALTER TABLE menus ADD COLUMN days_per_week INTEGER NOT NULL DEFAULT 5"),
            ("cycle_week", "ALTER TABLE menus ADD COLUMN cycle_week INTEGER NOT NULL DEFAULT 1"),
            ("returned_comments", "ALTER TABLE menus ADD COLUMN returned_comments TEXT"),
            ("approval_notes", "ALTER TABLE menus ADD COLUMN approval_notes TEXT"),
            ("is_favorite", "ALTER TABLE menus ADD COLUMN is_favorite BOOLEAN NOT NULL DEFAULT 0"),
        ]
        with engine.begin() as conn:
            for column_name, ddl in menu_alterations:
                if column_name not in existing_columns:
                    conn.execute(text(ddl))

    if "menu_items" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("menu_items")}
        menu_item_alterations = [
            ("day_index", "ALTER TABLE menu_items ADD COLUMN day_index INTEGER NOT NULL DEFAULT 0"),
            ("component_key", "ALTER TABLE menu_items ADD COLUMN component_key VARCHAR(50)"),
            ("is_alternate", "ALTER TABLE menu_items ADD COLUMN is_alternate BOOLEAN NOT NULL DEFAULT 0"),
            ("source_type", "ALTER TABLE menu_items ADD COLUMN source_type VARCHAR(50) NOT NULL DEFAULT 'manual'"),
        ]
        with engine.begin() as conn:
            for column_name, ddl in menu_item_alterations:
                if column_name not in existing_columns:
                    conn.execute(text(ddl))

    if "menu_comments" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("menu_comments")}
        menu_comment_alterations = [
            ("target_type", "ALTER TABLE menu_comments ADD COLUMN target_type VARCHAR(50) NOT NULL DEFAULT 'menu'"),
            ("target_label", "ALTER TABLE menu_comments ADD COLUMN target_label VARCHAR(255)"),
            ("day_index", "ALTER TABLE menu_comments ADD COLUMN day_index INTEGER"),
            ("meal_slot", "ALTER TABLE menu_comments ADD COLUMN meal_slot VARCHAR(100)"),
            ("component_key", "ALTER TABLE menu_comments ADD COLUMN component_key VARCHAR(100)"),
            ("recipe_id", "ALTER TABLE menu_comments ADD COLUMN recipe_id INTEGER"),
            ("nutrient_key", "ALTER TABLE menu_comments ADD COLUMN nutrient_key VARCHAR(100)"),
            ("review_status", "ALTER TABLE menu_comments ADD COLUMN review_status VARCHAR(50) NOT NULL DEFAULT 'open'"),
        ]
        with engine.begin() as conn:
            for column_name, ddl in menu_comment_alterations:
                if column_name not in existing_columns:
                    conn.execute(text(ddl))

    if "historical_menus" in existing_tables:
        existing_columns = {column["name"] for column in inspector.get_columns("historical_menus")}
        historical_menu_alterations = [
            ("program_type", "ALTER TABLE historical_menus ADD COLUMN program_type VARCHAR(100)"),
            ("meal_type", "ALTER TABLE historical_menus ADD COLUMN meal_type VARCHAR(100)"),
            ("menu_coverage", "ALTER TABLE historical_menus ADD COLUMN menu_coverage VARCHAR(100)"),
            ("diet_type", "ALTER TABLE historical_menus ADD COLUMN diet_type VARCHAR(100)"),
            ("menu_duration_type", "ALTER TABLE historical_menus ADD COLUMN menu_duration_type VARCHAR(100)"),
            ("meal_served_format", "ALTER TABLE historical_menus ADD COLUMN meal_served_format VARCHAR(150)"),
            ("menu_tags", "ALTER TABLE historical_menus ADD COLUMN menu_tags JSON NOT NULL DEFAULT '[]'"),
            ("cycle", "ALTER TABLE historical_menus ADD COLUMN cycle VARCHAR(100)"),
            ("days_per_week", "ALTER TABLE historical_menus ADD COLUMN days_per_week INTEGER NOT NULL DEFAULT 5"),
            ("contracts", "ALTER TABLE historical_menus ADD COLUMN contracts JSON NOT NULL DEFAULT '[]'"),
            ("sample_category", "ALTER TABLE historical_menus ADD COLUMN sample_category VARCHAR(100)"),
        ]
        with engine.begin() as conn:
            for column_name, ddl in historical_menu_alterations:
                if column_name not in existing_columns:
                    conn.execute(text(ddl))
