# Synthetic decision material

The migration leaves obsolete configuration entries behind. The project owner must approve a
cleanup scope and a rollout time before the migration can ship.

## Cleanup scope

- Narrow cleanup removes only entries carrying the generator's exact marker. It preserves every
  locally edited entry, including stale ones. It is safe to run unattended but leaves some users
  with obsolete settings that can continue to influence later commands.
- Thorough cleanup removes entries that match the old setting's meaning even when their text was
  locally edited. It produces a clean result, but it can remove an intentional local
  customization when the migration cannot distinguish that customization from a stale entry.

## Rollout time

- Automatic broad rollout reaches everyone immediately and has no per-project confirmation.
- Staged rollout starts with a small group, shows the planned removals, and expands after the
  results are checked. It takes an additional release cycle.

These choices are coupled. Automatic broad rollout is acceptable only with narrow cleanup.
Thorough cleanup requires the staged rollout because its planned removals need inspection.

The migration author recommends thorough cleanup with a staged rollout: obsolete settings stop
affecting later commands, while the preview limits accidental removal. The cost is one additional
release cycle and an approval step for the first group.

## Evidence log

The trial contained 120 synthetic configurations. Narrow cleanup retained 18 obsolete edited
entries and removed no intentional customization. Thorough cleanup removed all obsolete entries
and also selected 2 intentional customizations for removal; both were caught in the staged
preview. The remainder of the log contains per-fixture names and repeats those totals in scan
order. It is useful for audit but not needed in full at the approval point.
