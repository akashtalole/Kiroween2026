/* Boo, the guide ghost: one line of mischief, then exactly one next step. Dismissible, keyboard friendly, reduced-motion safe. */
(function () {
  "use strict";
  var page = document.body.getAttribute("data-page") || "";
  var TIPS = {
    home: ["Boo! Didn't mean to scare you. Start here, it takes 30 minutes.", "Start Lab 01", "lab.html?id=01-setup-smoke-test"],
    ideas: ["So many ideas and only one of you. Filter to 'Chosen' to see what we're building.", "Show the chosen ideas", "ideas.html?status=Chosen"],
    labs: ["Do them in order. Skipping Lab 01 is how ghosts are made.", "Open Lab 01", "lab.html?id=01-setup-smoke-test"],
    doc: ["Long read? The table of contents on the right is your lantern. Or take the short way:", "See the 2-minute overview", "index.html#categories"]
  };
  var t = TIPS[page]; if (!t) return;
  try { if (sessionStorage.getItem("ns-boo-" + page) === "gone") return; } catch (e) {}
  var css = ".boo{position:fixed;right:16px;bottom:16px;z-index:60;max-width:320px;background:var(--bg-elev);border:1px solid var(--violet);border-radius:16px;padding:12px 14px 12px 58px;box-shadow:var(--shadow);font-size:14px;animation:boo-in .5s ease-out}" +
    ".boo .g{position:absolute;left:12px;top:12px;font-size:32px;line-height:1;animation:boo-float 3s ease-in-out infinite}" +
    ".boo p{margin:0 0 8px;color:var(--fg)}.boo .row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}" +
    ".boo a.go{background:var(--accent);color:var(--accent-fg);border-radius:8px;padding:5px 10px;font-weight:700}.boo a.go:hover{text-decoration:none}" +
    ".boo button{background:none;border:0;color:var(--fg-muted);cursor:pointer;font:inherit;padding:5px 6px}" +
    "@keyframes boo-in{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}@keyframes boo-float{50%{transform:translateY(-4px)}}" +
    "@media (max-width:480px){.boo{left:12px;right:12px;max-width:none}body.has-boo{padding-bottom:150px}}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var el = document.createElement("aside");
  el.className = "boo"; el.setAttribute("role", "complementary"); el.setAttribute("aria-label", "Guide ghost");
  el.innerHTML = '<span class="g" aria-hidden="true">👻</span><p>' + t[0] + '</p><div class="row"><a class="go" href="' + t[2] + '">' + t[1] + ' →</a><button type="button">Shoo</button></div>';
  document.body.appendChild(el); document.body.classList.add("has-boo");
  el.querySelector("button").addEventListener("click", function () {
    el.remove(); document.body.classList.remove("has-boo"); try { sessionStorage.setItem("ns-boo-" + page, "gone"); } catch (e) {}
  });
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && el.isConnected) el.querySelector("button").click(); });
})();
