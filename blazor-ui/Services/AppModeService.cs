using NycAging.Web.Models;

namespace NycAging.Web.Services;

public enum AppRole
{
    Admin,
    Provider
}

public sealed class AppModeService
{
    public AppRole CurrentRole { get; private set; } = AppRole.Admin;
    public string ProviderContract { get; private set; } = "ABSW OAC";

    public bool IsAdmin => CurrentRole == AppRole.Admin;
    public bool IsProvider => CurrentRole == AppRole.Provider;

    public event Action? Changed;

    public void SetRole(AppRole role)
    {
        if (CurrentRole == role)
        {
            return;
        }

        CurrentRole = role;
        Changed?.Invoke();
    }

    public bool CanProviderSeeMenu(MenuSummaryDto menu)
    {
        if (IsAdmin)
        {
            return true;
        }

        var matchesContract = (menu.ContractName ?? string.Empty).Equals(ProviderContract, StringComparison.OrdinalIgnoreCase)
            || menu.Contracts.Any(contract => contract.Equals(ProviderContract, StringComparison.OrdinalIgnoreCase));
        var visibleStatus = ProviderMenuStatuses.Contains(menu.Status, StringComparer.OrdinalIgnoreCase);
        return matchesContract && visibleStatus;
    }

    public static readonly string[] ProviderMenuStatuses =
    [
        "Submitted to Contract(s) for Review",
        "Contract(s) Reviewed Menu",
        "Submitted To NYC Aging",
        "Returned for correction (from NYC Aging)",
        "Resubmitted To NYC Aging",
        "Approved",
        "Completed",
        "NYC Aging Edited"
    ];
}
