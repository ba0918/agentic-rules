# agentic-rules

[English](README.md) | 日本語

> この文書は [README.md](README.md) の日本語訳です。内容が食い違う場合は英語版を正とします。

AI コーディングエージェント向けの規範を [Agent Skills](https://agentskills.io) として
まとめたリポジトリです。規範はここに一度だけ書き、このリポジトリから多数のプロジェクト・
多数のエージェントへ配布します。

ここに置くのは**領域の規範だけ**です。ワークフローの自動化（手順・オーケストレーション）は
別の場所に置き、このリポジトリからは依存しません。

## インストール

更新をどう受け取りたいかで経路を選んでください。どの経路でも届くスキルは同じです。

| 経路 | エージェント | 更新の届き方 | 向いている用途 |
|---|---|---|---|
| プラグイン | Claude Code, Codex CLI, OpenCode | バージョンが上がったとき（下記参照） | 公開されたリリースに追従する |
| パッケージマネージャ | APM | `apm update`（`apm.lock.yaml` が固定したコミットから進める） | 複数のエージェントを 1 つのマニフェストで揃える |
| コピー | `gh skill`, `npx skills` | インストールコマンドを再実行する | リビジョンを固定したいプロジェクト・チーム・CI |

インストール済みのプラグインは、最新コミットではなく `.claude-plugin/marketplace.json` で
宣言されたバージョンに従います。変更がプラグイン利用者に届くのは、そのバージョンを上げた
リリースに含まれたときだけです。

### Claude Code

```
/plugin marketplace add ba0918/agentic-rules
/plugin install ba0918-rules@agentic-rules
```

### Codex CLI

Codex も同じマーケットプレイスのマニフェストを読みます。スキルはプラグイン名付きで
`ba0918-rules:ba0918-design` のように見えます。

```
codex plugin marketplace add ba0918/agentic-rules
codex plugin add ba0918-rules@agentic-rules
```

### OpenCode

`opencode.json`（プロジェクトのもの、またはグローバルの
`~/.config/opencode/opencode.json`）の `plugin` にこのリポジトリを追加し、OpenCode を
再起動します。

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugin": ["agentic-rules@git+https://github.com/ba0918/agentic-rules.git"]
}
```

このプラグインは `skills/` をスキルの置き場所として登録するだけです。スキルは OpenCode
自身の `skill` ツールから読み込まれ、セッションには何も注入されません。

### APM

[APM](https://github.com/microsoft/apm) は、npm がパッケージを管理するように、複数の
エージェントのスキルを 1 つの `apm.yml` で管理します。

```
apm install ba0918/agentic-rules --target claude
apm install -g ba0918/agentic-rules
```

1 つ目はプロジェクトにインストールします。Claude Code なら `.claude/skills/`、
`--target opencode` やその他のツール共通のターゲット（Copilot、Cursor、Codex など）なら
共有の `.agents/skills/` に置かれます。2 つ目はユーザースコープの `~/.apm/` 配下に
インストールします。依存を固定しないと APM が警告するので、リリースタグ
（`ba0918/agentic-rules#v<version>`）かコミット SHA で固定してください。

OpenCode だけならプラグイン経路で足ります。APM が役に立つのは、複数のエージェントを
1 つのマニフェストで管理するときです。

### コピー（`gh skill` / `npx skills`）

インストール時にスキルがプロジェクトへコピーされます。

```
gh skill install ba0918/agentic-rules
npx skills add ba0918/agentic-rules
```

`gh skill` は `@<ref>` を受け付けます。再現性が必要なら、リリースタグ（`v<version>`）か
コミット SHA で固定してください。

規範の意味を変える変更は、[CHANGELOG.md](CHANGELOG.md) で **BREAKING** と明記します。

## スキル

スキルは、扱う作業の種類ごとに分けて載せています。**読み込まれ方**は、エージェントが
そのスキルを読むきっかけを示します。

### 常に適用

| スキル | 範囲 | 読み込まれ方 |
|---|---|---|
| [`ba0918-design`](skills/ba0918-design/SKILL.md) | テスト可能性を最上位の目標とする設計原則 | `always` |
| [`ba0918-placement`](skills/ba0918-placement/SKILL.md) | 情報の置き場所：コード・テスト・コミットログ・コメントのどれに書くか | `always` |
| [`ba0918-readability`](skills/ba0918-readability/SKILL.md) | 技術的な意味を失わずに、なじみのない文脈を説明する人間向けの出力 | `always` |
| [`ba0918-secrets`](skills/ba0918-secrets/SKILL.md) | 認証情報と機密情報：検出、ステージング禁止、読み手の範囲の境界、第三者のライセンス、漏洩時の対応 | `always` |

### コードを書く

| スキル | 範囲 | 読み込まれ方 |
|---|---|---|
| [`ba0918-tdd`](skills/ba0918-tdd/SKILL.md) | テストファーストの契約（RED → GREEN → REFACTOR） | `required:implement` |
| [`ba0918-reuse`](skills/ba0918-reuse/SKILL.md) | 作る前に再利用を探す：層への分解、8 段の探索、採用か自作かの記録 | `required:design` |
| [`ba0918-gui-structure`](skills/ba0918-gui-structure/SKILL.md) | GUI の画面構成：領域ごとの部品、状態ごとに 1 つの持ち主、データは下へ・イベントは上へ、ダイアログ状態は 1 つ | `required:gui` |
| [`ba0918-testing`](skills/ba0918-testing/SKILL.md) | テストのアンチパターン | description |

### 変更を届ける

| スキル | 範囲 | 読み込まれ方 |
|---|---|---|
| [`ba0918-commit`](skills/ba0918-commit/SKILL.md) | コミットの分割とメッセージの規約 | `required:commit` |
| [`ba0918-ci`](skills/ba0918-ci/SKILL.md) | CI パイプラインの規律：既存のワークフローに揃える、外部のコードを固定する、最小権限、信頼できない入力を実行しない、有限の実行、ロジックはスクリプトへ | `required:ci` |
| [`ba0918-mutation-testing`](skills/ba0918-mutation-testing/SKILL.md) | 変異テストの運用の規律：マシンを守る資源の枠、決まった順で速くする、範囲の段、フックで回さず待たない、差分の見逃し0件を関門にする | `required:mutation` |
| [`ba0918-documents`](skills/ba0918-documents/SKILL.md) | 文書の規律：種類ごとのツリー、作る前に探す、事実の置き場所は 1 か所、種類ごとの寿命、偽になった文書はその変更の中で剪定する | `required:document` |
| [`ba0918-diff-review`](skills/ba0918-diff-review/SKILL.md) | レビューへの変更の提示：意図ごとにまとめ、理由と判断点を添え、承認対象のバイト列を明示する | `required:diff-review` |
| [`ba0918-release`](skills/ba0918-release/SKILL.md) | リリースの規律：正のバージョン、bump、破壊的変更、変更履歴、タグ | `required:release` |

### 他のエージェントと働く

| スキル | 範囲 | 読み込まれ方 |
|---|---|---|
| [`ba0918-delegation`](skills/ba0918-delegation/SKILL.md) | 委譲の規律：オーケストレータ原則、5 つの役割契約、実行役の表 | `required:delegate` |
| [`ba0918-verification`](skills/ba0918-verification/SKILL.md) | 検証の規律：証拠の要求、最悪値での集約、受け渡しの衛生 | `required:review` |
| [`ba0918-worktree`](skills/ba0918-worktree/SKILL.md) | worktree の運用：置き場所は 1 か所、名前はブランチとタスクに対応、書き手 1 つに作業ツリー 1 つ、成果を届けてから片付ける | `required:worktree` |

### スキルとプロジェクトの準備

| スキル | 範囲 | 読み込まれ方 |
|---|---|---|
| [`ba0918-skill-authoring`](skills/ba0918-skill-authoring/SKILL.md) | スキルの書き方：範囲、読む側のコスト、実行環境への非依存、発火する description、規範の種類に応じた書き方 | description |
| [`ba0918-scaffold`](skills/ba0918-scaffold/SKILL.md) | 利用側プロジェクトの `AGENTS.md` / `PROJECT.md` を生成する | 明示的な依頼 |

### スキルが読み込まれる仕組み

`always` と `required:<trigger>` は、各 `SKILL.md` の `metadata.ba0918-routing` の値で、
有効な形はこの 2 つだけです。`ba0918-scaffold` はこれを読んで、利用側プロジェクトの
`AGENTS.md` にルーティング表を生成します。`always` の規範はすべての作業で読まれ、
`required:<trigger>` の規範はそのトリガーが指す作業の前に読まれます。

このフィールドを持たないスキルはルーティング表に載りません。エージェントは、スキルの
description が作業に合ったとき、または人が名前を挙げて頼んだときに読み込みます。

## このリポジトリの開発

### 命名

スキル名は `ba0918-<領域を表す名詞>` です。`ba0918` はオーナーのユーザー ID で、フラットな
グローバルのスキル名前空間での衝突を避けるためだけに付けており、変わることはありません。
領域の名詞は短い一般的な英単語 1〜2 語です。名前は英小文字・数字・ハイフンで 64 文字以内とし、
ディレクトリ名と一致させます。

スキルのディレクトリが配布の単位で、それ自体で完結しています。ディレクトリの外のパスは
参照せず、スキル同士は名前だけで言及します。

### スキル文書の構成

規範スキルの `SKILL.md` は、Scope、Rules、Judgment、Examples、Evidence をこの相対順で
載せます。それぞれの書き方の規約は、正となる設計仕様
[docs/spec/repository-design.md](docs/spec/repository-design.md) で定めています。節の順序は
レビューで確認する事項で、バリデータは検査しません。

### 検証

```
python3 scripts/validate.py              # このリポジトリの規約
uv run --with pytest -- pytest tests/    # バリデータ自身のテスト
```

`scripts/validate.py` は Python の標準ライブラリだけを使います。各スキルの frontmatter、
名前、500 行の上限、description の 1024 文字の上限、routing の値を検査し、スキルの
ディレクトリの外へ出る参照がないことを確かめます。さらに `.claude-plugin/plugin.json`、
`package.json`、[CHANGELOG.md](CHANGELOG.md) の最新リリースの見出しが、正のバージョン
（`.claude-plugin/marketplace.json` の `plugins[0].version`）と一致することも検査します。
違反がなければ 0、違反があれば 1、渡したパスがディレクトリでなければ 2 で終了します。

CI では Agent Skills のリファレンスバリデータ `skills-ref validate` もすべてのスキルに
実行します。このバリデータは Agent Skills のリポジトリから、固定したコミットで
インストールします。こちらは公開仕様を、ローカルのバリデータはこのリポジトリの規約を
検査します。両方とも通る必要があります。
