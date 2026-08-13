namespace NycAging.Web.Services;

public sealed record PrintQueueItem(
    Guid Id,
    string ContentType,
    string Title,
    string Url,
    string? Detail,
    DateTime AddedAt);

public sealed class PrintQueueService
{
    private readonly List<PrintQueueItem> _items = [];

    public event Action? Changed;

    public IReadOnlyList<PrintQueueItem> Items => _items;

    public bool Add(string contentType, string title, string url, string? detail = null)
    {
        if (_items.Any(item => item.ContentType.Equals(contentType, StringComparison.OrdinalIgnoreCase)
            && item.Url.Equals(url, StringComparison.OrdinalIgnoreCase)))
        {
            return false;
        }

        _items.Add(new PrintQueueItem(Guid.NewGuid(), contentType, title, url, detail, DateTime.Now));
        Changed?.Invoke();
        return true;
    }

    public void Remove(Guid id)
    {
        _items.RemoveAll(item => item.Id == id);
        Changed?.Invoke();
    }

    public void Clear()
    {
        _items.Clear();
        Changed?.Invoke();
    }
}
