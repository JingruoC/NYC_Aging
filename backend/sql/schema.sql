CREATE TABLE IF NOT EXISTS recipes (
  recipe_id SERIAL PRIMARY KEY,
  recipe_name VARCHAR(255) NOT NULL,
  meal_type VARCHAR(50) NOT NULL,
  category VARCHAR(50) NOT NULL,
  calories DOUBLE PRECISION NOT NULL,
  sodium_mg DOUBLE PRECISION NOT NULL,
  protein_g DOUBLE PRECISION NOT NULL,
  fiber_g DOUBLE PRECISION NOT NULL,
  fat_g DOUBLE PRECISION NOT NULL,
  tags JSONB NOT NULL DEFAULT '[]'::jsonb,
  is_approved BOOLEAN NOT NULL DEFAULT TRUE,
  ingredients JSONB NOT NULL DEFAULT '[]'::jsonb,
  instructions JSONB NOT NULL DEFAULT '[]'::jsonb,
  serving_size VARCHAR(100),
  yield_servings INTEGER NOT NULL DEFAULT 50,
  scale_note TEXT,
  contributed_by VARCHAR(255),
  created_on DATE,
  is_public BOOLEAN NOT NULL DEFAULT TRUE,
  is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
  is_dead BOOLEAN NOT NULL DEFAULT FALSE,
  nutrient_claims JSONB NOT NULL DEFAULT '[]'::jsonb,
  vitamin_c_mg DOUBLE PRECISION NOT NULL DEFAULT 0,
  calcium_mg DOUBLE PRECISION NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS ix_recipes_recipe_name ON recipes(recipe_name);
CREATE INDEX IF NOT EXISTS ix_recipes_meal_type ON recipes(meal_type);
CREATE INDEX IF NOT EXISTS ix_recipes_category ON recipes(category);
CREATE INDEX IF NOT EXISTS ix_recipes_is_approved ON recipes(is_approved);
CREATE INDEX IF NOT EXISTS ix_recipes_is_public ON recipes(is_public);
CREATE INDEX IF NOT EXISTS ix_recipes_is_favorite ON recipes(is_favorite);
CREATE INDEX IF NOT EXISTS ix_recipes_is_dead ON recipes(is_dead);

CREATE TABLE IF NOT EXISTS recipe_comments (
  id SERIAL PRIMARY KEY,
  recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  action VARCHAR(100) NOT NULL,
  author VARCHAR(255) NOT NULL,
  role VARCHAR(100) NOT NULL,
  body TEXT NOT NULL,
  visibility VARCHAR(100) NOT NULL DEFAULT 'Admin and provider',
  badge_class VARCHAR(50) NOT NULL DEFAULT 'brand',
  is_user_comment BOOLEAN NOT NULL DEFAULT TRUE,
  target_type VARCHAR(50) NOT NULL DEFAULT 'recipe',
  target_label VARCHAR(255),
  nutrient_key VARCHAR(100),
  review_status VARCHAR(50) NOT NULL DEFAULT 'open'
);

CREATE INDEX IF NOT EXISTS ix_recipe_comments_recipe_id ON recipe_comments(recipe_id);
CREATE INDEX IF NOT EXISTS ix_recipe_comments_target_type ON recipe_comments(target_type);
CREATE INDEX IF NOT EXISTS ix_recipe_comments_review_status ON recipe_comments(review_status);

CREATE TABLE IF NOT EXISTS menus (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  contract_name VARCHAR(255),
  program_type VARCHAR(100),
  meal_type VARCHAR(100),
  menu_coverage VARCHAR(100),
  diet_type VARCHAR(100),
  menu_format VARCHAR(100),
  menu_duration_type VARCHAR(100),
  meal_served_format VARCHAR(150),
  menu_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
  cycle VARCHAR(100),
  cycle_start_date DATE,
  cycle_end_date DATE,
  contracts JSONB NOT NULL DEFAULT '[]'::jsonb,
  sample_menu_id INTEGER,
  completed_weeks JSONB NOT NULL DEFAULT '[]'::jsonb,
  submitted_programs JSONB NOT NULL DEFAULT '[]'::jsonb,
  status VARCHAR(50) NOT NULL DEFAULT 'Draft',
  status_date DATE,
  submitted_to VARCHAR(255),
  submitted_to_nyc_aging_on DATE,
  nutrition_advisor VARCHAR(255),
  created_by VARCHAR(255),
  service_date DATE NOT NULL DEFAULT CURRENT_DATE,
  start_date DATE,
  end_date DATE,
  days_per_week INTEGER NOT NULL DEFAULT 5,
  cycle_week INTEGER NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  notes TEXT,
  returned_comments TEXT,
  approval_notes TEXT,
  is_favorite BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_menus_contract_name ON menus(contract_name);
CREATE INDEX IF NOT EXISTS ix_menus_program_type ON menus(program_type);
CREATE INDEX IF NOT EXISTS ix_menus_meal_type ON menus(meal_type);
CREATE INDEX IF NOT EXISTS ix_menus_diet_type ON menus(diet_type);
CREATE INDEX IF NOT EXISTS ix_menus_cycle ON menus(cycle);
CREATE INDEX IF NOT EXISTS ix_menus_status ON menus(status);
CREATE INDEX IF NOT EXISTS ix_menus_is_favorite ON menus(is_favorite);

CREATE TABLE IF NOT EXISTS menu_items (
  id SERIAL PRIMARY KEY,
  menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
  recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id),
  position INTEGER NOT NULL DEFAULT 0,
  day_index INTEGER NOT NULL DEFAULT 0,
  meal_slot VARCHAR(50),
  component_key VARCHAR(50),
  is_alternate BOOLEAN NOT NULL DEFAULT FALSE,
  source_type VARCHAR(50) NOT NULL DEFAULT 'manual'
);

CREATE INDEX IF NOT EXISTS ix_menu_items_menu_id ON menu_items(menu_id);
CREATE INDEX IF NOT EXISTS ix_menu_items_recipe_id ON menu_items(recipe_id);

CREATE TABLE IF NOT EXISTS menu_comments (
  id SERIAL PRIMARY KEY,
  menu_id INTEGER NOT NULL REFERENCES menus(id) ON DELETE CASCADE,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  action VARCHAR(100) NOT NULL,
  author VARCHAR(255) NOT NULL,
  role VARCHAR(100) NOT NULL,
  body TEXT NOT NULL,
  visibility VARCHAR(100) NOT NULL DEFAULT 'Admin and provider',
  badge_class VARCHAR(50) NOT NULL DEFAULT 'brand',
  is_user_comment BOOLEAN NOT NULL DEFAULT TRUE,
  target_type VARCHAR(50) NOT NULL DEFAULT 'menu',
  target_label VARCHAR(255),
  day_index INTEGER,
  meal_slot VARCHAR(100),
  component_key VARCHAR(100),
  recipe_id INTEGER,
  nutrient_key VARCHAR(100),
  review_status VARCHAR(50) NOT NULL DEFAULT 'open'
);

CREATE INDEX IF NOT EXISTS ix_menu_comments_menu_id ON menu_comments(menu_id);
CREATE INDEX IF NOT EXISTS ix_menu_comments_target_type ON menu_comments(target_type);
CREATE INDEX IF NOT EXISTS ix_menu_comments_review_status ON menu_comments(review_status);

CREATE TABLE IF NOT EXISTS historical_menus (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  service_date DATE NOT NULL,
  program_type VARCHAR(100),
  meal_type VARCHAR(100),
  menu_coverage VARCHAR(100),
  diet_type VARCHAR(100),
  menu_duration_type VARCHAR(100),
  meal_served_format VARCHAR(150),
  menu_tags JSONB NOT NULL DEFAULT '[]'::jsonb,
  cycle VARCHAR(100),
  days_per_week INTEGER NOT NULL DEFAULT 5,
  contracts JSONB NOT NULL DEFAULT '[]'::jsonb,
  sample_category VARCHAR(100),
  passes_nutrition BOOLEAN NOT NULL DEFAULT TRUE,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_historical_menus_program_type ON historical_menus(program_type);
CREATE INDEX IF NOT EXISTS ix_historical_menus_meal_type ON historical_menus(meal_type);
CREATE INDEX IF NOT EXISTS ix_historical_menus_diet_type ON historical_menus(diet_type);
CREATE INDEX IF NOT EXISTS ix_historical_menus_cycle ON historical_menus(cycle);
CREATE INDEX IF NOT EXISTS ix_historical_menus_passes_nutrition ON historical_menus(passes_nutrition);

CREATE TABLE IF NOT EXISTS historical_menu_items (
  id SERIAL PRIMARY KEY,
  historical_menu_id INTEGER NOT NULL REFERENCES historical_menus(id) ON DELETE CASCADE,
  recipe_id INTEGER NOT NULL REFERENCES recipes(recipe_id),
  position INTEGER NOT NULL DEFAULT 0,
  meal_slot VARCHAR(50)
);

CREATE INDEX IF NOT EXISTS ix_historical_menu_items_historical_menu_id ON historical_menu_items(historical_menu_id);
CREATE INDEX IF NOT EXISTS ix_historical_menu_items_recipe_id ON historical_menu_items(recipe_id);

CREATE TABLE IF NOT EXISTS nutrient_thresholds (
  id SERIAL PRIMARY KEY,
  nutrient_key VARCHAR(50) NOT NULL UNIQUE,
  low_fail DOUBLE PRECISION,
  low_warn DOUBLE PRECISION,
  high_warn DOUBLE PRECISION,
  high_fail DOUBLE PRECISION,
  unit VARCHAR(20) NOT NULL DEFAULT ''
);

CREATE INDEX IF NOT EXISTS ix_nutrient_thresholds_nutrient_key ON nutrient_thresholds(nutrient_key);

CREATE TABLE IF NOT EXISTS recommendation_logs (
  id SERIAL PRIMARY KEY,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  endpoint VARCHAR(100) NOT NULL,
  selected_recipe_ids JSONB NOT NULL DEFAULT '[]'::jsonb,
  result_count INTEGER NOT NULL DEFAULT 0,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);
