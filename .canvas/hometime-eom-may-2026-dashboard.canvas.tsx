import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Text,
} from 'cursor/canvas';
import { useMemo, useState } from 'react';

type Severity = 'critical' | 'major' | 'moderate' | 'minor';
type ThemeKey = 'all' | 'payments' | 'tax' | 'accounting' | 'invoice' | 'process';

interface Theme {
  key: ThemeKey;
  label: string;
  severity: Severity;
  summary: string;
  eomImpact: string;
  tickets: string[];
}

interface Ticket {
  key: string;
  theme: ThemeKey;
  friction: string;
  status: 'Closed' | 'Open';
  resolution: string;
}

const THEMES: Theme[] = [
  {
    key: 'payments',
    label: 'Duplicate Payment Charges',
    severity: 'critical',
    summary:
      'Guests were charged multiple times through Merchant Warrior — in some cases up to 10×. Guesty sent duplicate API requests; ghost reservations from failed DB saves amplified the problem.',
    eomImpact: 'Payment automations turned off as workaround. Guest cards cancelled/blocked. GOLD-9426 still open.',
    tickets: ['GOLD-9424', 'GOLD-9426'],
  },
  {
    key: 'tax',
    label: 'Tax-Inclusive Calculation Errors',
    severity: 'critical',
    summary:
      'Taxes added instead of extracted, or missing entirely — 51+ reservations across TBC + MRP. Negative AF from disabled feature toggles, bundled-fee bugs, and markup-on-fees + inclusive tax conflicts.',
    eomImpact: 'Blocked customer payouts and owner statements. Bulk recalc of ~2,000 reservations required.',
    tickets: ['T3-166405', 'T3-166678', 'T3-167159', 'T3-167520', 'FIN-10855', 'FIN-10873'],
  },
  {
    key: 'accounting',
    label: 'Cash Ledger Not Auto-Created',
    severity: 'critical',
    summary:
      'Cash entries stopped auto-creating in the Accounting folio from ~23 May. Owner-statement generation-day change to "current month" caused 181 payments (~A$354k) to stay unrecognized.',
    eomImpact: 'Hometime halted reprocessing pending investigation. EOM reconciliation impossible without manual BEAST runs.',
    tickets: ['ACC-5894', 'T3-165833'],
  },
  {
    key: 'invoice',
    label: 'Guest Invoice Discrepancies',
    severity: 'major',
    summary:
      'Guest-facing invoice breakdown did not match folio — Cleaning Fee missing or not bundled into Accommodation Fare when deducted-fees toggle was off.',
    eomImpact: 'Guest-facing documents misleading; code fix deployed but older imported reservations still affected.',
    tickets: ['FIN-10790', 'T3-165745'],
  },
  {
    key: 'process',
    label: 'Slow Response & Escalation Friction',
    severity: 'major',
    summary:
      'Multiple Immediate-priority tickets (opened ~20 May) had no updates after 1–2+ weeks. Harry escalated repeatedly; tickets marked Immediate went unanswered.',
    eomImpact: 'Eroded trust with Hometime team during critical EOM window. VRBO auth-hold API gap (GOLD-9379) open 2+ weeks.',
    tickets: ['GOLD-9379', 'PFR-9532', 'GOLD-9427'],
  },
];

const TICKETS: Ticket[] = [
  { key: 'GOLD-9426', theme: 'payments', friction: 'Ongoing duplicate MW charges — root cause open', status: 'Open', resolution: '—' },
  { key: 'GOLD-9424', theme: 'payments', friction: 'Duplicate charge same timestamp — ghost reservations', status: 'Closed', resolution: 'Bugfix' },
  { key: 'FIN-10873', theme: 'tax', friction: 'Resort-fee GST wrong on 51+ Airbnb res', status: 'Closed', resolution: 'Bugfix' },
  { key: 'FIN-10855', theme: 'tax', friction: 'Balance due = tax value on VRBO res', status: 'Closed', resolution: 'As Designed' },
  { key: 'T3-166405', theme: 'tax', friction: 'Negative AF on 32+ BDC reservations', status: 'Closed', resolution: 'Tech Fix (FT)' },
  { key: 'T3-166678', theme: 'tax', friction: 'Bundled/deducted fees — A$760 folio gap', status: 'Closed', resolution: 'Duplicate → FIN-10848' },
  { key: 'ACC-5894', theme: 'accounting', friction: 'Cash transactions missing from accounting folio', status: 'Closed', resolution: 'Tech Fix' },
  { key: 'FIN-10790', theme: 'invoice', friction: 'Cleaning fee missing from guest invoice', status: 'Closed', resolution: 'Tech Fix' },
  { key: 'GOLD-9379', theme: 'process', friction: 'Future auth holds API not working', status: 'Closed', resolution: 'Tech Fix' },
  { key: 'PFR-9532', theme: 'process', friction: 'No automated VRBO auth-hold flow', status: 'Open', resolution: '—' },
];

function severityTone(s: Severity): 'danger' | 'warning' | 'info' | 'neutral' {
  if (s === 'critical') return 'danger';
  if (s === 'major') return 'warning';
  if (s === 'moderate') return 'info';
  return 'neutral';
}

function severityLabel(s: Severity): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export default function HometimeEomMayDashboard(): JSX.Element {
  const [filter, setFilter] = useState<ThemeKey>('all');

  const filteredTickets = useMemo(
    () => (filter === 'all' ? TICKETS : TICKETS.filter((t) => t.theme === filter)),
    [filter],
  );

  const openCount = TICKETS.filter((t) => t.status === 'Open').length;
  const criticalThemes = THEMES.filter((t) => t.severity === 'critical').length;

  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Hometime EOM May 2026 — Friction Dashboard</H1>
        <Text tone="secondary">
          TBC + MRP accounts · 27 May – 12 Jun 2026 · Source: Jira + hometime-internal Slack
        </Text>
      </Stack>

      <Callout tone="danger">
        <Text weight="semibold">Main EOM friction in one sentence</Text>
        <Text>
          A cascade of financial calculation bugs — tax-inclusive errors, duplicate payment charges, missing
          cash-ledger recognition, and guest-invoice discrepancies — converged on May EOM deadlines, compounded by
          slow resolution on Immediate-priority tickets that eroded trust with the Hometime team.
        </Text>
      </Callout>

      <Grid columns={4} gap={12}>
        <Stat label="Critical themes" value={String(criticalThemes)} tone="danger" />
        <Stat label="Tickets tracked" value={String(TICKETS.length)} />
        <Stat label="Still open" value={String(openCount)} tone={openCount > 0 ? 'warning' : undefined} />
        <Stat label="Res affected (tax)" value="51+" tone="warning" />
      </Grid>

      <Grid columns={3} gap={12}>
        <Stat label="Payments unrecognized" value="181" sublabel="~A$354,400 · May 2026" tone="danger" />
        <Stat label="Bulk recalc needed" value="~2,000" sublabel="Markup + tax-inclusive res" tone="warning" />
        <Stat label="Automations" value="OFF" sublabel="Workaround for duplicate charges" tone="danger" />
      </Grid>

      <Stack gap={12}>
        <H2>Friction themes</H2>
        <Grid columns={2} gap={12}>
          {THEMES.map((theme) => (
            <Card key={theme.key}>
              <CardHeader>
                <Row gap={8} align="center" wrap>
                  <Text weight="semibold">{theme.label}</Text>
                  <Pill tone={severityTone(theme.severity)}>{severityLabel(theme.severity)}</Pill>
                </Row>
              </CardHeader>
              <CardBody>
                <Stack gap={8}>
                  <Text>{theme.summary}</Text>
                  <Callout tone={severityTone(theme.severity)}>
                    <Text size="sm" weight="medium">EOM impact</Text>
                    <Text size="sm">{theme.eomImpact}</Text>
                  </Callout>
                  <Text size="sm" tone="secondary">
                    {theme.tickets.join(' · ')}
                  </Text>
                </Stack>
              </CardBody>
            </Card>
          ))}
        </Grid>
      </Stack>

      <Stack gap={12}>
        <H2>How the frictions connected</H2>
        <Card>
          <CardBody>
            <Stack gap={12}>
              <Row gap={8} align="center" wrap>
                <Pill tone="danger">1. Tax rollout</Pill>
                <Text tone="secondary">→</Text>
                <Pill tone="danger">2. Folio / invoice wrong</Pill>
                <Text tone="secondary">→</Text>
                <Pill tone="danger">3. EOM blocked</Pill>
              </Row>
              <Text tone="secondary">
                Mid-May tax-inclusive enablement triggered negative AF, wrong GST extraction, and bundled-fee display
                bugs. These inflated balance-due and host-payout values, making owner statements and customer payouts
                unreliable.
              </Text>
              <Divider />
              <Row gap={8} align="center" wrap>
                <Pill tone="danger">4. Duplicate charges</Pill>
                <Text tone="secondary">→</Text>
                <Pill tone="warning">5. Automations off</Pill>
                <Text tone="secondary">→</Text>
                <Pill tone="warning">6. Manual ops</Pill>
              </Row>
              <Text tone="secondary">
                Parallel to tax issues, MW duplicate charges forced payment automations off — shifting more work to
                manual processing during the heaviest EOM period.
              </Text>
              <Divider />
              <Row gap={8} align="center" wrap>
                <Pill tone="danger">7. Cash ledger gap</Pill>
                <Text tone="secondary">→</Text>
                <Pill tone="danger">8. Reconciliation halt</Pill>
              </Row>
              <Text tone="secondary">
                From ~23 May, cash journal entries stopped auto-creating (generation-day config change). Hometime
                paused reservation reprocessing, blocking accounting reconciliation entirely.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Stack>

      <Stack gap={12}>
        <Row gap={8} align="center" wrap>
          <Text weight="semibold">Filter tickets:</Text>
          <Pill tone={filter === 'all' ? 'info' : 'neutral'} onClick={() => setFilter('all')}>
            All
          </Pill>
          {THEMES.map((t) => (
            <Pill
              key={t.key}
              tone={filter === t.key ? 'info' : 'neutral'}
              onClick={() => setFilter(t.key)}
            >
              {t.label}
            </Pill>
          ))}
        </Row>

        <Card>
          <CardHeader>
            <Text weight="semibold">Key tickets — {filteredTickets.length} shown</Text>
          </CardHeader>
          <CardBody>
            <Stack gap={14}>
              {filteredTickets.map((t) => (
                <Stack key={t.key} gap={4}>
                  <Row gap={8} align="center" wrap>
                    <Text weight="semibold">{t.key}</Text>
                    <Pill tone={t.status === 'Open' ? 'warning' : 'success'}>{t.status}</Pill>
                    <Pill tone="neutral">{t.resolution}</Pill>
                  </Row>
                  <Text tone="secondary">{t.friction}</Text>
                  <Divider />
                </Stack>
              ))}
            </Stack>
          </CardBody>
        </Card>
      </Stack>

      <Stack gap={8}>
        <H2>What mattered most for EOM</H2>
        <Grid columns={3} gap={12}>
          <Card>
            <CardHeader><H3>#1 Tax-inclusive bugs</H3></CardHeader>
            <CardBody>
              <Text>
                Biggest volume and blast radius. Wrong taxes → wrong payouts → owner statements delayed.
                Required code fixes plus mass recalculation.
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><H3>#2 Duplicate charges</H3></CardHeader>
            <CardBody>
              <Text>
                Highest guest-facing urgency. Forced automations off and left GOLD-9426 open with no root-cause
                fix through EOM.
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><H3>#3 Cash ledger failure</H3></CardHeader>
            <CardBody>
              <Text>
                Stopped accounting reconciliation cold. 181 unrecognized payments meant EOM could not close
                without manual intervention.
              </Text>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      {openCount > 0 ? (
        <Callout tone="warning">
          <Text weight="semibold">Still open at report time</Text>
          <Text>GOLD-9426 (duplicate charge root cause) · PFR-9532 (VRBO auto auth holds) · GOLD-9427 (bulk auth holds API)</Text>
        </Callout>
      ) : null}

      <Text size="sm" tone="tertiary">
        Accounts: TBC 69d5bb4de615023969dc3b34 · MRP 6989bac56844f86a9df2db8c · Generated Jul 12, 2026
      </Text>
    </Stack>
  );
}
