window.simpleServings = window.simpleServings || {};

window.simpleServings.copyText = async function copyText(text) {
  const value = text || "";

  if (navigator.clipboard && window.isSecureContext) {
    await navigator.clipboard.writeText(value);
    return true;
  }

  const textArea = document.createElement("textarea");
  textArea.value = value;
  textArea.setAttribute("readonly", "readonly");
  textArea.style.position = "fixed";
  textArea.style.left = "-9999px";
  textArea.style.top = "0";
  document.body.appendChild(textArea);
  textArea.focus();
  textArea.select();

  try {
    return document.execCommand("copy");
  } finally {
    document.body.removeChild(textArea);
  }
};

window.simpleServings.printUrl = function printUrl(url) {
  const targetUrl = new URL(url, window.location.origin).href;
  const printWindow = window.open(targetUrl, "_blank");

  if (!printWindow) {
    return false;
  }

  let attempts = 0;
  const tryPrint = function tryPrint() {
    if (printWindow.closed) {
      return;
    }

    attempts += 1;
    try {
      if (printWindow.document.readyState !== "complete" && attempts < 20) {
        window.setTimeout(tryPrint, 250);
        return;
      }

      // Give Blazor pages time to finish rendering data after the document loads.
      window.setTimeout(function openPrintDialog() {
        try {
          printWindow.focus();
          printWindow.print();
        } catch {
          // Browser PDF viewers can block scripted printing. The source file remains
          // open in its own tab so the user can use the viewer's Print control.
        }
      }, 900);
    } catch {
      // A built-in PDF viewer may not expose its document. Keep the file open so
      // the user can print it from the viewer instead of printing the queue page.
    }
  };

  window.setTimeout(tryPrint, 250);
  return true;
};

window.simpleServings.printUrls = function printUrls(urls) {
  let opened = 0;

  for (const url of urls || []) {
    if (window.simpleServings.printUrl(url)) {
      opened += 1;
    }
  }

  return opened;
};
