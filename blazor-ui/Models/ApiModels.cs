using System.Text.Json.Serialization;

namespace NycAging.Web.Models;

public enum MealSlot
{
    Breakfast,
    Lunch,
    Dinner
}

public sealed class RecipeDto
{
    public int RecipeId { get; set; }
    public string RecipeName { get; set; } = string.Empty;
    public string MealType { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public decimal Calories { get; set; }
    public decimal SodiumMg { get; set; }
    public decimal ProteinG { get; set; }
    public decimal FiberG { get; set; }
    public decimal FatG { get; set; }
    public List<string> Tags { get; set; } = [];
    public bool IsApproved { get; set; }
    public List<string> Ingredients { get; set; } = [];
    public List<string> Instructions { get; set; } = [];
    public string? ServingSize { get; set; }
    public int YieldServings { get; set; } = 50;
    public string? ScaleNote { get; set; }
    public string? ContributedBy { get; set; }
    public DateTime? CreatedOn { get; set; }
    public bool IsPublic { get; set; } = true;
    public bool IsFavorite { get; set; }
    public bool IsDead { get; set; }
    public List<string> NutrientClaims { get; set; } = [];
    public decimal VitaminCMg { get; set; }
    public decimal CalciumMg { get; set; }
    public decimal SaturatedFatG { get; set; }
    public decimal TransFatG { get; set; }
    public decimal CholesterolMg { get; set; }
    public decimal CarbohydratesG { get; set; }
    public decimal TotalSugarsG { get; set; }
    public decimal AddedSugarsG { get; set; }
    public decimal VitaminDMcg { get; set; }
    public decimal IronMg { get; set; }
    public decimal PotassiumMg { get; set; }

    public bool Matches(string searchText)
    {
        var query = searchText.Trim().ToLowerInvariant();
        if (string.IsNullOrWhiteSpace(query))
        {
            return true;
        }

        var haystack = string.Join(' ', [RecipeName, MealType, Category, string.Join(' ', Tags), string.Join(' ', Ingredients), string.Join(' ', NutrientClaims)]).ToLowerInvariant();
        return query.Split(' ', StringSplitOptions.RemoveEmptyEntries).All(haystack.Contains);
    }

    public bool IsSuitableForMealSlot(MealSlot mealSlot) => mealSlot switch
    {
        MealSlot.Breakfast => MealType.Equals("breakfast", StringComparison.OrdinalIgnoreCase) || MealType.Equals("snack", StringComparison.OrdinalIgnoreCase),
        MealSlot.Lunch => MealType.Equals("lunch", StringComparison.OrdinalIgnoreCase) || MealType.Equals("snack", StringComparison.OrdinalIgnoreCase),
        MealSlot.Dinner => MealType.Equals("dinner", StringComparison.OrdinalIgnoreCase) || MealType.Equals("snack", StringComparison.OrdinalIgnoreCase),
        _ => false
    };
}

public sealed class RecipeCreateRequest
{
    public string RecipeName { get; set; } = string.Empty;
    public string MealType { get; set; } = "lunch";
    public string Category { get; set; } = "entree";
    public decimal Calories { get; set; }
    public decimal SodiumMg { get; set; }
    public decimal ProteinG { get; set; }
    public decimal FiberG { get; set; }
    public decimal FatG { get; set; }
    public List<string> Tags { get; set; } = [];
    public bool IsApproved { get; set; }
    public List<string> Ingredients { get; set; } = [];
    public List<string> Instructions { get; set; } = [];
    public string? ServingSize { get; set; }
    public int YieldServings { get; set; } = 1;
    public string? ScaleNote { get; set; }
    public string? ContributedBy { get; set; }
    public DateTime? CreatedOn { get; set; }
    public bool IsPublic { get; set; } = true;
    public bool IsFavorite { get; set; }
    public bool IsDead { get; set; }
    public List<string> NutrientClaims { get; set; } = [];
    public decimal VitaminCMg { get; set; }
    public decimal CalciumMg { get; set; }
    public decimal SaturatedFatG { get; set; }
    public decimal TransFatG { get; set; }
    public decimal CholesterolMg { get; set; }
    public decimal CarbohydratesG { get; set; }
    public decimal TotalSugarsG { get; set; }
    public decimal AddedSugarsG { get; set; }
    public decimal VitaminDMcg { get; set; }
    public decimal IronMg { get; set; }
    public decimal PotassiumMg { get; set; }
}

public sealed class RecipeAttachmentDto
{
    public int Id { get; set; }
    public int RecipeId { get; set; }
    public string FileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = "application/octet-stream";
    public string FileKind { get; set; } = "supporting_document";
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; }
}

public sealed class RecipeReviewCommentDto
{
    public int Id { get; set; }
    public int RecipeId { get; set; }
    public DateTime CreatedAt { get; set; }
    public string Action { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public string Visibility { get; set; } = "Admin and provider";
    public string BadgeClass { get; set; } = "brand";
    public bool IsUserComment { get; set; } = true;
    public string TargetType { get; set; } = "recipe";
    public string? TargetLabel { get; set; }
    public string? NutrientKey { get; set; }
    public string ReviewStatus { get; set; } = "open";
}

public sealed class RecipeReviewCommentCreateRequest
{
    public string Action { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public string Visibility { get; set; } = "Admin and provider";
    public string BadgeClass { get; set; } = "brand";
    public bool IsUserComment { get; set; } = true;
    public string TargetType { get; set; } = "recipe";
    public string? TargetLabel { get; set; }
    public string? NutrientKey { get; set; }
    public string ReviewStatus { get; set; } = "open";
}

public sealed class HomeUpdateDto
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string UpdateType { get; set; } = "Announcement";
    public string Summary { get; set; } = string.Empty;
    public string Content { get; set; } = string.Empty;
    public DateTime PublishedOn { get; set; }
    public string? ImageSource { get; set; }
}

public sealed class HomeUpdateCreateRequest
{
    public string Title { get; set; } = string.Empty;
    public string UpdateType { get; set; } = "Announcement";
    public string Summary { get; set; } = string.Empty;
    public string? Content { get; set; }
    public DateTime PublishedOn { get; set; } = DateTime.Today;
    public string? ImageSource { get; set; }
}

public sealed class RecipeHomeCategorySettingDto
{
    public string CategoryKey { get; set; } = string.Empty;
    public bool IsVisible { get; set; }
    public string? DisplayLabel { get; set; }
    public string? Description { get; set; }
}

public sealed class MenuItemInput
{
    public int RecipeId { get; set; }
    public int Position { get; set; }
    public int DayIndex { get; set; }
    public string MealSlot { get; set; } = string.Empty;
    public string? ComponentKey { get; set; }
    public bool IsAlternate { get; set; }
    public string SourceType { get; set; } = "manual";
}

public sealed class MenuAnalysisRequest
{
    public List<int> RecipeIds { get; set; } = [];
    public List<MenuItemInput> Items { get; set; } = [];
}

public sealed class MenuCreateRequest
{
    public string Name { get; set; } = string.Empty;
    public string? ContractName { get; set; }
    public string? ProgramType { get; set; }
    public string? MealType { get; set; }
    public string? MenuCoverage { get; set; }
    public string? DietType { get; set; }
    public string? MenuFormat { get; set; }
    public string? MenuDurationType { get; set; }
    public string? MealServedFormat { get; set; }
    public List<string> MenuTags { get; set; } = [];
    public string? Cycle { get; set; }
    public DateTime? CycleStartDate { get; set; }
    public DateTime? CycleEndDate { get; set; }
    public List<string> Contracts { get; set; } = [];
    public int? SampleMenuId { get; set; }
    public List<int> CompletedWeeks { get; set; } = [];
    public List<string> SubmittedPrograms { get; set; } = [];
    public string Status { get; set; } = "Draft";
    public DateTime? StatusDate { get; set; }
    public string? SubmittedTo { get; set; }
    public DateTime? SubmittedToNycAgingOn { get; set; }
    public string? NutritionAdvisor { get; set; }
    public string? CreatedBy { get; set; }
    public DateTime StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public int DaysPerWeek { get; set; }
    public int CycleWeek { get; set; }
    public string? Notes { get; set; }
    public string? ReturnedComments { get; set; }
    public string? ApprovalNotes { get; set; }
    public bool IsFavorite { get; set; }
    public List<MenuItemInput> Items { get; set; } = [];
}

public sealed class MenuCreateResponse
{
    public int Id { get; set; }
}

public sealed class ResourceFileDto
{
    public int Id { get; set; }
    public string Title { get; set; } = string.Empty;
    public string ResourceType { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Audience { get; set; } = "Staff + Providers";
    public DateTime LastUpdated { get; set; }
    public string UploadedBy { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string ContentType { get; set; } = "application/octet-stream";
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; }
}

public sealed class MenuSummaryDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? ContractName { get; set; }
    public string? ProgramType { get; set; }
    public string? MealType { get; set; }
    public string? MenuCoverage { get; set; }
    public string? DietType { get; set; }
    public string? MenuFormat { get; set; }
    public string? MenuDurationType { get; set; }
    public string? MealServedFormat { get; set; }
    public List<string> MenuTags { get; set; } = [];
    public string? Cycle { get; set; }
    public DateTime? CycleStartDate { get; set; }
    public DateTime? CycleEndDate { get; set; }
    public List<string> Contracts { get; set; } = [];
    public int? SampleMenuId { get; set; }
    public List<int> CompletedWeeks { get; set; } = [];
    public List<string> SubmittedPrograms { get; set; } = [];
    public string Status { get; set; } = "Draft";
    public DateTime? StatusDate { get; set; }
    public string? SubmittedTo { get; set; }
    public DateTime? SubmittedToNycAgingOn { get; set; }
    public string? NutritionAdvisor { get; set; }
    public string? CreatedBy { get; set; }
    public DateTime ServiceDate { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public int DaysPerWeek { get; set; }
    public int CycleWeek { get; set; }
    public DateTime CreatedAt { get; set; }
    public string? Notes { get; set; }
    public string? ReturnedComments { get; set; }
    public string? ApprovalNotes { get; set; }
    public bool IsFavorite { get; set; }
    public int ItemCount { get; set; }
    public List<string> RecipeNames { get; set; } = [];
}

public sealed class MenuReviewCommentDto
{
    public int Id { get; set; }
    public int MenuId { get; set; }
    public DateTime CreatedAt { get; set; }
    public string Action { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public string Visibility { get; set; } = "Admin and provider";
    public string BadgeClass { get; set; } = "brand";
    public bool IsUserComment { get; set; } = true;
    public string TargetType { get; set; } = "menu";
    public string? TargetLabel { get; set; }
    public int? DayIndex { get; set; }
    public string? MealSlot { get; set; }
    public string? ComponentKey { get; set; }
    public int? RecipeId { get; set; }
    public string? NutrientKey { get; set; }
    public string ReviewStatus { get; set; } = "open";
}

public sealed class MenuReviewCommentCreateRequest
{
    public string Action { get; set; } = string.Empty;
    public string Author { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public string Body { get; set; } = string.Empty;
    public string Visibility { get; set; } = "Admin and provider";
    public string BadgeClass { get; set; } = "brand";
    public bool IsUserComment { get; set; } = true;
    public string TargetType { get; set; } = "menu";
    public string? TargetLabel { get; set; }
    public int? DayIndex { get; set; }
    public string? MealSlot { get; set; }
    public string? ComponentKey { get; set; }
    public int? RecipeId { get; set; }
    public string? NutrientKey { get; set; }
    public string ReviewStatus { get; set; } = "open";
}

public sealed class HistoricalMenuSummaryDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime ServiceDate { get; set; }
    public string? ProgramType { get; set; }
    public string? MealType { get; set; }
    public string? MenuCoverage { get; set; }
    public string? DietType { get; set; }
    public string? MenuDurationType { get; set; }
    public string? MealServedFormat { get; set; }
    public List<string> MenuTags { get; set; } = [];
    public string? Cycle { get; set; }
    public int DaysPerWeek { get; set; } = 5;
    public List<string> Contracts { get; set; } = [];
    public string? SampleCategory { get; set; }
    public bool PassesNutrition { get; set; }
    public string? Notes { get; set; }
    public int ItemCount { get; set; }
    public List<string> RecipeNames { get; set; } = [];
}

public sealed class HistoricalMenuItemDto
{
    public int RecipeId { get; set; }
    public int Position { get; set; }
    public int DayIndex { get; set; }
    public string? MealSlot { get; set; }
    public string? ComponentKey { get; set; }
    public bool IsAlternate { get; set; }
    public string SourceType { get; set; } = "sample";
    public RecipeDto Recipe { get; set; } = new();
}

public sealed class HistoricalMenuDetailDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime ServiceDate { get; set; }
    public string? ProgramType { get; set; }
    public string? MealType { get; set; }
    public string? MenuCoverage { get; set; }
    public string? DietType { get; set; }
    public string? MenuDurationType { get; set; }
    public string? MealServedFormat { get; set; }
    public List<string> MenuTags { get; set; } = [];
    public string? Cycle { get; set; }
    public int DaysPerWeek { get; set; } = 5;
    public List<string> Contracts { get; set; } = [];
    public string? SampleCategory { get; set; }
    public bool PassesNutrition { get; set; }
    public string? Notes { get; set; }
    public List<HistoricalMenuItemDto> Items { get; set; } = [];
}

public sealed class MenuItemDetailDto
{
    public int RecipeId { get; set; }
    public int Position { get; set; }
    public int DayIndex { get; set; }
    public string MealSlot { get; set; } = string.Empty;
    public string? ComponentKey { get; set; }
    public bool IsAlternate { get; set; }
    public string SourceType { get; set; } = "manual";
    public RecipeDto Recipe { get; set; } = new();
}

public sealed class MenuDetailMenuDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? ContractName { get; set; }
    public string? ProgramType { get; set; }
    public string? MealType { get; set; }
    public string? MenuCoverage { get; set; }
    public string? DietType { get; set; }
    public string? MenuFormat { get; set; }
    public string? MenuDurationType { get; set; }
    public string? MealServedFormat { get; set; }
    public List<string> MenuTags { get; set; } = [];
    public string? Cycle { get; set; }
    public DateTime? CycleStartDate { get; set; }
    public DateTime? CycleEndDate { get; set; }
    public List<string> Contracts { get; set; } = [];
    public int? SampleMenuId { get; set; }
    public List<int> CompletedWeeks { get; set; } = [];
    public List<string> SubmittedPrograms { get; set; } = [];
    public string Status { get; set; } = "Draft";
    public DateTime? StatusDate { get; set; }
    public string? SubmittedTo { get; set; }
    public DateTime? SubmittedToNycAgingOn { get; set; }
    public string? NutritionAdvisor { get; set; }
    public string? CreatedBy { get; set; }
    public DateTime ServiceDate { get; set; }
    public DateTime? StartDate { get; set; }
    public DateTime? EndDate { get; set; }
    public int DaysPerWeek { get; set; }
    public int CycleWeek { get; set; }
    public DateTime CreatedAt { get; set; }
    public string? Notes { get; set; }
    public string? ReturnedComments { get; set; }
    public string? ApprovalNotes { get; set; }
    public bool IsFavorite { get; set; }
    public List<MenuItemDetailDto> Items { get; set; } = [];
}

public sealed class NutrientStatusDto
{
    public string NutrientKey { get; set; } = string.Empty;
    public decimal Total { get; set; }
    public string Unit { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}

public sealed class MealRequirementSuggestionDto
{
    public RecipeDto Recipe { get; set; } = new();
    public decimal Score { get; set; }
    public List<string> Reasons { get; set; } = [];
}

public sealed class MealRequirementDto
{
    public string RuleKey { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
    public List<string> ComponentBadges { get; set; } = [];
    public List<string> MissingComponentBadges { get; set; } = [];
    public List<string> Details { get; set; } = [];
    public List<MealRequirementSuggestionDto> Suggestions { get; set; } = [];
}

public sealed class MenuAnalysisDto
{
    public Dictionary<string, decimal> Totals { get; set; } = [];
    public List<NutrientStatusDto> Statuses { get; set; } = [];
    public List<MealRequirementDto> MealRequirements { get; set; } = [];
    public string OverallStatus { get; set; } = string.Empty;
    public List<RecipeDto> SelectedRecipes { get; set; } = [];
}

public sealed class RecommendationItemDto
{
    public RecipeDto Recipe { get; set; } = new();
    public decimal Score { get; set; }
    public List<string> Reasons { get; set; } = [];
}

public sealed class RevisionsResponseDto
{
    public Dictionary<string, List<RecommendationItemDto>> Suggestions { get; set; } = [];
}

public sealed class SimilarMenuDto
{
    public int Id { get; set; }
    public string Name { get; set; } = string.Empty;
    public DateTime ServiceDate { get; set; }
    public bool PassesNutrition { get; set; }
    public decimal Similarity { get; set; }
    public List<int> RecipeIds { get; set; } = [];
    public string? Notes { get; set; }
}

public sealed class MenuDetailDto
{
    public MenuDetailMenuDto Menu { get; set; } = new();
    public MenuAnalysisDto Analysis { get; set; } = new();
    public List<RecommendationItemDto> Autocomplete { get; set; } = [];
    public Dictionary<string, List<RecommendationItemDto>> Revisions { get; set; } = [];
    public List<SimilarMenuDto> SimilarMenus { get; set; } = [];
}

public sealed class TopRecipeDto
{
    public int RecipeId { get; set; }
    public string RecipeName { get; set; } = string.Empty;
    public int Count { get; set; }
    public string Category { get; set; } = string.Empty;
}

public sealed class TopPairingDto
{
    public string RecipeA { get; set; } = string.Empty;
    public string RecipeB { get; set; } = string.Empty;
    public int Count { get; set; }
}

public sealed class AnalyticsDto
{
    public List<TopRecipeDto> TopRecipes { get; set; } = [];
    public List<TopPairingDto> TopPairings { get; set; } = [];
    public List<Dictionary<string, object>> CategoryCounts { get; set; } = [];
    public List<Dictionary<string, object>> MealTypeCounts { get; set; } = [];
}
