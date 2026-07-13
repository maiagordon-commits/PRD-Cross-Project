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
  eomImpact?: string;
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
      'Guests charged multiple times through Merchant Warrior (up to 10×). Same root issue across GOLD-9424 & GOLD-9426 — ghost reservations from failed DB saves.',
    eomImpact: 'Closed as Bugfix.',
    tickets: ['GOLD-9424 / GOLD-9426'],
  },
  {
    key: 'tax',
    label: 'Tax-Inclusive Calculation Errors',
    severity: 'critical',
    summary: 'Negative AF, reverse mapping of fees bug, markup on fees across TBC + MRP.',
    tickets: ['T3-166405', 'T3-166678', 'T3-167159', 'T3-167520', 'FIN-10855', 'FIN-10873'],
  },
  {
    key: 'accounting',
    label: 'Cash Ledger Not Auto-Created',
    severity: 'critical',
    summary:
      'Cash entries stopped auto-creating in the Accounting folio from ~23 May. Owner-statement generation-day change caused 181 payments (~A$354k) to stay unrecognized.',
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
    eomImpact: 'Eroded trust with Hometime team during critical EOM window.',
    tickets: ['GOLD-9379'],
  },
];

const TICKETS: Ticket[] = [
  { key: 'GOLD-9424 / GOLD-9426', theme: 'payments', friction: 'Duplicate MW charges — same issue', status: 'Closed', resolution: 'Bugfix' },
  { key: 'FIN-10873', theme: 'tax', friction: 'Resort-fee GST wrong on Airbnb res', status: 'Closed', resolution: 'Bugfix' },
  { key: 'FIN-10855', theme: 'tax', friction: 'Balance due = tax value on VRBO res', status: 'Closed', resolution: 'As Designed' },
  { key: 'T3-166405', theme: 'tax', friction: 'Negative AF on 32+ BDC reservations', status: 'Closed', resolution: 'Tech Fix (FT)' },
  { key: 'T3-166678', theme: 'tax', friction: 'Reverse mapping of fees — A$760 folio gap', status: 'Closed', resolution: 'Duplicate → FIN-10848' },
  { key: 'ACC-5894', theme: 'accounting', friction: 'Cash transactions missing from accounting folio', status: 'Closed', resolution: 'Tech Fix' },
  { key: 'FIN-10790', theme: 'invoice', friction: 'Cleaning fee missing from guest invoice', status: 'Closed', resolution: 'Tech Fix' },
  { key: 'GOLD-9379 (GOLD-9427)', theme: 'process', friction: 'Future auth holds via API — resolved via GOLD-9379', status: 'Closed', resolution: 'Tech Fix' },
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
                  {theme.eomImpact ? (
                    <Callout tone={severityTone(theme.severity)}>
                      <Text size="sm" weight="medium">{theme.key === 'payments' ? 'Resolution' : 'EOM impact'}</Text>
                      <Text size="sm">{theme.eomImpact}</Text>
                    </Callout>
                  ) : null}
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
                Negative AF, reverse mapping of fees bug, and markup on fees drove wrong payouts and delayed owner
                statements. Required code fixes plus mass recalculation.
              </Text>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><H3>#2 Duplicate charges</H3></CardHeader>
            <CardBody>
              <Text>
                Highest guest-facing urgency. GOLD-9424 / GOLD-9426 — same issue, closed as Bugfix.
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

      <Text size="sm" tone="tertiary">
        Accounts: TBC 69d5bb4de615023969dc3b34 · MRP 6989bac56844f86a9df2db8c · Generated Jul 13, 2026
      </Text>
    </Stack>
  );
}
