import {
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
  Stat,
  Table,
  Text,
} from 'cursor/canvas';

type GapRow = {
  workflow: string;
  gaps: number;
  evals: string;
  attention: string;
  resources: string;
  pm: string;
};

/** Gap matrix from Workflow Registry Gaps canvas (2026-07-15), with PM owners from #agent-hub-june-20-agents. */
const ROWS: GapRow[] = [
  {
    workflow: 'owner-health',
    gaps: 3,
    evals: 'absent',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Gil Sheffi',
  },
  {
    workflow: 'reservation-readiness-surfacer',
    gaps: 3,
    evals: 'empty list',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Yarin Lerer',
  },
  {
    workflow: 'bookingcom-collect-deposit',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Eliana Ferdman',
  },
  {
    workflow: 'channel-collect-deposit',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Eliana Ferdman',
  },
  {
    workflow: 'checkout-balance-collection',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Dina Kats',
  },
  {
    workflow: 'daily-task-coverage-board',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Yarin Lerer',
  },
  {
    workflow: 'expedia-collect-deposit',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Eliana Ferdman',
  },
  {
    workflow: 'saved-replies-review',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Lital Herman',
  },
  {
    workflow: 'weekly-operations-brief',
    gaps: 2,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'absent',
    pm: 'Gur Geron',
  },
  {
    workflow: 'advanced-deposit-clearance',
    gaps: 1,
    evals: 'OK',
    attention: 'OK',
    resources: 'absent',
    pm: 'Rotem Meir',
  },
  {
    workflow: 'airbnb-listing-quality-audit',
    gaps: 1,
    evals: 'OK',
    attention: 'OK',
    resources: 'absent',
    pm: 'Javier Ibarz',
  },
  {
    workflow: 'calendar-block-monitor',
    gaps: 1,
    evals: 'OK',
    attention: 'OK',
    resources: 'absent',
    pm: 'Yarin Lerer',
  },
  {
    workflow: 'checkin-readiness',
    gaps: 1,
    evals: 'empty list',
    attention: 'OK',
    resources: 'OK',
    pm: 'Gil Sheffi',
  },
  {
    workflow: 'city-tax-config-audit',
    gaps: 1,
    evals: 'OK',
    attention: 'OK',
    resources: 'absent',
    pm: 'Alex Fischer Birnbaum',
  },
  {
    workflow: 'cleaning-schedule-conflict-detector',
    gaps: 1,
    evals: 'OK',
    attention: 'OK',
    resources: 'absent',
    pm: 'Yarin Lerer',
  },
  {
    workflow: 'stay-status-reconciler',
    gaps: 1,
    evals: 'OK',
    attention: 'criteria_prompt empty',
    resources: 'OK',
    pm: 'Yarin Lerer',
  },
];

function gapTone(gaps: number): 'danger' | 'warning' | 'info' {
  if (gaps >= 3) return 'danger';
  if (gaps === 2) return 'warning';
  return 'info';
}

function fieldTone(value: string): 'success' | 'warning' | 'danger' | 'neutral' {
  if (value === 'OK') return 'success';
  if (value === 'absent' || value === 'empty list') return 'danger';
  if (value.includes('empty')) return 'warning';
  return 'neutral';
}

export default function WorkflowRegistryGapsPm(): JSX.Element {
  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Workflow Registry Gaps + PM</H1>
        <Text tone="secondary">
          Gap matrix from shared canvas (n=39 workflows) · sorted by gaps · PM column added from Agent Hub ownership
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Stat value="16" label="Workflows with gaps" />
        <Stat value="3" label="Missing evals" />
        <Stat value="10" label="Empty attention criteria" />
        <Stat value="14" label="Missing resource_declarations" />
      </Grid>

      <Card>
        <CardHeader>
          <H2>Critical: all three missing (2)</H2>
        </CardHeader>
        <CardBody>
          <Row gap={8} wrap>
            <Pill tone="danger">owner-health · Gil Sheffi</Pill>
            <Pill tone="danger">reservation-readiness-surfacer · Yarin Lerer</Pill>
          </Row>
        </CardBody>
      </Card>

      <Stack gap={12}>
        <H2>Gap matrix — workflows with missing fields</H2>
        <Text tone="secondary" size="sm">
          Empty attention = attention_gate.criteria_prompt present but blank. Source: workflow.yaml audit + #agent-hub-june-20-agents ownership.
        </Text>
        <Table
          headers={['Workflow', 'Gaps', 'evals', 'attention criteria', 'resource_declarations', 'PM']}
          rows={ROWS.map((r) => [
            r.workflow,
            <Pill key={`${r.workflow}-g`} tone={gapTone(r.gaps)}>{String(r.gaps)}</Pill>,
            <Pill key={`${r.workflow}-e`} tone={fieldTone(r.evals)}>{r.evals}</Pill>,
            <Pill key={`${r.workflow}-a`} tone={fieldTone(r.attention)}>{r.attention}</Pill>,
            <Pill key={`${r.workflow}-r`} tone={fieldTone(r.resources)}>{r.resources}</Pill>,
            r.pm,
          ])}
        />
      </Stack>

      <Stack gap={8}>
        <H3>PM coverage notes</H3>
        <Text size="sm" tone="secondary">
          channel-collect-deposit mapped to Eliana Ferdman (Airbnb / channel collect-deposit split with bookingcom + expedia).
          airbnb-listing-quality-audit owned by Javier Ibarz (Distribution).
        </Text>
        <Text size="sm" tone="tertiary">
          Source canvas: canvas-9wakIoT1VAVW5-WtNx2NpHEv · Generated 2026-07-16
        </Text>
      </Stack>
    </Stack>
  );
}
