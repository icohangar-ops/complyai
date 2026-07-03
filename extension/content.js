/**
 * ComplyAI Content Script
 *
 * Extracts visible text from the page for compliance analysis.
 * Runs in the context of the page and listens for scan requests
 * from the popup.
 */

(function () {
  // Listen for scan requests from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scan") {
      const text = extractVisibleText();
      sendResponse({ text });
    }
    return true; // Keep channel open for async response
  });

  /**
   * Extract visible text from the page.
   * Ignores scripts, styles, hidden elements, and meta tags.
   */
  function extractVisibleText() {
    // Get all visible text nodes
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      {
        acceptNode: (node) => {
          const el = node.parentElement;
          if (!el) return NodeFilter.FILTER_REJECT;

          const style = window.getComputedStyle(el);
          const isHidden =
            style.display === "none" ||
            style.visibility === "hidden" ||
            style.opacity === "0" ||
            el.offsetWidth === 0 ||
            el.offsetHeight === 0;

          if (isHidden) return NodeFilter.FILTER_REJECT;

          // Skip script, style, noscript, meta, link tags
          const tag = el.tagName.toLowerCase();
          if (["script", "style", "noscript", "meta", "link", "svg"].includes(tag)) {
            return NodeFilter.FILTER_REJECT;
          }

          return NodeFilter.FILTER_ACCEPT;
        },
      }
    );

    const textParts = [];
    let node;
    while ((node = walker.nextNode())) {
      const text = node.textContent.trim();
      if (text.length > 0) {
        textParts.push(text);
      }
    }

    return textParts.join("\n");
  }
})();
