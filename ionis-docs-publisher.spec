# SUPERSEDED — DO NOT BUILD OR PUBLISH (KI7MT/fleet-ops#183, decided 2026-09-10)
#
# This package exists because the landing publisher's systemd units were hand-placed in
# /etc/systemd/system and owned by nothing. It was always an interim step: one package per site
# does not scale, and the coupling it leaves behind is already visible — landing-update.service
# runs under HAMSTATS' identity and reads /etc/hamstats/env, because that is where a HOST fact
# (CH_HOST) happens to live.
#
# The replacement is ionis-publish: one package for the publishing TIER, carrying every
# publisher unit, the ionis-publish service account and /etc/ionis-publish/env, with each site
# keeping its own repo for content. It is lab-only, so it ships from the private repository
# (KI7MT/fleet-ops#184) rather than Copr.
#
# STATE: never built in Copr. publish-1 runs ionis-docs-publisher 1.0.0 from a LOCAL install, so
# this spec is still the only recipe for something that is currently serving a public website —
# which is why the file stays until ionis-publish replaces it on that host, and only then is
# deleted. Do not build it in the meantime; a Copr build would make a superseded design
# installable by anyone.

%global debug_package %{nil}

Name:           ionis-docs-publisher
Version:        1.0.0
Release:        1%{?dist}
Summary:        Systemd units for the IONIS docs landing-page publisher

License:        GPL-3.0-or-later
URL:            https://github.com/IONIS-AI/ionis-docs
Source0:        %{url}/archive/refs/tags/publisher-v%{version}.tar.gz#/%{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  systemd-rpm-macros
Requires:       git
Requires:       systemd

%description
Timer and service that refresh the ionis-docs landing page numbers from ClickHouse and push
the result.

SHIPS UNITS, NOT CODE — the same split as ionis-hamstats. The unit was previously hand-written
into /etc/systemd/system on the 9975, owned by no package and no playbook, so upgrades never
touched it and nothing recorded what was deployed. The scripts run from the git checkout at
/srv/ionis/repos/ionis-docs, which is where they are also edited.

It runs on publish-1, the rendering tier, rather than on the control node. It is a renderer:
it reads ClickHouse and writes a page. The 9975 carries ClickHouse, the GPU, every ingester
and the Vault anchors for bob and turing, and cannot take a reboot without ingester data loss.

%prep
%autosetup -n ionis-docs-publisher-v%{version}

%build

%install
install -d -m 0755 %{buildroot}%{_unitdir}
install -p -m 0644 systemd/landing-update.service %{buildroot}%{_unitdir}/
install -p -m 0644 systemd/landing-update.timer   %{buildroot}%{_unitdir}/

%post
%systemd_post landing-update.timer
if [ $1 -eq 1 ]; then
cat <<'EOM'
------------------------------------------------------------
 ionis-docs-publisher installed.

 Requires: /srv/ionis/repos/ionis-docs checked out and pushable by the service user,
 and the service virtualenv with clickhouse-connect.

 If /etc/systemd/system/landing-update.service still exists it is the old hand-placed
 unit and SHADOWS this one. Remove it, then: systemctl daemon-reload
------------------------------------------------------------
EOM
fi

%preun
%systemd_preun landing-update.timer

%postun
%systemd_postun_with_restart landing-update.timer

%files
%{_unitdir}/landing-update.service
%{_unitdir}/landing-update.timer

%changelog
* Wed Sep 09 2026 Greg Beam <ki7mt@yahoo.com> - 1.0.0-1
- First packaged release. The unit was hand-written into /etc/systemd/system, owned by no
  package and no playbook.
- Moves the landing-page publisher off the 9975 onto publish-1. It is a renderer, not an
  ingester; the second of the two that were running on the control node.
- publish_landing.sh honours CH_HOST. update_landing.py defaults --ch-host to localhost,
  which is correct only where ClickHouse is local; publish-1 reads it over the 10.60.2 DAC.
