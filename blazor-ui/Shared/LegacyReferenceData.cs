namespace NycAging.Web.Shared;

public static class LegacyReferenceData
{
    public static readonly string[] ProgramTypes =
    [
        "Congregate",
        "Home Delivered Meal"
    ];

    public static readonly string[] MealTypes =
    [
        "Breakfast",
        "Lunch",
        "Dinner"
    ];

    public static readonly string[] MenuCoverageOptions =
    [
        "Breakfast + Lunch + Dinner",
        "Breakfast + Lunch",
        "Lunch + Dinner",
        "Breakfast only",
        "Lunch only",
        "Dinner only"
    ];

    public static readonly string[] DietTypes =
    [
        "Regular",
        "Medically Tailored Meal - Very Low Sodium",
        "Vegetarian",
        "Kosher",
        "Halal",
        "Dairy-Free"
    ];

    public static readonly string[] MenuDurationTypes =
    [
        "Less Than 5-day Menu",
        "Regular",
        "Medically Tailored Meal - Very Low Sodium"
    ];

    public static readonly string[] MealServedFormats =
    [
        "Cold",
        "Fresh Chilled",
        "Hot",
        "Frozen",
        "5-day hot, 2-day frozen",
        "5-day hot, 2-day fresh chilled",
        "5-day hot, 2-day cold",
        "5-day hot, 1-day frozen, 1-day cold",
        "5-day hot, 1-day frozen, 1-day fresh chilled",
        "5-day hot, 1-day cold, 1-day fresh chilled",
        "6-day hot, 1-day fresh chilled"
    ];

    public static readonly string[] MenuTags =
    [
        "Vegetarian"
    ];

    public static readonly string[] Cycles =
    [
        "Spring/Summer",
        "Fall/Winter",
        "Spring",
        "Summer",
        "Fall",
        "Winter",
        "Fiscal Year"
    ];

    public static readonly string[] MenuStatuses =
    [
        "Draft",
        "Submitted to Contract(s) for Review",
        "Returned for correction (from NYC Aging)",
        "Approved",
        "Submitted To NYC Aging",
        "NYC Aging Edited",
        "Completed",
        "Deleted",
        "Resubmitted to NYC Aging",
        "Contract(s) Reviewed Menu"
    ];

    public static readonly string[] ContractNames =
    [
        "ABSW OAC",
        "Aging Through Arts Center (Encore at St Malachy's)",
        "Agudath Israel Brookdale Senior Center",
        "Agudath Israel Moriah Older Adult Luncheon Club",
        "Agudath Israel of America Boro Park Senior Citizens Center",
        "Albany OAC",
        "Allen AME Community Senior Citizens Centers - Linden Blvd",
        "Allen AME Rockaway Blvd Senior Center",
        "Allen AME Theodora Jackson Center",
        "Alpha Phi Alpha Senior Citizens OAC",
        "AMICO 59th St Senior Citizen Ctr",
        "ANDERSON NEIGHBORHOOD SENIOR CENTER",
        "AR (Arrochar)",
        "ARC XVI A. Philip Randolph OAC",
        "ARC XVI Central Harlem Center",
        "ARC XVI Fort Washington OAC",
        "ARC XVI JACKIE ROBINSON NEIGHBORHOOD SENIOR CTR",
        "Arturo Schomburg",
        "Astoria NSC",
        "QUEENS COMM HOUSE HOME DELIVERED MEALS AT FOREST HILLS - QUEENS 3"
    ];

    public static readonly string[] NutritionAdvisors =
    [
        "NYC Aging Nutrition Unit",
        "Contract Nutrition Review Team",
        "Malek, Esther",
        "Regional Nutrition Advisor",
        "DFTA Menu Review"
    ];

    public static readonly string[] RecipeViewOptions =
    [
        "[All]",
        "Public",
        "Sponsor Private",
        "Caterer Private"
    ];

    public static readonly LegacyRecipeTile[] RecipeTiles =
    [
        new("Appetizers", "Optional starters and small menu items.", "appetizer"),
        new("Breakfast", "Breakfast recipes and morning meal components.", "breakfast"),
        new("Grains", "Whole grains, rolls, rice, pasta, and cereal items.", "grains"),
        new("Entrees", "Main dishes, proteins, and plant-based entrees.", "entree"),
        new("Vegetarian", "Vegetarian and plant-forward recipes.", "vegetarian"),
        new("Vegetables", "Starchy and non-starchy vegetable recipes.", "vegetable"),
        new("Dairy-Free", "Dairy-free and non-dairy equivalent options.", "dairy-free")
    ];

    public static readonly LegacyFilterGroup[] RecipeFilterGroups =
    [
        new("meal-components", "Meal Components",
        [
            "Entrée",
            "Appetizer",
            "Vegetable",
            "Fruit",
            "Grains",
            "Milk/Yogurt",
            "Juice or Dessert",
            "Condiments",
            "Breakfast",
            "Non-Starchy Vegetable",
            "Starchy vegetable",
            "Plant-based Entrée",
            "Whole Grains",
            "Plant-based Entrée (1/2)",
            "Plant-based Feature"
        ]),
        new("critical-nutrients", "Critical Nutrients",
        [
            "Very Low Sodium",
            "Good Source of Iron",
            "Good Source of Calcium",
            "Good source of Vitamin D",
            "Good for hot meal",
            "Good for cold meal",
            "Good for frozen meal",
            "Good Source of Vitamin A",
            "Good Source of Vitamin C",
            "Good Source of Fiber",
            "Good Source of Potassium"
        ]),
        new("cuisines", "Cuisines",
        [
            "Chinese Cuisine",
            "Latin Cuisine",
            "Caribbean Cuisine",
            "Standard Cuisine",
            "Mediterranean Cuisine",
            "Russian Cuisine",
            "Polish Cuisine",
            "Korean Cuisine",
            "Halal",
            "Kosher",
            "Vegetarian Cuisine",
            "Indian Cuisine"
        ]),
        new("dietary-restrictions", "Dietary Restrictions",
        [
            "Vegetarian",
            "Dairy-Free"
        ])
    ];

    public static readonly LegacyMealComponent[] MealComponents =
    [
        new("appetizer", "Appetizer", "Optional", "Optional starter or side item.", true),
        new("entree", "Entrée", "Required: 1 serving", "Main recipe for the meal.", false),
        new("grains", "Grains", "Required: 1 serving", "Grain, bread, rice, pasta, or whole grain item.", false),
        new("vegetable", "Vegetable", "Required: 1 serving non-starchy", "Non-starchy or starchy vegetable.", false),
        new("fruit", "Fruit", "Required: 1 serving", "Fruit component for the meal.", false),
        new("dairy", "Dairy or non-dairy equivalent", "Required: 1 serving", "Milk, yogurt, or approved non-dairy equivalent.", false),
        new("juice-dessert", "Juice (does not count as fruit) or Dessert", "Optional", "Optional juice or dessert item.", true),
        new("condiments", "Condiments", "Optional", "Optional condiments.", true),
        new("alternate", "Alternate", "Optional", "Alternate menu item.", true)
    ];

    public static readonly LegacyReportDefinition[] Reports =
    [
        new("monthly-calendar", "Menu - Monthly Calendar", "Menu Related Report", "This report displays and prints menus by calendar month.", ["PDF", "Excel", "Word"], true, true, false, true, true),
        new("daily-menu", "Menu - Daily Menu", "Menu Related Report", "This report displays and prints menus by day.", ["PDF", "Excel", "Word"], true, true, true, false, false),
        new("daily-labels", "Nutrition Fact Labels - Daily", "Menu Related Report", "This report displays and prints labels of the Nutrition Facts panel by individual day.", ["PDF"], false, true, true, false, false),
        new("nutrition-daily", "Nutritional Analysis - Daily", "Menu Related Report", "This report displays and prints a list of nutritional values for a specific day of the week in a chosen menu cycle.", ["PDF"], false, true, true, false, false),
        new("nutrition-weekly-average", "Nutritional Analysis - Weekly Average", "Menu Related Report", "This report displays and prints average nutritional values for a specified week in a chosen menu cycle.", ["PDF"], false, true, true, false, false),
        new("daily-menu-nutrition", "Menu - Daily Menu with Nutrition Facts Panel", "Menu Related Report", "This report displays and prints menus by day with the Nutrition Facts Panel included.", ["PDF"], true, true, true, false, false),
        new("weekly-labels", "Nutrition Fact Labels - Weekly", "Menu Related Report", "This report displays and prints daily Nutrition Facts panel information for a selected weekly menu.", ["PDF"], true, true, true, false, false),
        new("cycle-dates", "Menu - Cycle with Dates by Contract & Menu ID", "Menu Related Report", "This report displays and prints weekly menus for the full menu cycle selected.", ["PDF"], false, true, false, false, false),
        new("staffid-labels", "Nutrition Facts Labels by StaffID - Daily", "Menu Related Report", "This report displays and prints labels of the Nutrition Facts panel by individual day.", ["PDF"], false, true, true, false, false),
        new("recipe-link-test", "Test of Recipe Link", "Menu Related Report", "Test report for recipe link output.", ["PDF"], false, false, false, false, false),
        new("count-cycle-recipe", "Count Menus With Cycle ID By Recipe ID", "Administrative Related Report", "This report displays total menu count for all menus active within a date range and recipe input.", ["PDF", "Excel"], false, false, false, false, false)
    ];

    public static readonly string[] ResourceTypes =
    [
        "Forms",
        "Nutrition Messages",
        "Nutrition Policies",
        "Quarterly Food Service Trainings"
    ];

    public static readonly LegacyResourceItem[] Resources =
    [
        new("Active Nutrition Educators List", "Forms", "~/Resource/Active Nutrition Educators List_Apr 2024.pdf", "Current contact list for active nutrition educators and program support.", new DateTime(2024, 4, 15), "Staff", "NYC Aging Nutrition Unit"),
        new("Catered Meals - Weekly Meal Record", "Forms", "~/Resource/Weekly Meal Record.pdf", "Weekly tracking form for catered meal service counts and notes.", new DateTime(2026, 1, 10), "Providers", "NYC Aging Program Operations"),
        new("Catered Meals - Issues Log", "Forms", "~/Resource/Catered meals issues log.pdf", "Log for documenting catered meal delivery, quality, or service issues.", new DateTime(2026, 1, 10), "Providers", "NYC Aging Program Operations"),
        new("Catering Subcontractor Information Form", "Forms", "~/Resource/Catering Subcontractor Information Form.pdf", "Provider form for recording subcontractor and catering service details.", new DateTime(2026, 3, 15), "Providers", "NYC Aging Program Operations"),
        new("Cleaning Schedule - Instructions", "Forms", "~/Resource/Cleaning Schedules - Instructions.pdf", "Instructions for maintaining routine cleaning schedules and documentation.", new DateTime(2025, 10, 8), "Providers", "NYC Aging Food Service"),
        new("Food Cost Report - Monthly", "Forms", "~/Resource/Monthly Food Cost Report.pdf", "Monthly worksheet for reporting food costs and related meal-service expenses.", new DateTime(2026, 1, 10), "Providers", "NYC Aging Program Operations"),
        new("Food Used Record - Daily", "Forms", "~/Resource/Daily Food Used Record.pdf", "Daily record for documenting food used during meal preparation or service.", new DateTime(2026, 1, 10), "Providers", "NYC Aging Food Service"),
        new("Refrigerator and Freezer Temperature Log", "Forms", "~/Resource/Equipment Temperature Log.pdf", "Temperature log for refrigerator and freezer monitoring.", new DateTime(2026, 1, 10), "Providers", "NYC Aging Food Service"),
        new("Taste Test Log - Monthly (HDM)", "Forms", "~/Resource/Taste Test log_Monthly.pdf", "Monthly home-delivered meal taste-test documentation form.", new DateTime(2026, 2, 20), "Providers", "NYC Aging Nutrition Unit"),
        new("Cultural Meals - What is Halal?", "Nutrition Messages", "~/Resource/What is Halal.docx.pdf", "Reference message explaining halal meal considerations for providers.", new DateTime(2025, 9, 12), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("Cultural Meals - What is Kosher?", "Nutrition Messages", "~/Resource/What is Kosher.pdf", "Reference message explaining kosher meal considerations for providers.", new DateTime(2025, 9, 12), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("DSNY Organics Collection", "Nutrition Messages", "~/Resource/DSNY Resources_Organics Collection Presentation_Oct 2023.pdf", "Training-style reference on organics collection and food waste handling.", new DateTime(2023, 10, 18), "Providers", "NYC Aging Training"),
        new("Plant-Based Resources", "Nutrition Messages", "~/Resource/Plant Based Meal Resources - VN DPG 2024.pdf", "Reference packet for plant-based menu planning and nutrition guidance.", new DateTime(2024, 8, 6), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("NYC Food Standards - 2026", "Nutrition Policies", "~/Resource/NYC Food Standards 2026.pdf", "Full 2026 food standards used for menu and product review.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("NYC Food Standards - 2026 Example Product List", "Nutrition Policies", "~/Resource/food-standards-example-product-list.pdf", "Example product list for applying the 2026 food standards.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("NYC Food Standards - 2026 Fact Sheet", "Nutrition Policies", "~/Resource/food-standards-fact-sheet.pdf", "Short summary sheet for key 2026 food standards requirements.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("NYC Food Standards - Quick Reference Chart", "Nutrition Policies", "~/Resource/Quick Reference Nutrient Chart_3 4 25.pdf", "Quick chart for checking common nutrient limits and targets.", new DateTime(2025, 3, 4), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("NYC Food Standards - Sodium Quick Reference Chart (2026)", "Nutrition Policies", "~/Resource/Sodium Reference Chart_2026.pdf", "Quick sodium reference for reviewing recipes, products, and menus.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("Menu Guidelines - Breakfast (2026)", "Nutrition Policies", "~/Resource/Breakfast Guidelines_2026.pdf", "Breakfast menu pattern and nutrition guidance for 2026 review.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("Menu Guidelines - Lunch and Dinner (2026)", "Nutrition Policies", "~/Resource/Lunch and Dinner Guidelines_2026.pdf", "Lunch and dinner menu pattern and nutrition guidance for 2026 review.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("Menu Guidelines - Plant-Based Protein Guide (2026)", "Nutrition Policies", "~/Resource/Plant-Based Protein Guide_2026.pdf", "Guide for reviewing plant-based protein servings and menu use.", new DateTime(2026, 7, 1), "Staff + Providers", "NYC Aging Nutrition Unit"),
        new("Quarterly Food Service Training - Catered Meals", "Quarterly Food Service Trainings", "~/Resource/Quarterly Food Service Training - Catered Meals.pdf", "Quarterly training material for catered meal service expectations.", new DateTime(2026, 4, 10), "Providers", "NYC Aging Training"),
        new("Quarterly Food Service Training - Cleaning and Sanitizing Food Contact Surfaces", "Quarterly Food Service Trainings", "~/Resource/Quarterly Food Service Training - Cleaning and Sanitizing Food Contact Surfaces.pdf", "Training material for cleaning and sanitizing food contact surfaces.", new DateTime(2026, 4, 10), "Providers", "NYC Aging Training"),
        new("Quarterly Food Service Training - Safe Food Temperatures", "Quarterly Food Service Trainings", "~/Resource/Quarterly Food Service Training - Safe Food Temperatures.pdf", "Training material covering safe hot and cold food temperatures.", new DateTime(2026, 4, 10), "Providers", "NYC Aging Training"),
        new("Quarterly Food Service Training - Thermometer Use", "Quarterly Food Service Trainings", "~/Resource/Quarterly Food Service Training - Thermometer Use.pdf", "Training material on thermometer use and temperature checks.", new DateTime(2026, 4, 10), "Providers", "NYC Aging Training")
    ];

    public static string NormalizeFilterValue(string value) =>
        value.Replace("Entrée", "entree", StringComparison.OrdinalIgnoreCase)
             .Replace("Plant-based", "plant based", StringComparison.OrdinalIgnoreCase)
             .Replace("Milk/Yogurt", "milk yogurt", StringComparison.OrdinalIgnoreCase)
             .Replace("-", " ", StringComparison.OrdinalIgnoreCase)
             .Replace("/", " ", StringComparison.OrdinalIgnoreCase)
             .ToLowerInvariant();
}

public sealed record LegacyRecipeTile(string Label, string Description, string FilterValue);

public sealed record LegacyFilterGroup(string Key, string Label, string[] Options);

public sealed record LegacyMealComponent(string Key, string Label, string Requirement, string HelpText, bool Optional);

public sealed record LegacyReportDefinition(
    string Key,
    string Name,
    string Group,
    string Description,
    string[] ExportFormats,
    bool NeedsContractId,
    bool NeedsMenuId,
    bool NeedsDate,
    bool NeedsYearMonth,
    bool NeedsMealType);

public sealed record LegacyResourceItem(
    string Title,
    string ResourceType,
    string Path,
    string Description = "",
    DateTime? LastUpdated = null,
    string Audience = "Staff + Providers",
    string UploadedBy = "NYC Aging Nutrition Unit");
