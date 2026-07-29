using NycAging.Web.Models;

namespace NycAging.Web.Services;

public sealed class MenuDraftService
{
    public MenuCreateRequest? Draft { get; private set; }

    public void Set(MenuCreateRequest draft)
    {
        Draft = draft;
    }

    public MenuCreateRequest? Consume()
    {
        var draft = Draft;
        Draft = null;
        return draft;
    }
}
