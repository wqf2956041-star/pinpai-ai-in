# pinpai.ai.in — 全球品牌索引

> **全球品牌实体索引系统**
> 私有仓库 | 仅 wqf2956041-star 账号可访问
> 最后更新：2026-05-25 (北京时间)

---

## 一、项目概况

| 项目 | 内容 |
|------|------|
| 域名 | pinpai.ai.in（印度.in后缀，续费约30元/年） |
| 定位 | 全球品牌索引 — 品牌实体收录与搜索流量索引系统 |
| 盈利模式 | Google AdSense 广告收入 |
| 不侵权 | 纯文字介绍，无图片，来源为维基百科摘要 |
| 流量逻辑 | 每个品牌自带搜索流量 → 底部「类似品牌」含埃舍尔Escher → 引向自有品牌 |
| 托管 | GitHub Pages（免费） |
| 域名归宿 | 老板个人持有，与 GitHub 账号无关 |

**远期规划：** 如果流量做大，换 .com 或 .cn 域名。品牌主键系统 + master-brands.csv 驱动，支持百万级品牌索引。

---

## 二、网站结构

```
pinpai-ai.in/
├── index.html              ← 首页（搜索 + 品牌网格）
├── search.html             ← 搜索页面
├── template.html           ← 品牌页面模板
├── generator.py            ← 品牌生成器
├── brands_index.json       ← 搜索索引
├── README.md               ← 本文件
└── {brand-slug}/           ← 每个品牌一个目录
    ├── index.html          ← 该品牌页面（10种语言内嵌JS切换）
    └── brand.json          ← 品牌数据
```

---

## 三、品牌收录状态

当前收录：69 个品牌
已标记为完成（done）的品牌列表见 brands_index.json

---

## 四、核心工作流

1. **master-brands.csv** — 品牌主库，唯一ID + 唯一slug，AI只处理已有品牌
2. **generator.py** — 品牌生成器，读取品牌数据 → AI生成内容 → 渲染页面 → 更新索引
3. **验证系统** — 生成后验证所有语言页面真实存在，不存在的不显示语言按钮
4. **GitHub Pages** — 自动部署

---

## 五、遵守的品牌主键规则

- 一个品牌 = 一个唯一 slug
- 所有语言绑定同一个 slug（/ja/nike/ 而不是 /ja/ナイキ/）
- AI 不能自己发明品牌，只能处理 master-brands.csv 中已有的
- 重复检查通过 generated.log 的 status 状态机（pending/done/error）

---

## 六、技术架构

### 数据层
- master-brands.csv — 品牌实体主库
- brand.json — 每个品牌的数据文件
- brands_index.json — 全站搜索索引

### 内容层
- AI 生成内容，每种语言独立重写（非翻译）
- 10种语言全静态页面

### 构建层
- template.html 模板渲染
- 验证系统：生成 → 验证 → 部署
- 自动 GitHub Pages 部署

---

## 七、SEO

- 每个品牌独立 URL
- 每个语言独立展示（JS内嵌切换，无独立URL）
- 底部类似品牌推荐（含埃舍尔Escher推广位）
- 纯文字内容，无侵权图片
