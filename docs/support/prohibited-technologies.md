# Prohibited Technologies & Covered Applications

!!! info "This page is a summary"
    This page summarizes the State of Texas prohibited-technology policy for Juno users.
    The official lists are maintained by the Texas Department of Information Resources
    (DIR) and may change more often than this page is updated. **The original source
    always takes precedence** over anything here — when in doubt, confirm against the
    [authoritative DIR list](#authoritative-source) before installing unfamiliar software.

## Overview

Juno is a state-owned system operated by UT Dallas. Under Texas law, certain foreign-owned applications and hardware are prohibited from use on state-owned devices and networks. As a Juno user, **you are responsible for not installing, running, or storing prohibited technologies on the cluster**, including in your home, work, scratch, or group directories.

This requirement comes from Governor Abbott's executive orders and **Senate Bill 1893 (88th Texas Legislature)**, and applies to all state and local governmental entities as defined by Texas Government Code Chapter 620.

!!! warning "This policy is binding on Juno"

    The cluster's login and compute nodes are state-owned devices on a state network. Installing or running any of the prohibited software below — or connecting prohibited hardware to access Juno — is a violation of state policy and UT Dallas rules, and may result in removal of the software and loss of access.

## Covered Applications

The following are designated **Covered Applications** and must not be installed or run on Juno:

- **TikTok** — and any successor application developed by ByteDance Ltd.
- **Lemon8**
- **RedNote**

## Prohibited Software, Applications & Developers

Over 30 entities are prohibited, including their subsidiaries and affiliates. Notable examples:

| Category | Examples |
|----------|----------|
| Social / messaging | TikTok, WeChat (Tencent), Lemon8, RedNote |
| Parent developers | ByteDance Ltd., Tencent Holdings, Alibaba, Baidu |
| AI developers | DeepSeek, Baichuan, Moonshot AI, MiniMax, StepFun |
| E-commerce | Temu (PDD Holdings), Shein |
| Financial apps | Alipay, QQ Wallet, Moomoo, WeBull, Tiger Brokers |
| Other software | CamScanner, iFlytek, Kaspersky, SHAREit, WPS Office, Xiaomi |

!!! note "Relevant to HPC workloads"

    Some prohibited developers — such as **DeepSeek**, **Baichuan**, **Moonshot AI**, **MiniMax**, and **iFlytek** — distribute AI/ML models and tooling. Do not download, install, or run these models or their software on Juno, even for research, unless an approved exception is in place (see below).

## Prohibited Hardware, Equipment & Manufacturers

Restricted manufacturers (including subsidiaries and affiliates) include:

- **Huawei Technologies**
- **DJI** (drones)
- **Hikvision**, **Dahua Technology** (cameras/surveillance)
- **TP-Link**, **ZTE Corporation** (networking)
- **Xiaomi**, **TCL Technology**, **Hisense**
- **CATL** (batteries), **Hytera** (telecommunications)

Do not use prohibited hardware to connect to or access Juno from state-managed devices or networks.

## Exceptions

Limited exceptions may be approved **only by an agency head** (this authority cannot be delegated) for:

- Law enforcement investigations
- Developing or implementing information security measures
- Other legitimate uses

Approved exceptions must be reported to the Office of the Governor and the Texas Department of Information Resources (DIR). If you believe your research genuinely requires a prohibited technology, **do not install it yourself** — contact UT Dallas IT Security first to determine whether a documented exception is possible.

## Questions & Reporting

- **Whether something is prohibited / requesting an exception**: [issuport@utdallas.edu](mailto:issuport@utdallas.edu)
- **HPC-specific guidance**: [circ-assist@utdallas.edu](mailto:circ-assist@utdallas.edu)

## Authoritative Source

The official, continually updated lists are maintained by the Texas Department of Information Resources. Always confirm against the source before installing unfamiliar software:

- **DIR — Covered Applications & Prohibited Technologies**: [dir.texas.gov/information-security/covered-applications-and-prohibited-technologies](https://dir.texas.gov/information-security/covered-applications-and-prohibited-technologies)

*Lists summarized here reflect DIR updates as of February 2026 and are subject to change. The DIR page is authoritative.*
