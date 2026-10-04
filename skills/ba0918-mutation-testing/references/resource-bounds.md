# Resource bounds

How to put a mutation run inside the boundary the rules in `SKILL.md` require: memory and CPU
capped for the whole process tree, lower priority on a shared machine, and an outer cap on a
virtualised environment. The numbers below are starting values, not rules; size them to the
machine.

## Linux with systemd (workstation)

Run the tool as a transient user service. A service accepts both resource limits and priority
settings, and every process the tool starts stays inside it.

```bash
systemd-run --user --wait --collect --pipe --same-dir \
  -p MemoryMax=12G -p MemorySwapMax=0 \
  -p CPUQuota=400% \
  -p Nice=19 -p IOSchedulingClass=idle \
  --setenv=PATH="$PATH" --setenv=HOME="$HOME" \
  -- <mutation tool command>
```

- `CPUQuota` is a percentage of one core: `400%` is four cores' worth. Leave enough cores for the
  rest of the machine — about half is a reasonable start.
- `MemorySwapMax=0` makes a runaway mutant hit the memory cap instead of pushing the machine into
  swap.
- A service does not inherit the caller's environment. Pass every variable the tool needs with
  `--setenv`.
- Give the unit a name unique to the run (`--unit=<name>-$$`) when an interrupted script must stop
  it: killing the `systemd-run` client leaves the service running.

The limits only take effect when the user manager has the controllers delegated. Check before
relying on them; a missing controller is ignored without an error:

```bash
cat "/sys/fs/cgroup/user.slice/user-$(id -u).slice/user@$(id -u).service/cgroup.controllers"
# must list: cpu memory
```

## Reaping leftovers

A mutant that times out can leave child processes — a server, a watcher — that the tool does not
kill. Give each run its own temporary directory, so the mutated binaries of this run can be told
apart from other runs, and kill processes started from it that outlive the per-mutant time limit.
Match on the start of the path: a looser pattern kills other runs' processes or the watcher
itself.

## WSL

The boundary inside WSL protects WSL. To protect the Windows host, also cap WSL as a whole in
`%UserProfile%\.wslconfig`:

```ini
[wsl2]
memory=16GB
processors=8
swap=0
```

Apply it with `wsl --shutdown` from Windows; it does not take effect on a running instance.
`systemd-run --user` inside WSL needs systemd enabled in `/etc/wsl.conf`:

```ini
[boot]
systemd=true
```

A VM is the same: cap the VM's memory and virtual CPUs in its host settings, and bound the run
inside it.

## Containers

Where the run already happens in a container, the container is the boundary:

```bash
docker run --rm --memory=12g --memory-swap=12g --cpus=4 --pids-limit=4096 \
  -v "$PWD":/work -w /work <image> <mutation tool command>
```

`--memory-swap` equal to `--memory` disables swap for the container.

## CI runners

A hosted runner is a machine of its own, so priority matters less, but the memory cap still
does: without it a runaway mutant takes the runner down, and the job reports a lost runner
("the runner has received a shutdown signal") instead of a result.

A GitHub-hosted Linux runner has systemd as the system manager and passwordless `sudo`, but no
user manager, so `systemd-run --user` fails there. Start a scope through the system manager and
drop back to the runner's user:

```bash
sudo --preserve-env systemd-run --scope --quiet \
  --uid="$(id -un)" --gid="$(id -gn)" \
  -p MemoryMax=12G -p MemorySwapMax=0 -p CPUQuota=200% \
  -- env "PATH=$PATH" <mutation tool command>
```

- A scope runs the command from the caller, so it keeps the caller's environment and working
  directory. `sudo` resets `PATH`, hence `env "PATH=$PATH"`, which the shell expands before
  `sudo` runs.
- A scope does not accept `Nice=` or `IOSchedulingClass=`; prefix the command with
  `nice -n 19 ionice -c 3` where priority matters.
- Size both caps to the runner: keep memory below its available memory and CPU quota below its
  total CPU capacity, leaving room for the runner agent itself. `200%` is two cores' worth;
  reduce it on a two-core runner, or adjust it for a larger runner.

Running the job in a container (`docker run` as above, or the platform's job container with
resource options) is the alternative where `sudo` is not available.

## Evidence

From inside the run, show the cgroup and its limits, for example as the first step of the
command:

```bash
cat /proc/self/cgroup
cat "/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)/memory.max"
cat "/sys/fs/cgroup$(cut -d: -f3 /proc/self/cgroup)/cpu.max"
```

`max` in `memory.max` means no limit is applied.
