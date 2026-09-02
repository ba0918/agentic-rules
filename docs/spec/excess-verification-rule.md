# 検証の過剰の規約(ba0918-verification 追記)

## 目的と出典

AI による高速な生成は、コードだけでなく検証も規模に釣り合わずに蓄積する。出典は小さな
CLI ツールの実装で、本体よりテストと CI の検査の方がはるかに大きくなり、人が二度にわたって
縮小した。膨らみ方には構造があった: 仕様が境界シナリオを全て反例として列挙し、計画が
名指しのテストを足し、適合レビューが未テストの項目を全て指摘にし、修正役が指摘ごとに
oracle(テスト・検査・fixture)を作る。各工程に「足す」操作しかなく、「削る」「コストを見る」
操作がどこにも無い。

象徴的な連鎖はこうである。仕様が、対応環境では起き得ない失敗のための診断文言を定める。
レビューが「その文言に対応する振る舞いテストが無い」を指摘する。修正役が libc を差し替えて
失敗を捏造する fixture を C で書く。人がそれを消す。検証基盤を検証するテスト — CI workflow
の文面を読んで step の並びを断言する、ヘルパが自分自身を検証する — も肥大し、workflow を
少し触るだけで壊れた。人の言葉では「検証の検証は勝手に実装しない」である。

一部は既存規則の不履行でもあった(warn の指摘は新しいテストを要求しない、という規則が
あるのに要求された)。だから採るのは散文の戒めではなく、レビューがその場で当てられる観測
可能な条件である。

原型は YAGNI(You Aren't Gonna Need It)の精神である。ただし「要らなかった」は証明できず、
精神のままでは検証不能で、レビューで裁けない。継ぎ目の規約(proportionality-rule.md)と
同じく、採るのは検証可能な言い換えだけである: **oracle が証拠として数えられる条件を観測
可能に定め、条件を満たさない oracle はコストと扱う**。

これは簡潔さという第二の原則ではなく、ba0918-verification の柱「主張は証拠ではない」の
延長として扱う。到達不能な条件の下で得た観測もまた、証拠ではない。

置き場所が verification である理由: 定義は「何が証拠か」に落ちる。routing は
`required:review` で、過剰な指摘が生まれるその場で読まれる。要件を書く工程と計画を書く
工程への届け方は「写せる形(contract)」の節で定める。

## 判定基準

「変わりやすい」「将来壊れる」は予測であり、判定には使わない。oracle は次の 4 条件を
全て満たすときだけ証拠である。1 つでも欠ければコストであり、足す・残す・要求する理由に
ならない。

1. **到達可能な条件。** oracle が作り出す条件を、対応環境のどれかが運用中に生み出せる。
   判定は、テストまたは指摘が、その条件の運用上の生み手を名指しできること。生み手が
   oracle 自身の差し替えしか無い条件は到達不能である。
   例: ユーザーデータベースの home 欄が空 — 生み手は「そういう利用者」で、libc を差し替えて
   再現しても正当。シグナル設定の照会が失敗する — 生み手を名指しできず、到達不能。
2. **対象が oracle 自身でない。** oracle の対象が製品(そのプロジェクトが作るもの。補助
   スクリプトや workflow を含む)または検査であって、oracle 自身ではない。製品のソースを走査して禁止された API が無いことを確かめるのも、検査を実行して
   exit と出力を観測するのも、対象は製品や検査であり正当。検査やヘルパが自分自身を検証する
   のは違反。
3. **仕様が述べた規則。** 検査が強制する規則を仕様が述べている。仕様に無い規則(例: 変更履歴の
   日付が実在の暦日であること)を検査が強制するのは違反。
4. **契約として宣言された表現。** oracle が固定する文言・ファイルの構造・内部の名前を、
   仕様が契約として宣言している。判定は「仕様の振る舞いを全て保ったまま行える変更で、
   この oracle は壊れるか」。壊れるなら振る舞いの証拠ではない。仕様が宣言した表現(例:
   診断の固定接頭辞)の固定は正当。CI workflow の文面や step の並びを断言するテストは、
   仕様がその規則を述べていても、その表現を宣言していない限り違反。

宣言の読み取り元: 「仕様」はそのプロジェクトが規範とする仕様文書。仕様文書を持たない
プロジェクトでは、利用者向けの公開文書(README、help、公開 API の文書)を宣言の読み取り元と
する。「対応環境」はその文書が対応と宣言する OS・アーキテクチャ・実行系である。

規模では裁かない。大きな fixture でも対象が到達可能な振る舞いなら正当で、一行の断言でも
宣言の無い文言を固定すれば違反である。「fixture が対象より複雑」は臭いとして Judgment に
置くが、評決の根拠にはしない。

条件は独立に効く。仕様が文言を宣言していても、その文言が出る条件が到達不能なら条件 1 で
違反である。

### 写せる形(contract)

要件を書く工程と計画を書く工程は verification を読まない。それらの工程を持つ workflow
側のスキルへは、本リポジトリの `contracts/oracle-evidence.md` を正本として、その本文を
写して届ける。写した先には出典として本規則の名前と対応する版を添える — 正本が変わったのに
写しが古いままの状態を、版の照合で見つけられるようにするためである。digest による自動同期
(agentic-skill-vendor の contract)への移行は、写しのドリフトが実害を出した時点で判断する。
repository-design の「共有原典への移行は自動発動しない」と同じ段階を踏む。本文は 2 段落
(英語)。第 1 段落は Rules 追記の 1 行目と同じ 4 条件と禁止。第 2 段落は要件の処遇を、
要件を書く側の行為として述べたもので、Rules 追記の 3 行目はその同じ処遇をレビューする側が
記録し提案する形で述べる。正本と一字一句同じ本文を以下に示す:

> An oracle — a test, a check, or a fixture — counts as evidence only when the condition it
> produces has a named operational producer in a supported environment, its subject is the
> product or a check rather than the oracle itself, the rule it enforces is stated by the
> specification, and every wording, file layout, or internal name it pins is declared there as
> a contract. An oracle that fails any of these is a cost: do not add it, keep it in a change
> under review, or demand it.
>
> A requirement whose only oracle would fail these conditions is not mechanically verifiable:
> when it is not code, verify it by a human-run check or by the platform's own checker; when it
> is code, drop the requirement and let the failure join a generic error path a reachable
> failure already proves — never resolve it by having the implementer build the fixture.

## 3 つの層

- **要件層(仕様を書く工程)。** 要件の oracle が 4 条件を満たす形で書けないなら、その要件は
  機械検証できない。コード以外の要件(workflow ファイル、文書、実際に動かして観測する
  プラットフォームの振る舞い)は、人が実行して確認する検査か、プラットフォーム自身の検査器
  (workflow の lint など)で確認する要件として記録する。コードの振る舞いで、生み手が捏造しか
  無い条件は振る舞いではない: 要件を落とし、その失敗は到達可能な失敗が既に証明している
  汎用のエラー経路に合流させる。専用の分岐・文言・テストを作らない。実装者に fixture を
  作らせることで解決しない。届け方は「写せる形(contract)」。
- **oracle 層(実装とレビュー)。** レビュー対象の差分が条件を満たさない oracle を足せば指摘。
  差分が行を変更した既存の oracle(テスト関数、検査の step)が条件を満たさなければ、その
  削除を差分の範囲内の修正として指摘する。差分が触れていない oracle は対象外。
- **指摘層(レビューと修正)。** 新しい oracle の作成を求める指摘は、その oracle が 4 条件を
  満たすことを指摘自身が示す。示していない指摘は、既存の処遇のうち「記録された提案」か
  「文書化された不同意」になり、修正にはならない。

## 既存規範との関係

「主張は証拠ではない」との関係は延長である。既存の Rules 行は改稿せず追加のみとする —
吸収・改稿は既存ルールの意味変更(BREAKING)に触れるためである。

「finding は権威ではなくデータ」とは一致する。finding の 3 つの処遇(差分内の修正、記録された
提案、文書化された不同意)は変えない。変えるのは、oracle を要求する finding が満たすべき
完全性の条件を足すことで、満たさない finding は 3 つのうち修正にならない。

「決定的な検査を自分で実行してから PASS を記録する」との関係: 機械検証できない要件は PASS に
ならない。既存の UNVERIFIED に、理由と処遇の提案を添えて記録する。これは要件ごとの記録で
あり、レビュー全体の評決の軸(必須レビュアの欠落で全体が UNVERIFIED になる規則)は変えない。
その要件は誰にも検証できないので、評決の隣に記録して処遇の提案を人に回す。

Rules 追記の 2 行目は、完全性を欠く finding が「修正」になることを閉じる。finding の処遇を
選ぶのが受け入れ側であることは変わらないが、選択肢が 1 つ狭まる。既存行の意味変更ではなく
新しい制約の追加と判断し、CHANGELOG には Added として載せる。

ba0918-tdd との境界は production code とそれ以外である。人が実行する検査やプラットフォームの
検査器に委ねるのはコード以外の要件に限る。コードの振る舞いで生み手の無い失敗は、テスト
無しの production code を許すのではなく、要件を落とす。tdd の鉄則「失敗するテスト無しに
production code を書かない」と衝突しない。

ba0918-design の置換可能性の規則とは同じ判定を共有する — 契約ではなく実装の詳細を固定する
テストは契約を測っていない。design はそれを構造の側から、本規約は証拠の資格の側から述べる。

非決定性(sleep による同期など)は本規約の範囲外である。現行の規則群にそれを扱う規範は無い。

ba0918-reuse の梯子 1 段目(「その層はそもそも要るか」)と重なるように見えるが、reuse は
記録を裁き評決を裁かない原則を持ち、routing も design 時点である。本規約は評決(削除)を
出し、review 時点で読まれる。

## ba0918-verification への追記

Rules に加える規範(3 行。各行は 1 つの命令とその帰結):

- Count an oracle — a test, a check, or a fixture — as evidence only when the condition it
  produces has a named operational producer in a supported environment, its subject is the
  product or a check rather than the oracle itself, the rule it enforces is stated by the
  specification, and every wording, file layout, or internal name it pins is declared there
  as a contract; an oracle that fails any of these is a cost — do not add it, keep it in the
  diff under review, or demand it.
- Accept a finding that demands a new oracle only when it shows that the oracle meets those
  conditions; a finding that does not becomes a recorded proposal or a documented
  disagreement, never a fix.
- Record a requirement whose only oracle would fail those conditions as UNVERIFIED with the
  reason, and propose its disposition: a human-run check or the platform's own checker when
  it is not code, dropping the requirement when it is code with its failure joining a generic
  error path a reachable failure already proves — never a fixture to build.

Judgment に加える項目(既存と同じく、太字の主張 1 文 + 説明。3 項目):

- **到達不能な条件の下で得た観測も証拠ではない。** 主張と同じく、その観測は検証しようと
  する振る舞いから切り離されている。捏造した失敗が通ることは、診断の分岐が存在することを
  示すだけで、製品が正しいことを示さない。「仕様」は規範とする仕様文書、無ければ利用者向けの
  公開文書であり、「対応環境」はその文書が宣言するものである。
- **oracle が測るのは対象であって、oracle の形ではない。** 自分自身を検証する検査は無限に
  後退する。仕様に無い規則を検査が強制すると、誰も決めていない要求が製品に課される。宣言の
  無い表現を固定する oracle は、振る舞いを保つ変更で壊れるので、測っているのは振る舞いでは
  なく変更の頻度である。
- **規模は臭いであって評決ではない。** fixture が対象より複雑なら、条件のどれかが欠けて
  いないかを見る合図である。大きな fixture でも対象が到達可能な振る舞いなら正当で、一行の
  断言でも宣言の無い文言を固定すれば違反である。

Examples に加える対比(2 組。1 組目は手法を両側で同じにし、違いは条件だけにする。2 組目は
対象の違いを示す):

- 対応環境では起き得ない失敗のために仕様が診断文言を定め、レビューがその振る舞いテストを
  要求し、修正役が libc を差し替えて失敗を捏造する(Bad)。運用上の生み手がある稀な条件
  (例: アカウント情報の home 欄が空)を、同じ libc 差し替えで再現して観測する(Good)。
  違いは差し替えという手法ではなく、条件に生み手がいるかどうかである。
- テストが CI workflow ファイルを読み、step の文面と並びを断言する(Bad)。テストが
  ヘルパを fixture 付きで実行し、exit と、仕様が述べた結果(停止したか、続行したか)を断言する。
  workflow の構造はプラットフォームの検査器に委ねる(Good)。

Evidence に加える項目(レビュー対象の差分だけに要求する):

- 差分が足した oracle ごとに、条件の運用上の生み手、対象、規則を述べる仕様の見出し。
  文言・ファイルの構造・内部の名前を固定する oracle に限り、その表現を宣言する仕様の見出しも。
- 新しい oracle を要求する finding ごとに、同じ項目。
- 差分が削った oracle ごとに、欠けていた条件。
- UNVERIFIED と記録した要件ごとに、欠ける条件の理由と、提案した処遇。

リポジトリ全体の証明は要求しない。

## 適用範囲

既存の oracle の棚卸しは要求しない。対象は、レビュー対象の差分が条件を満たさない oracle を
足さないこと、および差分が行を変更した oracle が条件を満たすことのみである。description は
変更しない — 発火条件は変わらず、変わるのは読まれた後の規範だけである。運用して違和感が
出た時点で見直す。

## 出典データとの照合

出典の縮小で人が消したものと残したものを、4 条件で分類した結果である。出典は私的な
プロジェクトのため、種類だけを記す。

| 人の判断 | 種類 | 判定 |
|---|---|---|
| 消した | シグナル設定の照会失敗、記述子状態の記録失敗を捏造する fixture とそのテスト | 条件 1 |
| 消した | CI workflow の文面と step の並びを断言するテスト | 条件 4 |
| 消した | テストヘルパの自己検証 | 条件 2 |
| 消した | 変更履歴の日付の実在暦日検証、直前コミットとの変更履歴一致 | 条件 3 |
| 消した | private 関数名をソースに要求するテスト | 条件 4 |
| 消した | 境界テストのうち実装の文言に依存した断言 | 条件 4 |
| 残した | ユーザーデータベースの空 home 欄を libc 差し替えで再現するテスト | 素通り |
| 残した | argv[0] と引数を C のレポータで観測するテスト | 素通り |
| 残した | リリース補助スクリプトを fixture 付きで実行し、exit と仕様が述べた結果を断言するテスト | 素通り |
| 残した | 製品ソースを走査して禁止 API が無いことを確認するテスト | 素通り |
| 消した | 同期を sleep で待つテスト | 範囲外(非決定性。現行規則に無い) |
