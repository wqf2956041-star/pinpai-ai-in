import json, os, re

WWW = "/var/www/pinpai"
h = open(os.path.join(WWW, "index.html"), encoding="utf-8", errors="replace").read()
idx = json.load(open(os.path.join(WWW, "brands_index.json")))
data_json = json.dumps(idx, ensure_ascii=False)

m = re.search(r'(.*?)<script>', h, re.DOTALL)
html_pre = m.group(1) if m else ""
m2 = re.search(r'</script>(.*)', h, re.DOTALL)
html_post = m2.group(1) if m2 else ""

# JS with data_json inserted properly (not using %)
core_js = '''
var brandsData = DATA_JSON_PLACEHOLDER;

var DISPLAY_COUNT = 20;
var currentCount = 20;
var currentLang = "zh-CN";
var shuffledIndices = [];

function buildShuffledList() {
    var total = brandsData.length;
    if (total === 0) return;
    shuffledIndices = [];
    for (var i = 0; i < total; i++) shuffledIndices.push(i);
    for (var i = shuffledIndices.length - 1; i > 0; i--) {
        var j = Math.floor(Math.random() * (i + 1));
        var tmp = shuffledIndices[i];
        shuffledIndices[i] = shuffledIndices[j];
        shuffledIndices[j] = tmp;
    }
}

function renderBrands() {
    var list = document.getElementById("brand-list");
    if (!list || brandsData.length === 0) return;
    if (shuffledIndices.length === 0) buildShuffledList();
    var h = "";
    var count = Math.min(currentCount, shuffledIndices.length);
    for (var i = 0; i < count; i++) {
        var ix = shuffledIndices[i];
        var b = brandsData[ix];
        if (!b) continue;
        h += "<a class=\"brand-card\" href=\"/" + b.slug + "/\">";
        h += "<h2>" + (b.name || "") + "</h2>";
        h += "<div class=\"en\">" + (b.name_en || b.name || "") + "</div>";
        if (b.category) h += "<span class=\"cat-tag\">" + b.category + "</span>";
        h += "</a>";
    }
    if (count < shuffledIndices.length) {
        h += "<div style=\"text-align:center;padding:20px\"><button onclick=\"loadMore()\" style=\"padding:8px 30px;background:#222;color:#fff;border:none;border-radius:6px;cursor:pointer\">More Brands</button></div>";
    }
    list.innerHTML = h;
}

function loadMore() {
    currentCount += DISPLAY_COUNT;
    if (currentCount > shuffledIndices.length) currentCount = shuffledIndices.length;
    renderBrands();
}

function fetchBrands() {
    var x = new XMLHttpRequest();
    x.open("GET", "/brands_index.json", true);
    x.onload = function() {
        try {
            var fr = JSON.parse(x.responseText);
            if (fr && fr.length > 0) {
                brandsData = fr;
                buildShuffledList();
                renderBrands();
            }
        } catch(e) {}
    };
    x.send();
}

function searchBrand() {
    var inp = document.getElementById("search-input");
    if (!inp) return;
    var q = inp.value.toLowerCase().trim();
    var list = document.getElementById("brand-list");
    if (!list) return;
    if (!q) {
        currentCount = DISPLAY_COUNT;
        buildShuffledList();
        renderBrands();
        return;
    }
    var h = "";
    for (var i = 0; i < brandsData.length; i++) {
        var b = brandsData[i];
        var n = (b.name || "").toLowerCase();
        var ne = (b.name_en || "").toLowerCase();
        if (n.indexOf(q) >= 0 || ne.indexOf(q) >= 0) {
            h += "<a class=\"brand-card\" href=\"/" + b.slug + "/\"><h2>" + (b.name || "") + "</h2><div class=\"en\">" + (b.name_en || b.name || "") + "</div></a>";
        }
    }
    list.innerHTML = h || "<div style=\"padding:30px;color:#999\">No matching brands</div>";
}

document.addEventListener("DOMContentLoaded", function() {
    if (brandsData.length > 0) {
        buildShuffledList();
        renderBrands();
    }
    fetchBrands();
});

// ===== Status Animation =====
(function() {
    var spinners = ["⠸", "⠹", "⠺", "⠻", "⠼", "⠽", "⠾", "⠿"];
    var spinners2 = ["\\\\", "|", "/", "---"];
    var spinners3 = ["◒", "◐", "◑", "◓"];
    var dots = ["", ".", "..", "..."];
    var idx1 = 0, idx2 = 0, idx3 = 0, dotIdx = 0;
    var progStep = 1;

    function updateAnimation() {
        idx1 = (idx1 + 1) % spinners.length;
        idx2 = (idx2 + 1) % spinners2.length;
        idx3 = (idx3 + 1) % spinners3.length;
        dotIdx = (dotIdx + 1) % dots.length;

        var e1 = document.getElementById("spinner1");
        var e2 = document.getElementById("spinner2");
        var e3 = document.getElementById("spinner3");
        var d1 = document.getElementById("dot1");
        var d2 = document.getElementById("dot2");
        if (e1) e1.textContent = spinners[idx1];
        if (e2) e2.textContent = spinners2[idx2];
        if (e3) e3.textContent = spinners3[idx3];
        if (d1) d1.textContent = dots[dotIdx];
        if (d2) d2.textContent = dots[dotIdx];

        var p3 = document.getElementById("progress3");
        if (p3) {
            var percent = progStep;
            if (percent > 100) { progStep = 1; percent = 1; }
            var filled = Math.min(Math.round(percent / 100 * 25), 25);
            var bar = "";
            for (var b = 0; b < filled; b++) bar += "=";
            bar += ">";
            p3.textContent = percent + "%" + bar;
            progStep++;
        }
    }

    setInterval(updateAnimation, 800);
    setTimeout(updateAnimation, 100);
})();
'''.replace("DATA_JSON_PLACEHOLDER", data_json)

# 确保brand-list是空的（JS会动态填充）
html_post = re.sub(r'<div class="brand-grid" id="brand-list">.*?</div>',
                   '<div class="brand-grid" id="brand-list"></div>',
                   html_post, count=1, flags=re.DOTALL)

# 去掉任何额外的brand-card（只保留JS动态渲染的）
html_post = re.sub(r'<a class="brand-card".*?</a>\s*', '', html_post)

# 更新计数
html_post = re.sub(r'共 \d+ 个品牌', '共 %d 个品牌' % len(idx), html_post)

new_html = html_pre + '<script>' + core_js + '</script>' + html_post

with open(os.path.join(WWW, "index.html"), "w", encoding="utf-8") as f:
    f.write(new_html)

print("Done! %d brands" % len(idx))
v = open(os.path.join(WWW, "index.html"), encoding="utf-8").read()
for check in ['function renderBrands','function buildShuffledList','function fetchBrands','setInterval']:
    print("%s: %s" % (check, check in v))
print("brand-list empty: %s" % ('id="brand-list"></div>' in v))
