import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Stack,
  Text,
} from 'cursor/canvas';

interface Ticket {
  key: string;
  domain: string;
  friction: string;
  resolution: string;
  created: string;
  resolved: string;
}

const TICKETS: Ticket[] = [
  { key: 'FIN-10873', domain: 'Tax-inclusive', friction: 'Resort-fee GST wrong on Airbnb res', resolution: 'Bugfix', created: '8 Jun 2026', resolved: '9 Jun 2026' },
  { key: 'FIN-10855', domain: 'Tax-inclusive', friction: 'Balance due = tax value (VRBO)', resolution: 'As Designed', created: '4 Jun 2026', resolved: '10 Jun 2026' },
  { key: 'T3-166405', domain: 'Tax-inclusive', friction: 'Negative accommodation fare, 32+ BDC res', resolution: 'Tech Fix', created: '28 May 2026', resolved: '28 May 2026' },
  { key: 'T3-166678', domain: 'Tax-inclusive', friction: 'Reverse mapping of fees — A$760 gap', resolution: 'Duplicate', created: '1 Jun 2026', resolved: '4 Jun 2026' },
  { key: 'GOLD-9424 / GOLD-9426', domain: 'Payments', friction: 'Duplicate MW charges — same issue', resolution: 'Bugfix', created: '27 May 2026', resolved: '27 May 2026' },
  { key: 'ACC-5894', domain: 'Accounting', friction: 'Cash missing from accounting folio', resolution: 'Tech Fix', created: '22 May 2026', resolved: '27 May 2026' },
  { key: 'FIN-10790', domain: 'Guest invoice', friction: 'Cleaning fee missing from invoice', resolution: 'Tech Fix', created: '21 May 2026', resolved: '2 Jun 2026' },
  { key: 'GOLD-9379 (GOLD-9427)', domain: 'Payments / API', friction: 'Future auth holds via API — resolved via GOLD-9379', resolution: 'Tech Fix', created: '20 May 2026', resolved: '31 May 2026' },
];

export default function HometimeEomMayDashboard(): JSX.Element {
  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Hometime EOM May 2026 — Friction Dashboard</H1>
        <Text tone="secondary">TBC + MRP accounts · May – Jun 2026 · Source: Jira + hometime-internal Slack</Text>
      </Stack>

      <Callout tone="info">
        <Text>
          At the beginning of May there was a major improvement in tax-inclusive issues. However, at EOM of the
          same month we still saw discrepancies caused by specific use cases — reverse mapping of fees, markup on
          fees, and negative accommodation fare — in addition to issues in other domains (duplicate payments, cash
          ledger, guest invoicing).
        </Text>
      </Callout>

      <Stack gap={12}>
        <H2>Critical EOM frictions</H2>
        <Grid columns={3} gap={12}>
          <Card>
            <CardHeader><H3>#1 Tax-inclusive errors</H3></CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text tone="secondary">Negative AF, reverse mapping of fees bug, markup on fees.</Text>
                <Callout tone="success">
                  <Text size="sm" weight="medium">Resolution</Text>
                  <Text size="sm">Closed — Bugfix / Tech Fix / As Designed / Duplicate</Text>
                  <Text size="sm" tone="secondary">FIN-10873 · FIN-10855 · T3-166405 · T3-166678</Text>
                </Callout>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><H3>#2 Duplicate charges</H3></CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text tone="secondary">MW duplicate charges — same issue across GOLD-9424 & GOLD-9426.</Text>
                <Callout tone="success">
                  <Text size="sm" weight="medium">Resolution</Text>
                  <Text size="sm">Closed as Bugfix — GOLD-9424 / GOLD-9426</Text>
                </Callout>
              </Stack>
            </CardBody>
          </Card>
          <Card>
            <CardHeader><H3>#3 Cash ledger gap</H3></CardHeader>
            <CardBody>
              <Stack gap={8}>
                <Text tone="secondary">181 payments unrecognized from ~23 May.</Text>
                <Callout tone="success">
                  <Text size="sm" weight="medium">Resolution</Text>
                  <Text size="sm">Closed as Tech Fix — ACC-5894 · T3-165833</Text>
                </Callout>
              </Stack>
            </CardBody>
          </Card>
        </Grid>
      </Stack>

      <Stack gap={12}>
        <H2>Ticket register</H2>
        <Card>
          <CardBody>
            <Stack gap={14}>
              {TICKETS.map((t) => (
                <Stack key={t.key} gap={4}>
                  <Row gap={8} align="center" wrap>
                    <Text weight="semibold">{t.key}</Text>
                    <Pill tone="neutral">{t.domain}</Pill>
                    <Pill tone="success">Closed</Pill>
                    <Pill tone="neutral">{t.resolution}</Pill>
                  </Row>
                  <Text tone="secondary">{t.friction}</Text>
                  <Text size="sm" tone="tertiary">Created {t.created} · Resolved {t.resolved}</Text>
                </Stack>
              ))}
            </Stack>
          </CardBody>
        </Card>
      </Stack>

      <Text size="sm" tone="tertiary">
        Accounts: TBC 69d5bb4de615023969dc3b34 · MRP 6989bac56844f86a9df2db8c · Generated Jul 13, 2026
      </Text>
    </Stack>
  );
}
