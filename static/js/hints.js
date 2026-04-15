/**
 * VulnPy Hint Panel
 * Loads vuln_map.json and shows relevant vulnerabilities for the current page.
 * Toggle with the floating button or Ctrl+Shift+H.
 */
(function () {
  let vulnData = null;
  let panelOpen = false;

  function currentRoute() {
    return window.location.pathname;
  }

  function matchVulns(route) {
    if (!vulnData) return [];
    return vulnData.vulnerabilities.filter(function (v) {
      if (!v.route) {
        // Global vulns (config-level) — show on every page
        return true;
      }
      // Normalize route patterns: /post/<id> matches /post/3
      const pattern = v.route
        .replace(/<[^>]+>/g, "[^/]+")
        .replace(/\//g, "\\/");
      const re = new RegExp("^" + pattern + "\\/?$");
      return re.test(route);
    });
  }

  function severityClass(sev) {
    switch (sev.toLowerCase()) {
      case "critical": return "hint-critical";
      case "high":     return "hint-high";
      case "medium":   return "hint-medium";
      default:         return "hint-low";
    }
  }

  function buildPanel(vulns) {
    const panel = document.getElementById("hint-panel");
    if (!panel) return;

    const pageVulns = vulns.filter(v => v.route);
    const globalVulns = vulns.filter(v => !v.route);

    let html = '<div class="hint-panel-header">'
      + '<h3>Vulnerability Hints</h3>'
      + '<button onclick="document.getElementById(\'hint-panel\').classList.remove(\'open\')" class="hint-close">&times;</button>'
      + '</div>';

    if (pageVulns.length > 0) {
      html += '<div class="hint-group-label">This Page</div>';
      pageVulns.forEach(function (v) {
        html += buildCard(v);
      });
    }

    if (globalVulns.length > 0) {
      html += '<div class="hint-group-label">Application-Wide</div>';
      globalVulns.forEach(function (v) {
        html += buildCard(v);
      });
    }

    if (vulns.length === 0) {
      html += '<p class="hint-empty">No known vulnerabilities mapped to this route.</p>';
    }

    panel.innerHTML = html;
  }

  function buildCard(v) {
    return '<div class="hint-card">'
      + '<div class="hint-card-header">'
      + '<span class="hint-severity ' + severityClass(v.severity) + '">' + v.severity + '</span>'
      + '<span class="hint-id">' + v.id + '</span>'
      + '</div>'
      + '<h4>' + v.name + '</h4>'
      + '<div class="hint-tags">'
      + '<span class="hint-tag">' + v.owasp + '</span>'
      + '<span class="hint-tag">' + v.cwe + '</span>'
      + (v.route ? '<code class="hint-route">' + v.method + ' ' + v.route + '</code>' : '')
      + '</div>'
      + '<p class="hint-desc">' + v.description + '</p>'
      + '<details class="hint-details"><summary>Show Hint</summary>'
      + '<p class="hint-hint">' + v.hint + '</p>'
      + '</details>'
      + '<details class="hint-details"><summary>Fix</summary>'
      + '<p class="hint-fix">' + v.fix + '</p>'
      + (v.file ? '<code class="hint-file">' + v.file + '</code>' : '')
      + '</details>'
      + '</div>';
  }

  function togglePanel() {
    const panel = document.getElementById("hint-panel");
    if (!panel) return;
    panelOpen = !panelOpen;
    panel.classList.toggle("open", panelOpen);
  }

  // Keyboard shortcut: Ctrl+Shift+H
  document.addEventListener("keydown", function (e) {
    if (e.ctrlKey && e.shiftKey && e.key === "H") {
      e.preventDefault();
      togglePanel();
    }
  });

  // Load vuln_map.json and build panel
  fetch("/static/vuln_map.json")
    .then(function (r) { return r.json(); })
    .then(function (data) {
      vulnData = data;
      const vulns = matchVulns(currentRoute());
      buildPanel(vulns);

      // Update badge count
      const badge = document.getElementById("hint-badge");
      const pageVulns = vulns.filter(v => v.route);
      if (badge) badge.textContent = pageVulns.length;
    })
    .catch(function () {
      // Silently fail if vuln_map.json isn't available
    });

  // Expose toggle for the floating button
  window.toggleHintPanel = togglePanel;
})();
