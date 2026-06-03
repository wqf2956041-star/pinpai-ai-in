"""
最终方案：首页 HTML 永不更新。
心跳只做两件事：
1. 加品牌页面到 /var/www/pinpai/<slug>/
2. 更新 /var/www/pinpai/brands_index.json
首页通过 JS 读取 brands_index.json 动态渲染品牌列表。
"""
import json, os, re, shutil

WWW = "/var/www/pinpai"

# Step 1: 用原始模板重建首页（包含完整JS + 动画）
# 这个模板需要包含：renderBrands, buildShuffledList, fetchBrands, searchBrand, 动画
# 从当前首页提取框架，但确保所有JS都在
h = open(os.path.join(WWW, "index.html"), encoding="utf-8", errors="replace").read()
idx = json.load(open(os.path.join(WWW, "brands_index.json")))
data_json = json.dumps(idx, ensure_ascii=False)

# 用最原始的方式重建——只保留html框架和script部分
# html框架从原首页取（head, style, body结构）
m = re.search(r'(.*?)<script>', h, re.DOTALL)
if not m:
    print("Cannot find script start")
    exit(1)
html_pre = m.group(1)

m2 = re.search(r'</script>(.*)', h, re.DOTALL)
if not m2:
    print("Cannot find script end")
    exit(1)
html_post = m2.group(1)

# 核心JS代码（永不修改）
core_js = r"""
var brandsData = %s;

var DISPLAY_COUNT = 20;
var currentCount = 20;
var currentLang = 'zh-CN';
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

function renderBrands(lang) {
    var list = document.getElementById('brand-list');
    if (!list || brandsData.length === 0) return;
    if (shuffledIndices.length === 0) buildShuffledList();
    var h = '';
    var count = Math.min(currentCount, shuffledIndices.length);
    for (var i = 0; i < count; i++) {
        var ix = shuffledIndices[i];
        var b = brandsData[ix];
        if (!b) continue;
        h += '<a class="brand-card" href="/' + b.slug + '/">';
        h += '<h2>' + (b.name || '') + '</h2>';
        h += '<div class="en">' + (b.name_en || b.name || '') + '</div>';
        if (b.category) h += '<span class="cat-tag">' + b.category + '</span>';
        h += '</a>';
    }
    if (count < shuffledIndices.length) {
        h += '<div style="text-align:center;padding:20px"><button onclick="loadMore()" style="padding:8px 30px;background:#222;color:#fff;border:none;border-radius:6px;cursor:pointer">More Brands</button></div>';
    }
    list.innerHTML = h;
}

function loadMore() {
    currentCount += DISPLAY_COUNT;
    if (currentCount > shuffledIndices.length) currentCount = shuffledIndices.length;
    renderBrands(currentLang);
}

function fetchBrands() {
    var x = new XMLHttpRequest();
    x.open('GET', '/brands_index.json', true);
    x.onload = function() {
        try {
            var fr = JSON.parse(x.responseText);
            if (fr && fr.length > 0) {
                brandsData = fr;
                if (shuffledIndices.length === 0) buildShuffledList();
                renderBrands(currentLang);
            }
        } catch(e) {}
    };
    x.send();
}

function searchBrand() {
    var inp = document.getElementById('search-input');
    if (!inp) return;
    var q = inp.value.toLowerCase().trim();
    var list = document.getElementById('brand-list');
    if (!list) return;
    if (!q) {
        currentCount = DISPLAY_COUNT;
        buildShuffledList();
        renderBrands(currentLang);
        return;
    }
    var h = '';
    for (var i = 0; i < brandsData.length; i++) {
        var b = brandsData[i];
        var n = (b.name || '').toLowerCase();
        var ne = (b.name_en || '').toLowerCase();
        if (n.indexOf(q) >= 0 || ne.indexOf(q) >= 0) {
            h += '<a class="brand-card" href="/' + b.slug + '/"><h2>' + (b.name || '') + '</h2><div class="en">' + (b.name_en || b.name || '') + '</div></a>';
        }
    }
    list.innerHTML = h || '<div style="padding:30px;color:#999">No matching brands</div>';
}

document.addEventListener('DOMContentLoaded', function() {
    if (brandsData.length > 0) {
        buildShuffledList();
        renderBrands(currentLang);
    }
    fetchBrands();
});

// ===== Status Animation =====
(function() {
    var spinners = ['⠸', '⠹', '⠺', '⠻', '⠼', '⠽', '⠾', '⠿'];
    var spinners2 = ['\\', '|', '/', '—'];
    var spinners3 = ['◒', '◐', '◑', '◓'];
    var dots = ['', '.', '..', '...'];
    var idx1 = 0, idx2 = 0, idx3 = 0, dotIdx = 0;
    var progStep = 1;
    var progressChars = 25;

    function updateAnimation() {
        idx1 = (idx1 + 1) % spinners.length;
        idx2 = (idx2 + 1) % spinners2.length;
        idx3 = (idx3 + 1) % spinners3.length;
        dotIdx = (dotIdx + 1) % dots.length;

        var e1 = document.getElementById('spinner1');
        var e2 = document.getElementById('spinner2');
        var e3 = document.getElementById('spinner3');
        var p3 = document.getElementById('progress3');
        var d1 = document.getElementById('dot1');
        var d2 = document.getElementById('dot2');
        if (e1) e1.textContent = spinners[idx1];
        if (e2) e2.textContent = spinners2[idx2];
        if (e3) e3.textContent = spinners3[idx3];
        if (d1) d1.textContent = dots[dotIdx];
        if (d2) d2.textContent = dots[dotIdx];

        if (p3) {
            var percent = progStep;
            if (percent > 100) { progStep = 1; percent = 1; }
            var filled = Math.min(Math.round(percent / 100 * progressChars), progressChars);
            var bar = '';
            for (var b = 0; b < filled; b++) bar += '=';
            bar += '>';
            p3.textContent = percent + '%' + bar;
            progStep++;
        }
    }

    setInterval(updateAnimation, 800);
    setTimeout(updateAnimation, 100);
})();
""" % data_json

# 确保brand-list是空的（JS会动态填充）
brand_list_pattern = r'<div class="brand-grid" id="brand-list">.*?</div>'
html_post = re.sub(brand_list_pattern, '<div class="brand-grid" id="brand-list"></div>', html_post, count=1, flags=re.DOTALL)

# 把加载更多按钮的文字改为品牌计数
count_pattern = r'共 \d+ 个品牌'
html_post = re.sub(count_pattern, '共 %d 个品牌' % len(idx), html_post)

new_html = html_pre + '<script>' + core_js + '</script>' + html_post

# 写回
with open(os.path.join(WWW, "index.html"), "w", encoding="utf-8") as f:
    f.write(new_html)

print("Homepage rebuilt with %d brands" % len(idx))

# 验证
v = open(os.path.join(WWW, "index.html"), encoding="utf-8").read()
print("renderBrands: %s" % ('function renderBrands' in v))
print("buildShuffledList: %s" % ('function buildShuffledList' in v))
print("fetchBrands: %s" % ('function fetchBrands' in v))
print("Animation: %s" % ('setInterval' in v and 'spinner' in v))
print("brandsData: %s" % ('var brandsData = [' in v))
print("brand-list empty: %s" % ('id="brand-list"></div>' in v))
