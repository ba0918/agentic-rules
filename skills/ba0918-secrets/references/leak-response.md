# Leak Response

Read this when something protected has already reached somewhere it should not: a credential, or
information — an internal name, a confidential passage, an unlicensed copy.

Two paths follow. Which one applies is decided by a single question: **can the exposed thing be
revoked?** A credential can — it has a provider that can kill it, and revocation is the action
that actually stops the leak. Information cannot: a name, a document, a copyrighted text has no
off switch, so containment takes revocation's place and is never complete.

## Before either path

Reporting comes first, always, and is never gated on approval — it is what makes the exposure
known to the people who own it, so containment does not depend on one session quietly handling
it.

Three actions are gated, and only these three: revoking a credential, rewriting shared history,
and deleting discussion revisions. Each is irreversible, so a human executes it, or the agent
does only under explicit approval — and holding pushes while a response is "agreed" is not that
approval. Everything else proceeds at once: determining the exposure and recording what allowed
it through are reversible, and an active incident is understood sooner for them.

## When the leak is a credential

1. **Revoke and rotate** the credential at its provider, before any cleanup. Press for immediate
   revocation; while approval is pending, stop external operations that involve the affected
   credential.
2. **Determine the exposure**: which commits, branches, remotes, logs, CI runs, and transcripts
   contain it. Assume anything pushed has been fetched.
3. **Remove it from history** and force-update the affected refs, coordinating with anyone who
   has a clone.
4. **Prevent recurrence**: add the path to the ignore file and record what allowed it through.

## When the leak is information, not a credential

There is nothing to revoke, so containment replaces revocation.

1. **Scope the pause**: state what leaked and where, and hold further pushes and edits to the
   affected destination until the response is approved.
2. **Name the leaked material, then determine its exposure.** What leaked may be an identifier,
   or a passage or snippet that carries no stable name — a paraphrased document, copied code. An
   identifier is located by searching for it. Material without one is located from its
   provenance: the source it came from, and the change sets and discussions where it was
   written. Either way, trace it across every surface it reached, not just file content:
   - commits, including ones made unreachable, since a force-pushed commit can remain fetchable
     by its hash until garbage collection
   - branch and tag names
   - issue and pull request titles, bodies, comments and review comments, **and their edit
     histories**
   - forks, clones, mirrors, CI logs
3. **Contain** each surface found, since none of them is corrected by fixing another:
   - **History**: rewrite every affected commit, not only the tip — amending the tip leaves the
     original commit in the ancestry of its replacement, still reachable through the ref — then
     force-update the affected refs, coordinating with anyone who has a clone.
   - **Ref names**: rename or delete a branch or tag whose name carries the leaked material;
     updating what a ref points at never changes the ref's own name.
   - **Discussion text**: edit or delete the affected titles, bodies, comments and review
     comments, then delete the superseded revisions where the platform allows it.
   - **Beyond your reach**: platform support can delete revisions the platform still holds, and
     will say what it deleted; it reaches nothing already fetched into a clone, fork, mirror,
     notification or cache. Ask, then record what support confirmed — never report a purge.
   - For third-party material, removal plus resolving the licence question.
4. **Prevent recurrence**: record what allowed it through, and add the check that will catch a
   repeat. An identifier goes on a list that outgoing text is searched against. Material with no
   identifier has no search term to represent it, so the source goes on record instead: anything
   derived from it gets the provenance check before it goes out. Keep such a list outside the
   working tree, or excluded by the repository's local-only exclude file — untracked is not
   enough, because one bulk staging commits the very identifiers the list exists to catch.

## Evidence of the response

- **History is clean**: `git log --all --full-history -- <path>` for each credential path,
  returning no commits.
- **Revocation**: the provider's confirmation that the old credential is inactive, dated after
  the exposure.
- **Containment is accounted for**: every surface in the exposure inventory carries a stated
  outcome, with no blanks. The surfaces you control return no hits — a content search across all
  refs and their full history, the list of ref names, and a re-read of the affected titles,
  bodies, comments and their edit histories on the platform; where the material has no
  searchable form, those surfaces are re-read rather than searched. The surfaces beyond reach —
  fetched clones, forks, mirrors, notifications, caches — are listed as unresolved, together
  with whatever platform support confirmed it deleted. Each surface is accounted for on its own:
  cleaning one never clears another, and a cleanup that was not re-checked is not containment.
