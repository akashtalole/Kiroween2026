/* Night Shift site: shared chrome, theme, data helpers, markdown rendering. No build step. */
(function () {
  "use strict";
  var REPO = "https://github.com/akashtalole/Kiroween2026";
  var root = document.documentElement;
  var DEADLINE = new Date("2026-12-04T22:00:00Z"); // Dec 4, 2:00 pm PST

  // ----- theme (dark default; remembered if storage works) -----
  try { var saved = localStorage.getItem("ns-theme"); if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved); } catch (e) {}
  function theme() { return root.getAttribute("data-theme") === "light" ? "light" : "dark"; }
  function toggleTheme() {
    var next = theme() === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try { localStorage.setItem("ns-theme", next); } catch (e) {}
    document.dispatchEvent(new CustomEvent("ns-theme", { detail: next }));
  }

  // ----- helpers -----
  var cache = {};
  function getJSON(url) {
    if (!cache[url]) cache[url] = fetch(url).then(function (r) { if (!r.ok) throw new Error(url + " " + r.status); return r.json(); });
    return cache[url];
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  function slug(s) { return String(s).toLowerCase().replace(/[^\w\s-]/g, "").trim().replace(/\s+/g, "-"); }
  function daysLeft() { return Math.max(0, Math.ceil((DEADLINE - new Date()) / 86400000)); }

  // ----- chrome -----
  var page = document.body.getAttribute("data-page") || "";
  var NAV = [["ideas.html", "Ideas", "ideas"], ["labs.html", "Build labs", "labs"], ["doc.html?doc=night-shift", "Design", "doc"], ["doc.html?doc=kiro-features", "Kiro features", "features"], [REPO, "GitHub", ""]];
  function navLinks(cls) { return NAV.map(function (n) { return '<a href="' + n[0] + '"' + (page === n[2] && n[2] ? ' aria-current="page"' : "") + (n[0].indexOf("http") === 0 ? ' rel="noopener"' : "") + ">" + n[1] + "</a>"; }).join(""); }
  var skip = document.createElement("a"); skip.className = "skip"; skip.href = "#main"; skip.textContent = "Skip to content"; document.body.prepend(skip);
  var header = document.createElement("header"); header.className = "site-header";
  header.innerHTML = '<div class="wrap"><a class="brand" href="index.html"><span class="brand-mark" aria-hidden="true">N</span>Night Shift</a><nav class="nav" aria-label="Primary">' + navLinks() + '</nav><span class="spacer"></span>' +
    '<span class="chip accent" title="Devpost deadline: Dec 4, 2026, 2:00 pm PT">⏳ ' + daysLeft() + ' days left</span>' +
    '<button class="icon-btn" id="theme" aria-label="Toggle light and dark theme">☾ / ☀</button><button class="icon-btn menu-btn" id="menu" aria-label="Menu" aria-expanded="false">☰</button></div>' +
    '<nav class="mobile-nav" id="mnav" aria-label="Mobile">' + navLinks() + "</nav>";
  document.body.prepend(header);
  document.getElementById("theme").addEventListener("click", toggleTheme);
  var mb = document.getElementById("menu"), mn = document.getElementById("mnav");
  mb.addEventListener("click", function () { var o = mn.classList.toggle("open"); mb.setAttribute("aria-expanded", o); });
  var f = document.createElement("footer");
  f.innerHTML = '<div class="wrap"><span>Built for Kiroween 2026 with Kiro. Not affiliated with Kiro or AWS.</span><span><a href="' + REPO + '" rel="noopener">Source on GitHub</a> · <a href="https://kiroween.devpost.com/" rel="noopener">Kiroween on Devpost</a></span></div>';
  document.body.appendChild(f);

  // ----- markdown rendering -----
  var DOCMAP = {};
  function loadDocMap() { return getJSON("data/docs.json").then(function (d) { d.docs.forEach(function (x) { DOCMAP[x.file.toLowerCase()] = x.id; }); }).catch(function () {}); }
  function renderMarkdown(el, md) {
    if (!window.marked) { el.innerHTML = "<pre>" + esc(md) + "</pre>"; return Promise.resolve(); }
    return loadDocMap().then(function () {
      el.innerHTML = window.marked.parse(md);
      Array.prototype.forEach.call(el.querySelectorAll("h1,h2,h3,h4"), function (h) { h.id = slug(h.textContent); });
      Array.prototype.forEach.call(el.querySelectorAll("a[href]"), function (a) {
        var h = a.getAttribute("href"), base = h.split("#")[0].split("/").pop().toLowerCase();
        if (DOCMAP[base]) a.setAttribute("href", "doc.html?doc=" + DOCMAP[base] + (h.indexOf("#") > -1 ? "#" + h.split("#")[1] : ""));
        else if (/^https?:/.test(h)) a.setAttribute("rel", "noopener");
      });
      Array.prototype.forEach.call(el.querySelectorAll("pre > code"), function (code) {
        var pre = code.parentElement, lang = (code.className.match(/language-(\w+)/) || [])[1];
        if (lang === "mermaid") { var d = document.createElement("div"); d.className = "mermaid"; d.textContent = code.textContent; pre.replaceWith(d); return; }
        var b = document.createElement("button"); b.className = "copy"; b.type = "button"; b.textContent = "Copy";
        b.addEventListener("click", function () { if (navigator.clipboard) navigator.clipboard.writeText(code.textContent).then(function () { b.textContent = "Copied"; setTimeout(function () { b.textContent = "Copy"; }, 1400); }); });
        pre.appendChild(b);
      });
      if (window.mermaid) {
        window.mermaid.initialize({ startOnLoad: false, theme: theme() === "dark" ? "dark" : "default", securityLevel: "strict" });
        window.mermaid.run({ nodes: el.querySelectorAll(".mermaid") }).catch(function () {});
      }
      if (location.hash) { var t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) t.scrollIntoView(); }
    });
  }
  function toc(el, target) {
    target.innerHTML = Array.prototype.map.call(el.querySelectorAll("h2,h3"), function (h) { return '<li class="' + h.tagName.toLowerCase() + '"><a href="#' + h.id + '">' + esc(h.textContent) + "</a></li>"; }).join("");
  }
  function chips(arr, cls) { return (arr || []).map(function (s) { return '<span class="chip ' + (cls || "") + '">' + esc(s) + "</span>"; }).join(""); }

  window.NS = { getJSON: getJSON, esc: esc, slug: slug, daysLeft: daysLeft, renderMarkdown: renderMarkdown, toc: toc, chips: chips, REPO: REPO };
})();
