# 外部视觉 Demo 批次审计（2026-07-27）

本批共 5 项。逐项执行源码、固定版本、许可证、依赖、输入与移动端风险审计后，
完成并发布 4 项，跳过 1 项。已发布项目均保留 `?baseline=1` 原版机制基线，
再设计互不相同的触屏闭环；本批没有倒计时玩法。

## 已完成并上线

| 参考 | 视觉机制与固定源码 | 许可证与署名 | 依赖 | 原输入 → 触屏闭环 | 移动端风险与验证 | 上线与技能 |
|---|---|---|---|---|---|---|
| [CSS Splatters](https://codepen.io/meodai/full/WNPKNzv) | DOM/CSS 位移、弹丸、反冲、径向爆裂和残留飞溅；Pen `WNPKNzv`，2026-07-27 获取 | CodePen 公共 Pen MIT；David Aerne / meodai | 原生 DOM、CSS、Pointer Events | 鼠标按住喷射 → 按住瞄准，用反冲移动并依次触达四条边，留下完整画面 | DOM 节点上限、指针取消、窄屏标题安全区；390×844 与 320×568 通过 | [Recoil Bloom](https://yinxinghuan.github.io/recoil-bloom/)；正式 Skill `recoil-splatter-field` |
| [Stick Hero with Canvas](https://codepen.io/HunorMarton/full/xxOMQKg) | Canvas 平台生成、按压长杆、旋转、行走和相机平移；Pen `xxOMQKg`，2026-07-27 获取 | CodePen 公共 Pen MIT；Hunor Marton Borbely | Canvas 2D、Pointer Events | 鼠标按压长度 → 触屏按住架桥，连续通过 5 座平台完成天际线 | DPR、短屏平台间距、Pointer Capture、失败恢复；两尺寸通过，修复键盘路径负 pointer id | [Skyline Span](https://yinxinghuan.github.io/skyline-span/)；机制与现有 Canvas 跑酷类别重叠，暂不拆新 Skill |
| [Physics Menu](https://tympanus.net/Tutorials/PhysicsMenu/) | 三组铰接刚体文字/水果、Cannon 约束、指针物理扰动；commit `7ac40107cffefade7ef3a5443ebf5746f33a95d0` | Codrops 集成条款；Arno Di Nunzio / Codrops，禁止原样或插件化再分发 | Three.js 0.109、Cannon.js 0.6.2、Helvetiker | 鼠标拨动物理菜单 → 当前玩家用户名组成三排，逐排拨动并在低能量状态锁定 | WebGL、物理稳定性、长用户名、短屏相机；两尺寸通过，修复 320 高度构图 | [Kinetic Balance](https://yinxinghuan.github.io/kinetic-balance/)；许可禁止插件化，明确不抽成可再分发 Skill |
| [Little Big City](https://pissang.github.io/little-big-city/) | 矢量瓦片挤出、城市球面、道路/水域/建筑生成；commit `4baa8eaeab15effc0d35ce5970edb29894e0fa79` | MIT；pissang；保留 OpenStreetMap、Nextzen 与依赖许可 | ClayGL、maptalks、矢量瓦片、Webpack 4 engine + Vite shell | 地图拖动后自动刷新 → 触屏平移地图，在 3 个相距至少 0.008° 的坐标显式生长城市并装订图册 | 1.11 MiB engine、网络瓦片、WebGL、地图手势冲突；两尺寸通过，修复生成竞态与 `touch-action` | [City Atlas](https://yinxinghuan.github.io/city-atlas/)；依赖和机制体量大，暂不抽 Skill |

## 跳过

| 参考 | 视觉机制 | 源码 / 许可证结论 | 依赖与输入 | 移动端风险 | 结论 |
|---|---|---|---|---|---|
| [Pencil Sketch](https://codepen.io/bradarnett/full/XyZKaG) | Three.js 铅笔素描式 3D 模型渲染 | Pen 代码可按 MIT 使用，但决定画面主体的作者 S3 OBJ/MTL 没有独立素材许可证或再分发授权 | Three.js、外部 OBJ/MTL | 跨域素材、模型体量、移动端 GPU 成本均无法在许可门禁后可靠验证 | 跳过；不下载分发未授权模型，不用近似模型冒充基线，不技能化 |

## 玩法闭环

- Recoil Bloom：空间覆盖闭环；四条边均被飞溅命中后结束，可重置为新色相。
- Skyline Span：连续技巧闭环；完成 5 次桥接后抵达终点，失误立即进入恢复态。
- Kinetic Balance：物理安定闭环；玩家逐排扰动自己的名字，稳定后永久锁定。
- City Atlas：探索收集闭环；拖到 3 个不同坐标并生成城市，最终合成一册图册。

## 发布与 QA 门禁

- 4 项均为 Vite 工程，`base: './'`，`npm run build` 生成 `dist/`。
- 4 项的 `dist/THIRD_PARTY_NOTICES.txt` 均存在且非空；README 与游戏目录描述有可见原作署名。
- 4 项均已生成永久 UUID、Aigram transit 正式海报、公开源码仓库和 GitHub Pages 地址。
- 真实触屏 QA 覆盖 390×844 和 320×568、产品态与 `?baseline=1`；关键闭环在 390×844 全流程完成。
- P1 修复后已同状态复验：Recoil Bloom 标题安全区、Skyline Span 键盘输入、Kinetic Balance 短屏相机、City Atlas 生成竞态与地图手势。

## 可复用视觉能力

`recoil-splatter-field` 已在 Recoil Bloom 中完成源码级复原、真实玩法接入和双尺寸验证，
并通过 `skill-creator/quick_validate.py`。Skill 仅封装反冲、弹丸、边界爆裂和残留粒子，
同时记录最小接口、三档性能参数、降级路径、MIT 署名边界和禁止误用；不包含游戏标题、
HUD、四边目标或胜负逻辑。
