# 补充 IP 场景提示词

## 最终版本与局部编辑 QA

初版记录保留在上文，当前交付文件已替换为局部编辑后的版本。

- 03 最终文件：`assets/xiamen-ai-lecture-illustrations/03-public-learning.png`。已再次目视检查：身份一致、红衬衫换装、双手展开并夹住长卷、两条简体标注清晰，构图和颜色保留。
- 04 最终文件：`assets/xiamen-ai-lecture-illustrations/04-feedback-improvement.png`。局部编辑移除了不必要的红色繁体标注，仅留风筝反馈纸条「有点晃」。人物正在调整系线，动作承载“收到反馈后改进”，角色与构图未改变。
- 最终 03 为 1671×941 PNG，04 为 1672×941 PNG（均约 16:9），目视白底。经图像生成局部编辑后空白仍含近白色的极轻微生成噪点，未用滤镜或程序改图；不可宣称所有背景像素均为 RGB 255。
- 原始生成文件全部保留；首版另外备份于 `assets/xiamen-ai-lecture-illustrations/originals/`。
- 原始最终图 03：`/Users/huangjiabao/.codex/generated_images/01a1ef48-32f2-7043-a6fb-98653f2674f0/exec-96416e13-85a7-42b0-b719-bdbfc568cc2d.png`
- 原始最终图 04：`/Users/huangjiabao/.codex/generated_images/01a1ef48-32f2-7043-a6fb-98653f2674f0/exec-df7d1f4e-fa2e-4806-bee8-2cb0aa25c75a.png`

每次局部编辑均传入目标图＋两张固定身份参考。

### 03 局部编辑提示词

```text
Bornforthis identity: retain EXACTLY the first image's cobalt-blue short spiky hair, outward round ears, paper-white rounded-square face, circular yellow cheeks, tiny yellow nose dot, small cobalt eyes/brows and single-line smile. The second and third images are identity references only, never copy their clothes, yellow backgrounds, accessories or pose. Do not redraw the character unless unavoidable. Edit the FIRST image minimally. Remove only the extremely faint paper/noise texture from the EMPTY BACKGROUND and make all negative space perfectly solid pure white #FFFFFF. Keep the scene exactly as drawn: open orange window, Bornforthis in red rolled-sleeve shirt, hands, scroll, pencil, colors, original crayon hatching INSIDE all colored shapes, line weight, the words 学习记录 and 公开分享, composition, scale, aspect ratio and quality. Keep everything else unchanged. Do not erase the paper scroll's internal hatching or any object's texture. Do not add elements or titles.
```

### 04 第一轮局部编辑提示词

```text
Bornforthis identity: retain EXACTLY the first image's cobalt-blue short spiky hair, outward round ears, paper-white rounded-square face, circular yellow cheeks, tiny yellow nose dot, small cobalt eyes/brows and single-line smile. The second and third images are identity references only, never copy their clothes, yellow backgrounds, accessories or pose. Do not redraw the character unless unavoidable. Edit the FIRST image minimally in exactly TWO ways: (1) Remove the extremely faint paper/noise texture from the EMPTY BACKGROUND and replace it with perfectly solid pure white #FFFFFF. Keep crayon hatching INSIDE colored objects and clothing. (2) Replace the red handwritten text 再調一調 with simplified Chinese 再调一调 in the same size, red color and position. Preserve EVERYTHING else: the kneeling character, his blue shirt/white apron/orange trousers, exact face, hands tying the bridle, kite, bench, feedback note 有点晃, line work, full scene composition, dimensions and quality. No new objects, no title.
```

### 04 最终局部编辑提示词

```text
MINIMAL LOCAL EDIT. The FIRST attached image is the exact image to edit. The second and third images are identity-only references required by our art system. KEEP the FIRST image's identity, drawing, clothing, pose, objects, exact layout, scale, ratio, quality and every colored crayon stroke unchanged. ERASE ONLY the red handwritten phrase above the character's hands (the phrase currently reads 再調一調), replacing those red letters with clean pure white background. Keep the small red/yellow emphasis strokes beside the hands if possible, and keep the dark-blue feedback note 有点晃 intact. Do not write any replacement words. There must be no red text anywhere when finished. Leave just the ONE Chinese label 有点晃 on the kite feedback note. Keep Bornforthis cobalt short spiky hair, round protruding ears, white rounded-square face, yellow circles on cheeks, small blue eyes and simple smile exactly as they are. The empty background must look clean solid pure white #FFFFFF, while all crayon hatching inside objects stays unchanged. Do not copy outfits or yellow backgrounds from the second and third identity references.
```


使用技能：bornforthis-illustrations。生成时每张同时传入 bornforthis-ref-1.png 和 bornforthis-ref-2.png 作为身份参考。原稿与已有 01/02 图均不修改。

## 初版生成与目视 QA

- 两张独立生成，均为 1672×941 PNG（约 16:9）；已复制到 `assets/xiamen-ai-lecture-illustrations/`，原始生成文件保留。
- 03：钴蓝短刺发、外扩圆耳、纸白圆方脸、黄色圆脸颊均保留；改穿珊瑚红卷袖衬衫，主体亲手展开并夹住学习长卷；中文“学习记录”“公开分享”可读。白底、纹理填充、深蓝手绘线条、右侧留白；无 UI、无角色克隆。
- 04：同一身份，改穿蓝色短袖工作衫＋白围裙＋橙色直筒裤；主体跪着调节风筝系线；“有点晃”和“再調一調”可读（后一标签生成采用繁体“調”，含义正确）。无旧纸船/钥匙隐喻、无默认耳机夹克；动作与反馈关系清晰。
- 背景目视为白色，生成器仍带极轻微的纸感，这是输出自身的细节；未做后期擦除或滤镜。整体不是纯色矢量，主体颜色均有明显蜡笔斜线。
- 本次对照 `references/qa-checklist.md` 检查了画幅、背景观感、身份、换装、单一动作、短标注、留白和场景语义。

原始文件：

- 03：`/Users/huangjiabao/.codex/generated_images/01a1ef48-32f2-7043-a6fb-98653f2674f0/exec-5a7f3637-d008-4d5c-b338-b7be9dfdd0f9.png`
- 04：`/Users/huangjiabao/.codex/generated_images/01a1ef48-32f2-7043-a6fb-98653f2674f0/exec-c7244877-3660-4d09-bfce-4340c9e1dcf6.png`

## 03 · 公开学习

用于第 32 页 Learn in Public：将自己写下的学习记录从打开的窗户展示出去。

```text
IP Character Bornforthis (HIGHEST PRIORITY — preserve exactly the same identity in BOTH provided identity references): A youthful ADULT male, not a child, compact roughly 3.5–4-head-tall picture-book body; a large rounded-square PAPER-WHITE face, broad forehead, rounded cheeks and only slightly tapering lower face; thick saturated COBALT BLUE (#1262D5) short spiky hair with darker cobalt hatching, irregular upward tufts, very short faded sides and jagged natural forehead hairline; conspicuous outward-projecting semicircular ears, both visible, each one simple C inner line; short cobalt eyebrows, tiny cobalt dot/oval eyes with a simple curved upper-eyelid stroke; a tiny yellow nose dot and TWO flat perfectly round golden-yellow cheek circles; a short cobalt single-line closed-mouth smile, attentive and gently confident. No beard, no glasses, no huge anime eyes, no realistic skin, no pointed chin. This fixed FACE AND HAIR identity must survive every pose and outfit change.
The TWO attached images are identity references only, NOT composition or clothing references. DO NOT copy yellow backgrounds, white sticker borders, headphones, blue/yellow jacket, white T-shirt, beige baggy pants, huge sneakers, camera, bag, book, thumbs-up gesture or surrounding symbols. No fixed outfit.

Create ONE standalone 16:9 landscape Chinese article illustration with a pure clean WHITE background, no background texture. Deep navy slightly wobbly HAND-DRAWN outlines and visible natural diagonal CRAYON/MARKER HATCHING in EVERY colored region. Warm storybook drawing, slightly absurd but coherent, not slick vector, not 3D, not commercial stock art, not a presentation infographic. Mostly white negative space; scene occupies 40–60% of canvas, at least 35% quiet blank white space. At most 4–5 colors: cobalt blue, navy, golden yellow, coral red, soft orange plus paper white. No gradient, no cast shadow, no whole-background yellow or beige, no UI, no charts, no boxes-and-arrows layout, no top-left heading. Only the tiny specified Chinese handwritten labels, no long text.
Theme: Learn in Public / share your learning so others can see and learn from it. One simple metaphor: opening a window and unrolling private study notes into public view.
Composition: Place one modest freestanding wooden WINDOW in the middle-left of the landscape with both shutters already pushed outward; only the window frame and a small hint of sill, no large wall, no building facade. Bornforthis is leaning through the open window, three-quarter frontal face readable and both characteristic ears visible. His hands are actively securing and unrolling a long SHEET OF HIS HANDWRITTEN LEARNING NOTES across the outside of the windowsill towards the middle-right, like a modest street-side hanging scroll. One hand holds a small blue clip at the upper edge and the other pulls the loose paper roll open. The large paper unfurls with just a few navy handwritten squiggles and TWO SMALL, clear examples of hand-drawn learning: one tiny plant sketch and one simple hand-drawn cube. This is ordinary personal learning, NOT a software screen or flowchart. The outward unrolling action is the whole story. The scroll end gently curls at the lower right. A single blue pencil rests on the inner sill to indicate he wrote it himself. Leave the entire upper band and generous far-right white area calm and empty.
Wardrobe: DIFFERENT from refs: simple coral-red rolled-sleeve cotton work shirt with visible crayon hatching, no jacket, no headphones, no camera, no backpack, no accessories unrelated to the scene. His lower torso is only lightly visible through the lower window; do not force a full-body pose. Keep the adult compact proportions.
Only handwritten text: small navy “学习记录” on the top of the hanging paper; small red “公开分享” near its opened end. No other readable text, no large title. The character must be doing the opening and hanging action, not standing nearby. No duplicate Bornforthis, no additional human figures. Preserve both identity refs exactly in the face.
```

## 04 · 反馈与改进

用于第 41 页 Creator 与 Builder：把试用反馈贴到风筝上，认真调整真实作品的系线。

```text
IP Character Bornforthis (HIGHEST PRIORITY — preserve exactly the same identity in BOTH provided identity references): A youthful ADULT male, not a child, compact roughly 3.5–4-head-tall picture-book body; a large rounded-square PAPER-WHITE face, broad forehead, rounded cheeks and only slightly tapering lower face; thick saturated COBALT BLUE (#1262D5) short spiky hair with darker cobalt hatching, irregular upward tufts, very short faded sides and jagged natural forehead hairline; conspicuous outward-projecting semicircular ears, both visible, each one simple C inner line; short cobalt eyebrows, tiny cobalt dot/oval eyes with a simple curved upper-eyelid stroke; a tiny yellow nose dot and TWO flat perfectly round golden-yellow cheek circles; a short cobalt single-line closed-mouth smile, attentive and gently confident. No beard, no glasses, no huge anime eyes, no realistic skin, no pointed chin. This fixed FACE AND HAIR identity must survive every pose and outfit change.
The TWO attached images are identity references only, NOT composition or clothing references. DO NOT copy yellow backgrounds, white sticker borders, headphones, blue/yellow jacket, white T-shirt, beige baggy pants, huge sneakers, camera, bag, book, thumbs-up gesture or surrounding symbols. No fixed outfit.

Create ONE standalone 16:9 landscape Chinese article illustration with a pure clean WHITE background, no background texture. Deep navy slightly wobbly HAND-DRAWN outlines and visible natural diagonal CRAYON/MARKER HATCHING in EVERY colored region. Warm storybook drawing, slightly absurd but coherent, not slick vector, not 3D, not commercial stock art, not a presentation infographic. Mostly white negative space; scene occupies 40–60% of canvas, at least 35% quiet blank white space. At most 4–5 colors: cobalt blue, navy, golden yellow, coral red, soft orange plus paper white. No gradient, no cast shadow, no whole-background yellow or beige, no UI, no charts, no boxes-and-arrows layout, no top-left heading. Only the tiny specified Chinese handwritten labels, no long text.
Theme: A Builder learns from REAL USE and FEEDBACK, then adjusts the work. One fresh, warm low-tech metaphor: tuning a handmade kite after it wobbles in its first test.
Composition: A small hand-made coral-and-yellow diamond KITE is the single main prop, angled slightly in the air just above a small simple wooden workbench. A short navy frame and a loose white fabric tail show it is handmade, not polished. Bornforthis is kneeling to its LEFT, large enough that his fixed blue-spiky-hair face and both round ears are clearly seen. He is seriously and carefully retying the kite's BRIDLE at a new knot position with his two hands; one hand steadies the bridle while the other makes the knot. His eyes look at this real adjustment. A SMALL paper feedback note is clipped to the kite’s side, carrying the handwritten user feedback “有点晃”. A second tiny red annotation beside his working hands says “再调一调”. Two restrained navy wavy wind strokes near the kite show why tuning matters. A very small loose scrap of white tail fabric lies on the bench ready for a later adjustment. Everything should feel physically plausible: one coherent kite, one bridle, hands connected naturally, no floating random parts. The paper feedback note comes from an earlier real test, and the current action is improvement. Do NOT draw UI, dashboards, trophy, giant gears, multiple versions, cloned characters, paper boats, locks, keys, or a formal before/after split. Main scene lies across center and lower-middle with very generous pure-white margins and empty upper space.
Wardrobe: DIFFERENT from both refs and the other image: a plain short-sleeved cobalt work shirt under a paper-white canvas apron with light navy hatching, orange straight work trousers, plain low-profile dark-blue work shoes. NO headphones, NO varsity jacket, NO camera, NO beige baggy trousers, NO oversized reference sneakers. Adult proportions, quiet focused expression.
Only TWO tiny Chinese labels: navy “有点晃” on the feedback paper and red “再调一调” by the hands. No large title. The key story must be feedback visibly attached to a real object and Bornforthis actively changing that object.
```

