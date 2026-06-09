# Saturn Research Data Storage

## What is Saturn?

Saturn is UT Dallas's implementation of a Dell Isilon/PowerScale enterprise-grade NAS (network-attached storage) system, offered through the Office of Research and Innovation. It provides centralized, redundant, secure storage for **research data and backups**.

Saturn is a campus-wide service — it is **not** one of Juno's own storage tiers (Home, Work, Group, Scratch). Instead, it is a separate, larger, persistent store that can sit alongside the cluster and connect to your HPC workflows. For Juno's native filesystems and how they are sized, see [Storage and Data Transfer](storage.md#storage-systems-on-juno).

## How Saturn fits with Juno

Juno's built-in storage is deliberately sized for HPC work: Home is 50 GB, Work is 1 TB, and Group is 1 TB or more. The recommended workflow is to compute in [Scratch](scratch-space.md) and keep results in the backed-up Io tiers (`~`, `~/work`, `/groups`). See the [Storage Selection Guide](storage.md#storage-selection-guide) for which tier suits which data.

Saturn becomes useful when those tiers are not enough:

- **More persistent capacity than Work or Group provide** — when a group's active datasets outgrow a 1 TB Group quota and an [increase](storage.md#quota-management) is not sufficient.
- **A backup destination outside the cluster** — Scratch is never backed up, and even backed-up tiers should not be your only copy of critical data (see [Backup Strategy](storage.md#backup-strategy)).
- **Shared storage reachable from both the cluster and lab workstations** — Saturn mounts over SMB/NFS, so the same data can be accessed from Juno and from desktops in the lab.

For data that exceeds roughly 40 TB, **Titan Condo Storage** is the recommended alternative to Saturn.

## Capacity tiers

The Office of Research and Innovation offers three allocation levels:

| Tier | Capacity | Requirements |
|------|----------|--------------|
| Starter | Up to 10 TB | No additional requirements |
| Extended | Up to 20 TB | Data above 10 TB should be current/active (generally under one year old) |
| High Activity | Up to 30 TB | Requires demonstrated need, justification, and approval |

For needs beyond ~40 TB, consider Titan Condo Storage instead.

## Eligibility and access

- A Saturn share must be **sponsored by an active UTD research faculty member** (the share owner).
- Access requires a valid **NetID** and a connection to the **UTD campus network** (on-site or over [VPN](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/Service/167/PaloAlto-GlobalProtect-VPN)).
- The owner can grant access to approved UTD-affiliated staff and students for collaboration.

### Access methods

| Platform | Protocol | Path |
|----------|----------|------|
| Windows | SMB | `\\saturn\ShareName` |
| macOS | SMB | `smb://saturn.utdallas.edu/ShareName` |
| Linux | SMB or NFS | NFS available on request |

!!! tip "Connecting Saturn to HPC workflows"

    To use a Saturn share directly from Juno workflows, request **NFS** access. If a share is not mounted on the cluster, you can still move data between Saturn and Juno using the standard [data transfer methods](storage.md#data-transfer-methods) (`scp`, `rsync`, SFTP).

## Requesting Saturn

Saturn is requested and managed through the UTD service portal, not through Juno directly:

- **Request a share, manage access, or change ownership**: [Saturn Research Data Storage service](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/Service/411/Saturn-Research-Data-Storage)
- **Book a consultation**: [UTD.link/SATURNconsult](https://UTD.link/SATURNconsult)

The service page above is the authoritative source for current tiers, pricing, and policy — refer to it for anything not covered here.

## Next Steps

- [Storage and Data Transfer →](storage.md)
- [Scratch Space →](scratch-space.md)
- [Request group storage upgrade →](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/ServiceOffering/1212/Increase-Storage-Allocation/Request)

## Need Help?

- **Storage and data questions**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)
- **Saturn-specific requests**: Use the [Saturn service portal](https://atlas.utdallas.edu/TDClient/30/Portal/Requests/Service/411/Saturn-Research-Data-Storage)
