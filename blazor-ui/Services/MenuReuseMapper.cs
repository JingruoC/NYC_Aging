using NycAging.Web.Models;

namespace NycAging.Web.Services;

public static class MenuReuseMapper
{
    public static MenuCreateRequest FromMenu(MenuDetailDto detail, bool preserveDates, string sourceType)
    {
        var menu = detail.Menu;
        var daysPerWeek = Math.Clamp(menu.DaysPerWeek <= 0 ? 5 : menu.DaysPerWeek, 1, 7);
        var startDate = preserveDates
            ? menu.StartDate ?? menu.ServiceDate
            : StartOfServiceWeek(DateTime.Today);

        return new MenuCreateRequest
        {
            Name = preserveDates ? menu.Name : $"Copy of {menu.Name}",
            ContractName = menu.ContractName,
            ProgramType = menu.ProgramType,
            MealType = menu.MealType,
            MenuCoverage = menu.MenuCoverage,
            DietType = menu.DietType,
            MenuFormat = menu.MenuFormat ?? "Weekly",
            MenuDurationType = menu.MenuDurationType,
            MealServedFormat = menu.MealServedFormat,
            MenuTags = [.. menu.MenuTags],
            Cycle = menu.Cycle,
            CycleStartDate = preserveDates ? menu.CycleStartDate : startDate,
            CycleEndDate = preserveDates ? menu.CycleEndDate : startDate.AddMonths(6),
            Contracts = menu.Contracts.Count > 0
                ? [.. menu.Contracts]
                : string.IsNullOrWhiteSpace(menu.ContractName) ? [] : [menu.ContractName],
            SampleMenuId = menu.SampleMenuId,
            CompletedWeeks = preserveDates ? [.. menu.CompletedWeeks] : [],
            SubmittedPrograms = [.. menu.SubmittedPrograms],
            Status = "Draft",
            StatusDate = DateTime.Today,
            SubmittedTo = menu.SubmittedTo,
            SubmittedToNycAgingOn = preserveDates ? menu.SubmittedToNycAgingOn : null,
            NutritionAdvisor = menu.NutritionAdvisor,
            CreatedBy = menu.CreatedBy,
            StartDate = startDate,
            EndDate = startDate.AddDays(daysPerWeek - 1),
            DaysPerWeek = daysPerWeek,
            CycleWeek = preserveDates ? Math.Max(1, menu.CycleWeek) : 1,
            Notes = preserveDates ? menu.Notes : $"Started from Menu ID {menu.Id}: {menu.Name}.",
            ReturnedComments = preserveDates ? menu.ReturnedComments : null,
            ApprovalNotes = preserveDates ? menu.ApprovalNotes : null,
            IsFavorite = false,
            Items = menu.Items
                .OrderBy(item => item.DayIndex)
                .ThenBy(item => item.Position)
                .Select((item, index) => new MenuItemInput
                {
                    RecipeId = item.RecipeId,
                    Position = index + 1,
                    DayIndex = Math.Clamp(item.DayIndex, 0, daysPerWeek - 1),
                    MealSlot = item.MealSlot,
                    ComponentKey = item.ComponentKey,
                    IsAlternate = item.IsAlternate,
                    SourceType = sourceType
                })
                .ToList()
        };
    }

    private static DateTime StartOfServiceWeek(DateTime date)
    {
        var daysSinceMonday = ((int)date.DayOfWeek - (int)DayOfWeek.Monday + 7) % 7;
        return date.Date.AddDays(-daysSinceMonday);
    }
}
