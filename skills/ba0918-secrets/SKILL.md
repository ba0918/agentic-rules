---
name: ba0918-secrets
description: "Handling credentials and confidential material in a working repository — recognising keys, tokens and environment files, keeping them out of staged changes, logs, prompts and commit messages, and the first moves when one leaks. Also keeping confidential context (internal project names, internal hostnames, customer names, confidential documents) out of any destination whose audience is wider than the source's — a public repository's code, documentation, commit logs, issues and pull request text, and a broader private one alike — and copying third-party work only under a licence that permits it, in any destination. Use when touching configuration or environment files, staging changes, pasting output, writing a commit message, writing anything derived from a private context into a wider-audience destination, copying code or prose from an outside source, or responding to a suspected leak. 日本語キーワード: 機密情報 シークレット 認証情報 APIキー トークン 環境変数 .env 漏洩 露出 失効 ローテーション 機密文書 内部情報 プロジェクト名 著作権 著作物 ライセンス 公開リポジトリ 絶対パス ユーザ名 環境固有"
metadata:
  ba0918-routing: always
---

# Secret Handling

## Scope

Applies to credentials that pass through a working repository or an agent session: API keys,
access tokens, private keys, passwords, connection strings, session cookies, and the environment
files that hold them.

It covers four things: recognising a credential, keeping it out of version control, keeping it
out of anything that records it or carries it where it was not meant to go, and the first moves
after a leak.

It applies the same four moves to **confidential context and third-party material**: information
that identifies or reproduces private or protected content — internal project and product names,
internal hostnames and domains, customer names, the contents of confidential documents, the
environment the session itself runs in, and copyrighted works without a licence to redistribute.
The rule surface is every artifact the session writes and every field it fills in on the way out:
code and comments, tests, documentation, plans and working notes, commit messages, the author and
committer identity recorded with them, any trailer a tool appends, branch names, issues, and pull
request text.

It does not cover secret storage systems, key management design, or access control policy.

## Recognising a credential

| Signal | Examples |
|---|---|
| Environment files | `.env`, `.env.local`, `.env.production`, `credentials`, `secrets.yaml` |
| Key material | `id_rsa`, `*.pem`, `*.key`, `*.p12`, `*.keystore` |
| Provider token shapes | a fixed vendor prefix followed by a long random tail |
| High-entropy assignment | a name containing `key`, `token`, `secret`, `password`, or `credential` assigned a long opaque literal |
| Connection strings | a URL carrying a username and password in its authority section |

Treat a value as a credential when it grants access on presentation. Length and randomness are
hints, not the test.

## Recognising confidential context

| Signal | Examples |
|---|---|
| Internal identifiers | project and product codenames, repository names of private work |
| Internal network names | non-public hostnames, internal domains (`*.local`, `*.corp`), internal URLs and server paths |
| Local environment | the account a session runs as, the absolute path of its working clone, its home directory, the machine's hostname, the identity version control is configured with, the session identifiers its tooling appends |
| Business relations | customer, partner, and vendor names tied to non-public work |
| Private documents | text quoted or paraphrased from specs, contracts, or internal reports |
| Third-party works | code or prose copied from a source whose licence does not permit redistribution |

Treat a value as confidential context when it lets the destination's audience identify, locate,
or reproduce private or protected material they were never given. A credential grants access;
confidential context discloses existence — the test is the audience, not the value's shape.

Material the session produced itself counts. An account name or an absolute path read off the
machine came from no source document, so there is no narrower side to compare against; the
destination's audience decides on its own.

## Rules

- Never stage a credential. Never commit one.
- Never add an environment or key file to version control; add it to the ignore file instead.
- Stage files individually and read what you are staging before committing.
- Keep the real value out of anything that records it, or carries it somewhere it was not meant
  to go: commit messages, branch names, pull request text, logs, error messages, terminal
  output, prompts, issue reports, pasted output. Substitute a placeholder there, at the moment
  you first handle the value. Presenting the value to the service it authenticates against is
  its intended use, not a leak.
- Reference a credential by the name of its variable, never by its value.
- Use an obviously fake placeholder in documentation and tests, never a real value that is "expired".
- Before writing anywhere, compare the destination's audience with the source's. A destination
  whose audience is wider than the source's crosses the boundary — most sharply a public
  repository's code, documentation, commit log, issues and pull requests, and no less a more
  broadly shared private one. Material from the narrower side crosses only with its identifiers
  removed.
- Apply that comparison to what the session writes itself, not only to what it carries in from a
  source. When there is no narrower source, the destination's audience is still the test.
- Name a location by a path relative to the repository root. An absolute path from the machine the
  session runs on — a home directory, a working clone, a user profile — belongs in no tracked
  file, commit message, or outward-bound text, and neither does the account name or hostname it
  spells out.
- Keep environment-specific facts in session-local working state, or in the text handed to a
  delegate, rather than in a committed document. A plan that records where the work happened is
  the usual carrier.
- Read the fields a commit carries besides its message: the author and committer identity, and any
  trailer a tool appends. Both are fixed when the commit is made, so rewording the message later
  does not correct them.
- Judge the identity and the trailers by the same audience test as everything else. An address
  that names a person crosses; one the owner already publishes to that audience does not. A
  trailer crosses when it points that audience at work it was never shown, and not when the
  identifier it carries is one that audience cannot reach. The forge's no-reply address is the
  usual way to satisfy this, not the rule.
- Do not commit the output of a command whose scope was wider than this repository — a listing of
  a parent directory, an inventory of other clones, a dump of the environment. Reproduce only the
  part that concerns this repository, and name where it came from.
- When private work motivates a public change, keep the structural lesson and drop the
  identity: "a real project's friction measurement", never the project's name.
- Never carry confidential document content across an audience boundary. Within the audience
  already authorised for it, working from it — implementing what it requires in code, tests,
  or internal documentation — is ordinary work. Outward of that audience, refer to the
  document by a pointer that audience can legitimately reach, or not at all.
- Never reproduce third-party material without a licence that permits the copy. Here the
  licence decides, not the audience: a private destination does not make an unlicensed copy
  acceptable.

## Judgment

**Revocation is the only action that actually stops a leak.** Rewriting history removes the value
from the current branch, but the value may already exist in a clone, a fork, a CI log, a
notification, or a build cache. Until it is revoked and replaced, assume it is live. History
cleanup matters, but it is the second step, not the first.

**Revocation is irreversible in the same way rewriting shared history is.** A revoked credential
cannot be un-revoked, and cutting it can break running services far beyond the current session.
That blast radius is why the decision belongs to a human: the agent's part is to raise the alarm
and press for it, not to execute it.

**Redaction has to happen before the value is recorded, not after.** Once a credential reaches a
log file, a chat transcript, or a model prompt, you no longer control every copy. The moment to
substitute a placeholder is when you first handle the value.

**"It is only a development key" is not a category.** Development credentials routinely reach
shared infrastructure and are rarely scoped as narrowly as assumed. Apply the same rules and
decide the blast radius during revocation, not during staging.

**Bulk staging is the usual cause.** Adding everything at once is how environment files and key
material enter history, and history is expensive to correct once pushed. Individual staging is
the mechanism that makes the rule enforceable.

**A near-miss is worth recording.** When a credential nearly reached a commit, add the path to
the ignore file so the same near-miss cannot recur.

**A name grants no access, yet it still discloses.** An internal project name, hostname, or
customer name passes the credential test and every secret scanner — which is exactly how it
leaks: nothing flags it. What it reveals is existence and relationships: that the work exists,
who it is for, where it runs. The audience comparison is applied by hand; no scanner does it.
A paraphrase is worse still: strip the names out of a confidential passage and there is no
search term left, so nothing but knowing where the text came from will catch it.

**Your own environment is a source.** The account a session runs as, the path of its working
clone, the hostname of the machine it sits on — nothing handed these over, so they read as
ambient facts rather than as material with an audience, and the comparison never gets applied to
them. A credential scan clears them too, because a path grants nothing on presentation. They are
also the only class here with a fixed shape: a short set of absolute-path prefixes, the same on
every machine. That makes this the one class to search for rather than reason about — no list has
to be right for the search to find it. The search has a blind spot all the same: only the path form
has a shape. A bare list of names — the directories beside the working clone, the other clones on
the machine — discloses the same existence and passes every scan, so that half stays judgment, and
the moment to apply it is when the output is pasted, not when the commit is made.

Metadata is the harder half. A message can be reworded, but the identity and the trailers a commit
carries are fixed the moment it is made, so correcting them means rewriting the commit and every
commit after it. The check therefore belongs before the commit; the one before the push is only a
backstop.

**Leaked information cannot be revoked.** A credential has a provider that can kill it; a name,
a document, or a copyrighted text does not. Once pushed, assume it has been fetched — edit
histories and forks keep copies. Prevention is the only strong control; response after the fact
is containment, and containment is never complete.

**For third-party works, the licence is the test, not availability.** That a text or a snippet
is easy to find does not make it redistributable. Copy only under a licence that permits it,
and carry the licence's obligations (attribution, notices) along with the copy.

## Examples

A value exposed in a message, and the same fact stated safely:

```
Bad:  fix: API キー <実際のキー文字列を貼り付け> が失効したので差し替え
Good: fix: 決済 API の認証情報を差し替え（旧キーは失効済み）
```

A sample that invites copying, and one that cannot be mistaken for real:

```
Bad:  PAYMENT_API_KEY=<a realistic-looking vendor-prefixed literal>
Good: PAYMENT_API_KEY=<your-secret-key>
```

The Bad line above is written as a description rather than as a literal on purpose: a
documentation sample shaped like a real credential gets copied verbatim, and gets flagged by
every scanner that reads this file.

A private project named in a public artifact, and the same motivation stated safely:

```
Bad:  feat: <社内プロジェクト名> で要件合意の漏れが実害になったためチェックを追加
Good: feat: 実プロジェクトで要件合意の漏れが実害になったためチェックを追加
```

A document recording where the session ran, and the same instruction without it:

```
Bad:  Run the validator in /home/<account>/work/<repo> before pushing.
Good: Run the validator at the repository root before pushing.
```

Staging that leaks, and staging that does not:

```
Bad:  git add -A
Good: git status --short   # read it
      git add src/config/loader.ts
```

## After a leak

Suspicion is the trigger; confirmation is not a precondition. Report it first: a blocking task,
before any fix, and never quietly. Stop what is still moving — external operations involving the
affected credential, further pushes and edits to the affected destination. Establish what
actually happened after those two moves, not before them.

Revoking a credential, rewriting shared history, and deleting discussion revisions are
irreversible: a human executes them, or the agent does only under explicit approval. Reporting is
never gated on that approval — it comes first, precisely so the approval can be given.

Then read **`references/leak-response.md`** and follow it: revocation for a credential,
containment for information, and the evidence each response owes. Do not improvise the cleanup
from memory — the order matters, and the surfaces that get missed are the ones no search reaches.

## Evidence

Show these outputs rather than asserting nothing leaked.

- **What is staged**: `git status --short` and `git diff --cached --name-only` before committing,
  containing no environment file, key file, or credential path.
- **Content scan**: a search of the staged diff for credential-shaped assignments
  (for example `git diff --cached | rg -n "(api[_-]?key|secret|token|password)\s*[=:]"`),
  reviewed line by line.
- **Ignore coverage**: `git check-ignore -v` naming the rule that excludes each environment or key
  file present in the working tree.
- **Outgoing text is clean**: a search of the staged diff, the commit message, the branch name,
  and any outward-bound text (issue or pull request title and body) against a list of private
  identifiers held outside the working tree, returning no hits.
- **No local paths outgoing**: a search of the staged diff and the commit message for
  absolute-path prefixes, for example
  `git diff --cached | rg -n '/home/|/Users/|/mnt/[a-z]/|[A-Za-z]:\\Users|~/'`, returning no hits
  or only placeholders that are obviously fake. Unlike the check above, this one needs no list of
  identifiers, so it holds the first time it runs.
- **Outgoing identity is clean**: `git log --format='%an <%ae> | %cn <%ce>' <range>` over the
  commits about to leave, showing no address that names a person the destination's audience was
  not already given, and `git log --format=%B <range>` whose trailers point that audience at
  nothing it was never shown.
- **Provenance of derived text is cleared**: for each passage written from a private document, and
  for each block of output from a command whose scope was wider than this repository, its source
  named and the destination's audience compared with the source's — stated and reviewed, not
  searched.
- **Copied material is licensed**: for each copy of third-party material, the source, the
  licence that permits the copy, and the attribution or notice that licence requires — present
  in the artifact, not promised.

After a leak, `references/leak-response.md` names the evidence the response itself owes.
