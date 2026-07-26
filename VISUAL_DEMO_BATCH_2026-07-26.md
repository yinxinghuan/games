# 外部视觉 Demo 批次审计（2026-07-26）

本批共 11 项。许可门禁后完成并发布 5 项，跳过 6 项。所有已发布项目均先保留
`?baseline=1` 视觉基线，再加入不同的触屏闭环；没有使用统一倒计时。

## 已完成并上线

| 参考 | 视觉机制与固定源码 | 许可证与署名 | 依赖 | 原输入 → 触屏闭环 | 移动端风险与验证 | 上线与技能 |
|---|---|---|---|---|---|---|
| [Kinetic Typography](https://tympanus.net/Tutorials/codrops-kinetic-typo/) | 文本纹理映射到四套程序几何与 shader；`f381fb2b4aec7b6f9cc35b252bf8f911a51bf09c` | MIT；Mario Carrillo / Codrops | Three.js、BMFont/Canvas 文字回退 | 自动展示 → 当前用户名；依次轻触锁定 4 种形态，完成后自由观察 | 字形覆盖、长名、CJK、纹理分辨率；390×844 与 320×568 通过 | [Kinetic Name](https://yinxinghuan.github.io/kinetic-name/)；`kinetic-texture-carousel` |
| [Blurry](https://tympanus.net/Tutorials/Blurry/) | 浮点时间累积、相机抖动采样、五边形景深散景与粒子蛛网；`10652e8495b498dedd83b88ac8e93253de7603e2` | MIT；Domenico Bruzzese | Three.js、浮点/半浮点 render target | 指针相机 → 轻触锁定近/中/远 3 个焦面 | 浮点支持、累积失效、采样数与 DPR；两尺寸通过 | [Bokeh Web](https://yinxinghuan.github.io/bokeh-web/)；`accumulated-bokeh-field` |
| [Interactive Landscape](https://tympanus.net/Development/InteractiveLandscape/index.html) | 连续程序地形带、噪声山谷、雾、天空与调色；`8d840044b3e14ffb65b39f56527b86b320b7e392` | Codrops 集成条款；André Mattos / Codrops | Three.js r98、程序几何/噪声 | 鼠标地形变形 → 拖动控制山谷中心/宽度，穿过 3 枚路线信标 | 窄屏相机构图、顶点密度、对比度；修复 P1 后两尺寸复验通过 | [Horizon Drift](https://yinxinghuan.github.io/horizon-drift/)；`procedural-horizon-ribbon` |
| [Procedural Clouds](https://tympanus.net/Tutorials/ProceduralClouds/) | Sprite 云层、双纹理 mask、FBM/simplex 位移、环境雾；`029dce52c5027d2f29753ce8ae5083b8a593374a` | Codrops 集成条款；Robert Borghesi / Codrops；噪声保留 Ashima/Gustavson notice | Three.js 0.112、glslify、glsl-noise | 视角游览 → 按住绕行并凝结 3 层水汽 | 原 Babel/Webpack 与现代 Node 不兼容；原机制迁入 Vite，控制 Sprite 数/DPR；两尺寸通过 | [Cloud Loom](https://yinxinghuan.github.io/cloud-loom/)；`procedural-cloud-sprite` |
| [Interactive Particles](https://tympanus.net/Tutorials/InteractiveParticles/) | 图像暗像素剔除、实例化四边形粒子、shader 位移、64×64 触摸纹理与 raycast；`efe300f9cd2b976da377ed43e9f50662fb575bf7` | Codrops 集成条款；Bruno Imbrizi / Codrops；噪声保留 Ashima/Gustavson notice | Three.js r98、glslify、glsl-noise | 示例肖像/鼠标 → 当前玩家头像；触摸覆盖 12 格中的 9 格让肖像收束 | 头像 CORS/方向/裁切、shader alias、粒子量；默认、查询头像、无头像回退、基线及两尺寸通过 | [Portrait Current](https://yinxinghuan.github.io/portrait-current/)；`interactive-image-particle-field` |

## 跳过

| 参考 | 视觉机制 | 源码 / 许可证结论 | 依赖与输入 | 移动端风险 | 结论 |
|---|---|---|---|---|---|
| [pizza3 / Rwoqemx](https://codepen.io/pizza3/full/Rwoqemx) | 未进入机制提取；许可门禁先行 | 未取得带明确再分发许可的固定源码 | 未锁定 | 无法做可复现性能审计 | 跳过，不近似重画、不技能化 |
| [soju22 / JjEqebK](https://codepen.io/soju22/full/JjEqebK) | 未进入机制提取；许可门禁先行 | 未取得带明确再分发许可的固定源码 | 未锁定 | 无法做可复现性能审计 | 跳过，不近似重画、不技能化 |
| [strangerintheq / bGeRqpz](https://codepen.io/strangerintheq/full/bGeRqpz) | 未进入机制提取；许可门禁先行 | 未取得带明确再分发许可的固定源码 | 未锁定 | 无法做可复现性能审计 | 跳过，不近似重画、不技能化 |
| [pizza3 / pobevYW](https://codepen.io/pizza3/full/pobevYW) | 未进入机制提取；许可门禁先行 | 未取得带明确再分发许可的固定源码 | 未锁定 | 无法做可复现性能审计 | 跳过，不近似重画、不技能化 |
| [ycw / xxVPMwB](https://codepen.io/ycw/full/xxVPMwB) | 未进入机制提取；许可门禁先行 | 未取得带明确再分发许可的固定源码 | 未锁定 | 无法做可复现性能审计 | 跳过，不近似重画、不技能化 |
| [Mirrors / panna](https://tympanus.net/Tutorials/Mirrors/#/panna) | 镜像式图像体验页面可访问，但未找到可固定复原的公开源码包 | 页面展示不等于源码再分发许可；没有可审计 revision | 运行依赖和输入合同无法锁定 | 无法建立可靠基线与性能分档 | 跳过，不用近似镜面 shader 冒充复刻 |

## 发布门禁结果

- 5 个项目均为 Vite 工程，`base: './'`，`npm run build` 生成 `dist/`。
- 5 个 `dist/THIRD_PARTY_NOTICES.txt` 均存在且非空；README 和游戏目录描述均有可见署名。
- 5 个项目均有永久 UUID、正式 Aigram transit 海报、GitHub 源码仓库与 Pages 线上地址。
- 图像驱动的 Portrait Current 默认读取当前玩家头像；文字驱动的 Kinetic Name
  默认读取当前玩家用户名，示例输入仅保留在 `?baseline=1`。
- 5 个正式技能均通过 `skill-creator` 的 `quick_validate.py`。

## 2026-07-27 启动连续性回归

针对“点击进入后出现空挡和视觉落差”，五个项目统一改为真实第一帧握手，但各自
保留不同的低成本睡眠画面：字形轮廓、失焦光圈、程序山形、柔化云核和头像点阵。
桥接层不依赖固定倒计时，只有对应 mesh、纹理和 WebGL 输出已经绘制才淡出。

`qa-visual-batch-startup.mjs` 在所有 JS、字体和纹理额外延迟 420ms 的条件下验证：

| 项目 | 启动桥可见 | 真实第一帧（390×844 / 320×568） |
|---|---:|---:|
| Kinetic Name | 54–115ms | 2306ms / 2141ms |
| Bokeh Web | 59–60ms | 1876ms / 1875ms；顺序为 `frame-ready → cover-release` |
| Horizon Drift | 54–55ms | 1211ms / 1200ms |
| Cloud Loom | 51–55ms | 1016ms / 983ms |
| Portrait Current | 52–54ms | 1487ms / 1481ms |

五项均无 page error 或 shader 编译错误；原双尺寸完整玩法 QA 同步复验通过。
