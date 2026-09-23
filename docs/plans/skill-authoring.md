# 実装計画: ba0918-skill-authoring の追加

## Goal

どのリポジトリでもスキルを書くときに読まれる規範スキル `ba0918-skill-authoring` が配布物に加わり、
`repository-design.md` のスキル執筆に関する節がそのスキルの仕様を参照する形に整理された状態にする。

## Specification

`docs/spec/skill-authoring-rule.md`(以下「仕様」)。見出しは仕様の見出しをそのまま使って参照する。
このリポジトリの前提は `AGENTS.md` と `PROJECT.md` を先に読むこと。

## Approach and why

作業は 3 段に分ける。

1. スキル本体(SKILL.md)を先に書く。後の 2 段はどちらも「このスキルがある」ことを前提に
   参照を置くので、参照先を先に存在させる。
2. `repository-design.md` の 4 節から規範を移し、参照に置き換える。スキル本文を書き終えてから
   行うのは、移す対象と SKILL.md の記述を突き合わせて、落ちた規範がないかを確かめるため。
3. 配布まわり(README・manifest 2 つ・CHANGELOG)を揃える。配布物の記述は最後にまとめて直し、
   1 コミットで一貫させる。

各段の終わりで 1 コミットする(コミット規約は `ba0918-commit`)。

SKILL.md は、仕様が定める規範に自分自身も従って書く(自己適用)。特に: 本文は英語、
description は英語 + `日本語キーワード:` 付き、構成順は Scope → Rules → Judgment → Examples →
Evidence(このリポジトリでは規範スキルに必須)、routing メタデータを持たない、原則名を出さない、
外部ガイドラインを引用しない。既存スキル(例: `skills/ba0918-reuse/SKILL.md`)の見出しと体裁に
揃える。

## Scope of change

- `skills/ba0918-skill-authoring/SKILL.md`(新規)
- `docs/spec/repository-design.md`
- `README.md`
- `.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`(description のみ。version と keywords は変えない)
- `CHANGELOG.md`(Unreleased のみ)

これ以外のファイル、特に既存スキルの SKILL.md、`scripts/validate.py`、`tests/`、
`regression-lock.json`、`PROJECT.md` は変更しない。

## Step order and prerequisites

Step 1 → Step 2 → Step 3 の順。各 step は前の step のコミットを前提にする。

## Verification map

| 仕様の見出し | 確かめる step |
|---|---|
| 発火条件 | Step 1 |
| 対象 | Step 1 |
| 規範(1〜6 のすべて) | Step 1 |
| 既存スキル・文書との境界 | Step 1 |
| 作らないもの | Step 1(本文に含めないことの確認) |
| repository-design.md との分担 | Step 2 |
| リポジトリへの組み込み | Step 1(SKILL.md の追加)、Step 2(初期スキル表)、Step 3(残り) |
| 受け入れ確認 | Step 1 と Step 3 のチェック。人による合格条件との突き合わせは、全 step の完了後に結果を受け入れるときに行う |

## Left to the implementer

- SKILL.md の英語の文言、節内の小見出しの切り方、対比例の具体的な題材(仕様の反例と同じ意味を
  保つこと)
- README・manifest・CHANGELOG に足す英語の言い回し

## Stop conditions

一般の 4 条件(意味の欠落や承認内容からの逸脱 / 不可逆・特権・危険な操作 / 波及する事故 /
方針を変えても進まない)に加え、次のときは作業を止めて返す。

- 仕様の規範どうし、または仕様とこのリポジトリの既存の決まりが、SKILL.md に書こうとして
  両立しないと分かったとき
- description を仕様の発火条件どおりに書くと 1024 文字の上限を超えるとき
- バリデータが、routing メタデータのないスキルや、仕様どおりの記述を違反として扱うとき

## Out of scope

- 既存 13 スキルをこの規範に合わせる修正
- バージョンの bump とタグ(リリース時に行う)
- バリデータへの新しい検査ルールの追加
- `PROJECT.md` の変更(仕様と同時にコミット済み)

---

## Step 1 — スキル本体を書く

Purpose: 仕様の規範をスキル本文として書き起こす。
Specification: docs/spec/skill-authoring-rule.md#発火条件, #対象, #規範, #既存スキル・文書との境界, #作らないもの, #受け入れ確認.
Prerequisites: なし(ブランチ `feat/skill-authoring` に仕様がコミット済み)。
May change: `skills/ba0918-skill-authoring/` 配下のみ。`references/` を作るかどうかは仕様「規範」の
規範 2 に従って判断してよい。
Done when:
- frontmatter に `name: ba0918-skill-authoring` と description があり、`ba0918-routing` がない
- description が仕様「発火条件」の 3 場面を使う場面として挙げ、使うだけ・監査評価を挙げていない。
  規則の中身・手順は含まない(仕様 規範 5)
- 本文の最初の節が Scope で、仕様「対象」の 3 点(Agent Skills 形式に限る・両種類を対象にし
  片方限定の規範は種類を明記・部分的な書き換えは書き換えた箇所だけ)と、
  「既存スキル・文書との境界」の各項(隣接スキルは名前で)を述べている
- 規範 1〜6 の各項目が本文にあり、仕様の各節の合格条件を満たす
- 原則名(SOLID・DRY など)、外部ガイドラインの引用、検証・評価の規範、「文脈ごとに 1 回読む」
  規約が本文にない
Shown by: check — 次を順に実行する。合格の判定は各項目に書いたとおり。
1. `python3 scripts/validate.py` — 終了コード 0
2. `npx --yes skills-ref@0.1.5 validate skills/ba0918-skill-authoring/` — 終了コード 0
3. `rg -n -i -e '\bsolid\b' -e '\bdry\b' -e 'single responsibility' -e 'open[-/ ]closed' -e 'liskov' -e 'interface segregation' -e 'dependency inversion' skills/ba0918-skill-authoring/` — 出力が空であること(rg は一致なしで終了コード 1 を返す。これが合格)
(`tests/` の pytest は合成フィクスチャだけを検査し `skills/` を読まないので、この step の証拠にしない。)
Left to the implementer: 本文の英語の言い回しと、Judgment / Examples 節への項目の振り分け。
Stop and hand back if: 仕様の規範のうち、英語にしたとき 2 通りに読める語があり、どちらの読みかを
仕様から決められないとき。

## Step 2 — repository-design.md を整理する

Purpose: スキル執筆の一般規範を仕様側へ移し、`repository-design.md` にはこのリポジトリ固有の
決まりと参照だけを残す。
Specification: docs/spec/skill-authoring-rule.md#repository-design.md との分担, #リポジトリへの組み込み.
Prerequisites: Step 1 のコミット。
May change: `docs/spec/repository-design.md` のみ。
Done when:
- 「執筆スタイル」「SKILL.md と references/ の分担」「スキル自己完結の原則」「手続き型スキルの
  実行条件」の 4 節が、仕様「repository-design.md との分担」の振り分けどおりになっている
  (移すとした規範の本文が消え、`skill-authoring-rule.md` への参照があり、残すとした決まりが残る)
- 「執筆スタイル」節の構成順の記述が、対象を「各スキル」から規範スキルに限る形に直っている
  (仕様「repository-design.md との分担」の「残る決まり」の構成順の項)
- 「手続き型スキルの実行条件」の見出しが残り、中身は仕様への参照 1 行
- 「命名規約」節は変わっていない
- 「初期スキル」表に `ba0918-skill-authoring` の行がある(内容列はスキルの一行説明で、詳細仕様として
  `skill-authoring-rule.md` を括弧書きで示す。種列は「既存文書の一般化 + 運用実績の蒸留」。
  既存行の書き方に揃える)
- 移した各規範が Step 1 の SKILL.md に存在する(落ちた規範がない)
Shown by: artifact — `docs/spec/repository-design.md`。`git diff docs/spec/repository-design.md` を
仕様「repository-design.md との分担」の箇条と 1 項目ずつ突き合わせた結果(箇条ごとに、対応する差分の
行)を完了報告に書く。
Left to the implementer: 参照文の言い回しと、残す文の最小限の書き直し(意味を変えない範囲)。
Stop and hand back if: 移す規範のうち Step 1 の SKILL.md に対応する記述がないものが見つかったとき
(SKILL.md を直すか移さないかは仕様の判断なので、自分で決めない)。4 節以外の節が、移す規範の本文を
前提に書かれていて、参照に置き換えると意味が通らなくなるとき。

## Step 3 — 配布まわりを揃える

Purpose: 新しいスキルを配布物の説明と変更履歴に載せる。
Specification: docs/spec/skill-authoring-rule.md#リポジトリへの組み込み, #受け入れ確認.
Prerequisites: Step 2 のコミット。
May change: `README.md`、`.claude-plugin/plugin.json`、`.claude-plugin/marketplace.json`、
`CHANGELOG.md`。
Done when:
- README のスキル表に `ba0918-skill-authoring` の行があり、Routing 列が `fires from its description`
- README 冒頭の領域の列挙にスキル執筆が入っている
- README「Skill document structure」節の「Every `SKILL.md`」が、規範スキルに限る記述になっている
- 2 つの manifest の description が、スキル執筆(skill authoring)を含む同一の文字列である。
  version 欄は変わっていない
- CHANGELOG の `## [Unreleased]` の下に `### Added` があり、新スキルの追加が、このセッションを
  知らない読者にも分かる文で書かれている(既存の Added 項目の書き方に揃える)
Shown by: check — 次を順に実行する。合格の判定は各項目に書いたとおり。
1. `python3 scripts/validate.py` — 終了コード 0
2. `python3 -c "import json; a=json.load(open('.claude-plugin/plugin.json'))['description']; b=json.load(open('.claude-plugin/marketplace.json'))['plugins'][0]['description']; assert a == b and 'skill authoring' in a"` — 終了コード 0
3. `git diff 0e944ff -- .claude-plugin/ | rg '"version"'` — 出力が空であること(一致なしの終了コード 1 が合格)
Left to the implementer: 追記する英語の言い回しと、manifest の列挙の中でスキル執筆を置く位置。
Stop and hand back if: バリデータやテストが、Unreleased に項目があることや manifest の description の
変更を、バージョン未 bump として違反扱いするとき(bump はこの計画の範囲外)。
