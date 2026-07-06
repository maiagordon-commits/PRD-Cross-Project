#!/usr/bin/env python3
"""Build an account x agent activation matrix from an agent-level activation export.

Input: a CSV with (at least) these columns:
    Account ID, Account Name, Package, Segment, Active paying account, HQ type,
    Agent Category, Agent Name, Agent Active

Output (written to --outdir, default: exports/):
    <base>.xlsx  - styled workbook (Activation Matrix, Raw Data, Legend & Notes)
    <base>.csv   - plain grid
    <base>_preview.png - preview image

Cells: V = agent active, OFF = agent added but deactivated, blank = not added.

Usage:
    python3 scripts/build_activation_matrix.py INPUT.csv [--label 2026-07-06] [--outdir exports]

Designed to be run every morning on the latest export.
"""
import argparse
import csv
import re
from datetime import datetime, date
from pathlib import Path

import xlsxwriter
from PIL import Image, ImageDraw, ImageFont

CAT_ORDER = ['OPERATIONS', 'COMMUNICATIONS', 'FINANCE', 'ACCOUNTING', 'OWNER_RELATIONS', 'DISTRIBUTION']
CAT_COLORS = {
    'OPERATIONS': '#4F46E5', 'COMMUNICATIONS': '#0EA5A4', 'FINANCE': '#D97706',
    'ACCOUNTING': '#7C3AED', 'OWNER_RELATIONS': '#DB2777', 'DISTRIBUTION': '#0284C7', 'OTHER': '#64748B',
}
CAT_RGB = {
    'OPERATIONS': (79, 70, 229), 'COMMUNICATIONS': (14, 165, 164), 'FINANCE': (217, 119, 6),
    'ACCOUNTING': (124, 58, 237), 'OWNER_RELATIONS': (219, 39, 119), 'DISTRIBUTION': (2, 132, 199), 'OTHER': (100, 116, 139),
}
DATE_FMT = "%b %d, %Y, %I:%M:%S %p"


def parse_dt(s):
    s = (s or '').strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, DATE_FMT)
    except ValueError:
        return None


def load(input_path):
    rows = list(csv.DictReader(Path(input_path).open(encoding='utf-8')))
    required = {'Account ID', 'Account Name', 'Agent Name', 'Agent Active', 'Agent Category'}
    missing = required - set(rows[0].keys())
    if missing:
        raise SystemExit(
            f"Input is missing required columns: {sorted(missing)}.\n"
            f"Found columns: {list(rows[0].keys())}\n"
            "This tool needs the AGENT-LEVEL export (one row per account+agent with an 'Agent Name' column)."
        )
    return rows


def build_model(rows):
    accounts = {}            # id -> meta, preserving first-seen order (newest first in export)
    order = []
    agent_cat = {}
    status = {}              # (acct_id, agent) -> 'active' | 'inactive'
    for r in rows:
        aid = r['Account ID'].strip()
        name = r['Account Name'].strip()
        agent = r['Agent Name'].strip()
        cat = (r.get('Agent Category') or 'OTHER').strip() or 'OTHER'
        active = (r.get('Agent Active') or '').strip().lower() == 'true'
        if aid not in accounts:
            accounts[aid] = {
                'name': name,
                'segment': (r.get('Segment') or '').strip(),
                'package': (r.get('Package') or '').strip(),
                'paying': (r.get('Active paying account') or '').strip(),
                'hq': (r.get('HQ type') or '').strip(),
            }
            order.append(aid)
        agent_cat[agent] = cat
        key = (aid, agent)
        if active:
            status[key] = 'active'
        elif key not in status:
            status[key] = 'inactive'
    # ordered agent columns: by category order, alphabetical within category (stable day to day)
    agent_cols = []
    cats_present = [c for c in CAT_ORDER if c in set(agent_cat.values())]
    cats_present += [c for c in sorted(set(agent_cat.values())) if c not in cats_present]
    for c in cats_present:
        for a in sorted(x for x in agent_cat if agent_cat[x] == c):
            agent_cols.append((c, a))
    return accounts, order, agent_cols, status


def account_active_today(aid, agent_cols, status):
    return any(status.get((aid, a)) == 'active' for _, a in agent_cols)


def write_xlsx(path, accounts, order, agent_cols, status, label, src_name):
    wb = xlsxwriter.Workbook(str(path))
    ws = wb.add_worksheet('Activation Matrix')
    f_title = wb.add_format({'bold': True, 'font_size': 15, 'font_color': '#1E293B'})
    f_sub = wb.add_format({'font_size': 9, 'font_color': '#64748B'})

    def f_cat(c):
        return wb.add_format({'bold': True, 'font_size': 8, 'font_color': 'white', 'bg_color': CAT_COLORS.get(c, '#64748B'),
                              'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})
    f_agent = wb.add_format({'bold': True, 'font_size': 8, 'font_color': '#1E293B', 'align': 'center', 'valign': 'bottom',
                             'rotation': 90, 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F1F5F9'})
    f_hdr = wb.add_format({'bold': True, 'font_size': 9, 'font_color': 'white', 'bg_color': '#232A3C', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})
    f_hdr_c = wb.add_format({'bold': True, 'font_size': 9, 'font_color': 'white', 'bg_color': '#232A3C', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})

    def acct_fmt(alt):
        return wb.add_format({'bold': True, 'font_size': 9, 'font_color': '#1E293B', 'align': 'left', 'valign': 'vcenter',
                              'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    def meta_fmt(alt):
        return wb.add_format({'font_size': 8, 'font_color': '#475569', 'align': 'center', 'valign': 'vcenter',
                              'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    def id_fmt(alt):
        return wb.add_format({'font_size': 8, 'font_color': '#94A3B8', 'align': 'left', 'valign': 'vcenter',
                              'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF', 'font_name': 'Consolas'})

    def blank_fmt(alt):
        return wb.add_format({'border': 1, 'border_color': '#EEF2F7', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    f_v = wb.add_format({'bold': True, 'font_size': 10, 'font_color': '#166534', 'bg_color': '#DCFCE7', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
    f_off = wb.add_format({'font_size': 9, 'font_color': '#B91C1C', 'bg_color': '#FEE2E2', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
    f_count = wb.add_format({'bold': True, 'font_size': 9, 'font_color': '#1E293B', 'bg_color': '#EEF2FF', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})

    INFO = ['Account ID', 'Account Name', 'Segment', 'Package', 'CSM', 'Interview Date', 'Active today']
    first_agent = len(INFO)
    last_agent = first_agent + len(agent_cols) - 1
    count_col = last_agent + 1

    ws.write(0, 0, 'Agents Activation Tracking — Account x Agents', f_title)
    ws.write(1, 0, f'Snapshot: {label}  ·  source: {src_name}  ·  {len(order)} accounts · {len(agent_cols)} agents  ·  '
                   'V = activated, OFF = added but deactivated, blank = not added. CSM & Interview Date left blank for manual entry.', f_sub)

    CAT_ROW, AGENT_ROW, DATA = 3, 4, 5
    for i, name in enumerate(INFO):
        ws.merge_range(CAT_ROW, i, AGENT_ROW, i, name, f_hdr if i in (0, 1) else f_hdr_c)
    idx = 0
    while idx < len(agent_cols):
        cat = agent_cols[idx][0]
        j = idx
        while j < len(agent_cols) and agent_cols[j][0] == cat:
            j += 1
        lbl = cat.replace('_', ' ').title()
        if j - idx == 1:
            ws.write(CAT_ROW, first_agent + idx, lbl, f_cat(cat))
        else:
            ws.merge_range(CAT_ROW, first_agent + idx, CAT_ROW, first_agent + j - 1, lbl, f_cat(cat))
        idx = j
    for k, (_, agent) in enumerate(agent_cols):
        ws.write(AGENT_ROW, first_agent + k, agent, f_agent)
    ws.merge_range(CAT_ROW, count_col, AGENT_ROW, count_col, '# Active', f_hdr_c)

    for ri, aid in enumerate(order):
        row = DATA + ri
        alt = ri % 2 == 1
        meta = accounts[aid]
        ws.write(row, 0, aid, id_fmt(alt))
        ws.write(row, 1, meta['name'], acct_fmt(alt))
        ws.write(row, 2, meta['segment'], meta_fmt(alt))
        ws.write(row, 3, meta['package'], meta_fmt(alt))
        ws.write(row, 4, '', meta_fmt(alt))
        ws.write(row, 5, '', meta_fmt(alt))
        ws.write(row, 6, 'true' if account_active_today(aid, agent_cols, status) else 'false', meta_fmt(alt))
        cnt = 0
        for k, (_, agent) in enumerate(agent_cols):
            st = status.get((aid, agent))
            c = first_agent + k
            if st == 'active':
                ws.write(row, c, 'V', f_v); cnt += 1
            elif st == 'inactive':
                ws.write(row, c, 'OFF', f_off)
            else:
                ws.write_blank(row, c, None, blank_fmt(alt))
        ws.write(row, count_col, cnt, f_count)

    ws.set_column(0, 0, 20); ws.set_column(1, 1, 26); ws.set_column(2, 3, 9)
    ws.set_column(4, 4, 13); ws.set_column(5, 5, 12); ws.set_column(6, 6, 9)
    ws.set_column(first_agent, last_agent, 4.2); ws.set_column(count_col, count_col, 8)
    ws.set_row(AGENT_ROW, 150)
    ws.freeze_panes(DATA, 2)
    ws.set_zoom(90)

    wb.close()


def write_csv(path, accounts, order, agent_cols, status):
    INFO = ['Account ID', 'Account Name', 'Segment', 'Package', 'CSM', 'Interview Date', 'Active today']
    with Path(path).open('w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(INFO + [a for _, a in agent_cols] + ['# Active'])
        for aid in order:
            meta = accounts[aid]
            line = [aid, meta['name'], meta['segment'], meta['package'], '', '',
                    'true' if account_active_today(aid, agent_cols, status) else 'false']
            cnt = 0
            for _, agent in agent_cols:
                st = status.get((aid, agent))
                if st == 'active':
                    line.append('V'); cnt += 1
                elif st == 'inactive':
                    line.append('OFF')
                else:
                    line.append('')
            line.append(cnt)
            w.writerow(line)


def _font(sz, bold=False):
    p = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
    try:
        return ImageFont.truetype(p, sz)
    except OSError:
        return ImageFont.load_default()


def write_preview(path, accounts, order, agent_cols, status, label):
    id_w, name_w, seg_w, today_w, cell_w, count_w = 155, 190, 64, 52, 30, 42
    head_h, row_h, top, left = 150, 25, 72, 10
    n = len(agent_cols)
    W = left + id_w + name_w + seg_w + today_w + n * cell_w + count_w + 16
    H = top + head_h + len(order) * row_h + 24
    img = Image.new('RGB', (W, H), 'white')
    d = ImageDraw.Draw(img)
    f_t, f_s, f_sm, f_c, f_a, f_h = _font(19, True), _font(10), _font(9), _font(11, True), _font(10, True), _font(9, True)
    d.text((left, 16), 'Agents Activation Tracking — Account x Agents', font=f_t, fill=(30, 41, 59))
    d.text((left, 46), f'Snapshot {label}   {len(order)} accounts x {n} agents   V=activated  OFF=deactivated  blank=not added',
           font=f_s, fill=(100, 116, 139))
    x0 = left
    y_hb = top + head_h
    d.rectangle((x0, top, x0 + id_w + name_w + seg_w + today_w, y_hb), fill=(35, 42, 60))
    d.text((x0 + 6, y_hb - 20), 'Account ID', font=f_h, fill=(255, 255, 255))
    d.text((x0 + id_w + 6, y_hb - 20), 'Account Name', font=f_h, fill=(255, 255, 255))
    d.text((x0 + id_w + name_w + 4, y_hb - 20), 'Seg', font=f_h, fill=(255, 255, 255))
    d.text((x0 + id_w + name_w + seg_w + 2, y_hb - 20), 'Today', font=f_h, fill=(255, 255, 255))
    cx = x0 + id_w + name_w + seg_w + today_w
    idx = 0
    while idx < len(agent_cols):
        cat = agent_cols[idx][0]
        j = idx
        while j < len(agent_cols) and agent_cols[j][0] == cat:
            j += 1
        span = j - idx
        d.rectangle((cx + idx * cell_w, top, cx + j * cell_w - 2, top + 18), fill=CAT_RGB.get(cat, (100, 116, 139)))
        lbl = cat.replace('_', ' ').title()
        tb = d.textbbox((0, 0), lbl, font=f_h)
        if tb[2] - tb[0] < span * cell_w - 4:
            d.text((cx + idx * cell_w + (span * cell_w - (tb[2] - tb[0])) / 2, top + 3), lbl, font=f_h, fill=(255, 255, 255))
        idx = j
    for k, (_, agent) in enumerate(agent_cols):
        tmp = Image.new('RGBA', (head_h - 30, cell_w), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        nm = agent if len(agent) <= 20 else agent[:19] + '…'
        td.text((2, 6), nm, font=f_sm, fill=(30, 41, 59))
        tmp = tmp.rotate(90, expand=True)
        img.paste(tmp, (cx + k * cell_w, top + 20), tmp)
    d.rectangle((cx + n * cell_w, top, cx + n * cell_w + count_w, y_hb), fill=(35, 42, 60))
    d.text((cx + n * cell_w + 4, y_hb - 20), '#Act', font=f_h, fill=(255, 255, 255))
    for ri, aid in enumerate(order):
        y = y_hb + ri * row_h
        bg = (248, 250, 252) if ri % 2 else (255, 255, 255)
        d.rectangle((x0, y, cx + n * cell_w + count_w, y + row_h), fill=bg, outline=(238, 242, 247))
        meta = accounts[aid]
        d.text((x0 + 4, y + 7), aid[:20], font=f_sm, fill=(148, 163, 184))
        nm = meta['name'] if len(meta['name']) <= 26 else meta['name'][:25] + '…'
        d.text((x0 + id_w + 5, y + 6), nm, font=f_a, fill=(30, 41, 59))
        d.text((x0 + id_w + name_w + 5, y + 7), meta['segment'][:8], font=f_sm, fill=(71, 85, 105))
        d.text((x0 + id_w + name_w + seg_w + 6, y + 7),
               ('yes' if account_active_today(aid, agent_cols, status) else 'no'), font=f_sm, fill=(71, 85, 105))
        cnt = 0
        for k, (_, agent) in enumerate(agent_cols):
            st = status.get((aid, agent))
            cellx = cx + k * cell_w
            d.rectangle((cellx, y, cellx + cell_w, y + row_h), outline=(238, 242, 247))
            if st == 'active':
                d.rectangle((cellx + 1, y + 1, cellx + cell_w - 1, y + row_h - 1), fill=(220, 252, 231))
                d.text((cellx + cell_w / 2 - 4, y + 5), 'V', font=f_c, fill=(22, 101, 52)); cnt += 1
            elif st == 'inactive':
                d.rectangle((cellx + 1, y + 1, cellx + cell_w - 1, y + row_h - 1), fill=(254, 226, 226))
                d.text((cellx + 3, y + 7), 'off', font=f_sm, fill=(185, 28, 28))
        d.rectangle((cx + n * cell_w, y, cx + n * cell_w + count_w, y + row_h), fill=(238, 242, 255), outline=(226, 232, 240))
        d.text((cx + n * cell_w + count_w / 2 - 5, y + 5), str(cnt), font=f_c, fill=(30, 41, 59))
    img.save(path)


def write_raw(path_xlsx, rows):
    # append raw data as a second sheet by reopening not supported; handled inside write_xlsx caller instead
    pass


def infer_label(input_path):
    name = Path(input_path).stem
    m = re.search(r'(\d{4}-\d{2}-\d{2})', name)
    if m:
        return m.group(1)
    m = re.search(r'(\d{1,2})[_\- ]?(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)', name, re.I)
    if m:
        return f"{m.group(1)} {m.group(2).title()}"
    return date.today().isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('input', help='Agent-level activation export CSV')
    ap.add_argument('--label', help='Snapshot label (default: inferred from filename or today)')
    ap.add_argument('--outdir', default='exports', help='Output directory (default: exports)')
    ap.add_argument('--base', help='Output base filename (default: agents_activation_matrix_<label>)')
    args = ap.parse_args()

    label = args.label or infer_label(args.input)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r'[^0-9A-Za-z_-]', '_', label)
    base = args.base or f'agents_activation_matrix_{safe}'

    rows = load(args.input)
    accounts, order, agent_cols, status = build_model(rows)

    xlsx_path = outdir / f'{base}.xlsx'
    csv_path = outdir / f'{base}.csv'
    png_path = outdir / f'{base}_preview.png'

    # write xlsx with raw sheet embedded
    _write_xlsx_with_raw(xlsx_path, accounts, order, agent_cols, status, label, Path(args.input).name, rows)
    write_csv(csv_path, accounts, order, agent_cols, status)
    write_preview(png_path, accounts, order, agent_cols, status, label)

    active_accounts = sum(1 for aid in order if account_active_today(aid, agent_cols, status))
    print(f'label={label}')
    print(f'accounts={len(order)} active_today={active_accounts} agents={len(agent_cols)}')
    print(xlsx_path)
    print(csv_path)
    print(png_path)


def _write_xlsx_with_raw(path, accounts, order, agent_cols, status, label, src_name, rows):
    # Build matrix workbook, then add Raw Data + Legend sheets before closing.
    # Reuse write_xlsx logic but keep workbook open — reimplement minimal by calling and reopening is not possible,
    # so we duplicate: create workbook here.
    import xlsxwriter as _xw
    wb = _xw.Workbook(str(path))

    # ----- Activation Matrix sheet -----
    ws = wb.add_worksheet('Activation Matrix')
    f_title = wb.add_format({'bold': True, 'font_size': 15, 'font_color': '#1E293B'})
    f_sub = wb.add_format({'font_size': 9, 'font_color': '#64748B'})

    def f_cat(c):
        return wb.add_format({'bold': True, 'font_size': 8, 'font_color': 'white', 'bg_color': CAT_COLORS.get(c, '#64748B'),
                              'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})
    f_agent = wb.add_format({'bold': True, 'font_size': 8, 'font_color': '#1E293B', 'align': 'center', 'valign': 'bottom',
                             'rotation': 90, 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F1F5F9'})
    f_hdr = wb.add_format({'bold': True, 'font_size': 9, 'font_color': 'white', 'bg_color': '#232A3C', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})
    f_hdr_c = wb.add_format({'bold': True, 'font_size': 9, 'font_color': 'white', 'bg_color': '#232A3C', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': 'white'})

    def acct_fmt(alt):
        return wb.add_format({'bold': True, 'font_size': 9, 'font_color': '#1E293B', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    def meta_fmt(alt):
        return wb.add_format({'font_size': 8, 'font_color': '#475569', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    def id_fmt(alt):
        return wb.add_format({'font_size': 8, 'font_color': '#94A3B8', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0', 'bg_color': '#F8FAFC' if alt else '#FFFFFF', 'font_name': 'Consolas'})

    def blank_fmt(alt):
        return wb.add_format({'border': 1, 'border_color': '#EEF2F7', 'bg_color': '#F8FAFC' if alt else '#FFFFFF'})

    f_v = wb.add_format({'bold': True, 'font_size': 10, 'font_color': '#166534', 'bg_color': '#DCFCE7', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
    f_off = wb.add_format({'font_size': 9, 'font_color': '#B91C1C', 'bg_color': '#FEE2E2', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})
    f_count = wb.add_format({'bold': True, 'font_size': 9, 'font_color': '#1E293B', 'bg_color': '#EEF2FF', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': '#E2E8F0'})

    INFO = ['Account ID', 'Account Name', 'Segment', 'Package', 'CSM', 'Interview Date', 'Active today']
    first_agent = len(INFO)
    last_agent = first_agent + len(agent_cols) - 1
    count_col = last_agent + 1

    ws.write(0, 0, 'Agents Activation Tracking — Account x Agents', f_title)
    ws.write(1, 0, f'Snapshot: {label}  ·  source: {src_name}  ·  {len(order)} accounts · {len(agent_cols)} agents  ·  '
                   'V = activated, OFF = added but deactivated, blank = not added. CSM & Interview Date left blank for manual entry.', f_sub)

    CAT_ROW, AGENT_ROW, DATA = 3, 4, 5
    for i, name in enumerate(INFO):
        ws.merge_range(CAT_ROW, i, AGENT_ROW, i, name, f_hdr if i in (0, 1) else f_hdr_c)
    idx = 0
    while idx < len(agent_cols):
        cat = agent_cols[idx][0]
        j = idx
        while j < len(agent_cols) and agent_cols[j][0] == cat:
            j += 1
        lbl = cat.replace('_', ' ').title()
        if j - idx == 1:
            ws.write(CAT_ROW, first_agent + idx, lbl, f_cat(cat))
        else:
            ws.merge_range(CAT_ROW, first_agent + idx, CAT_ROW, first_agent + j - 1, lbl, f_cat(cat))
        idx = j
    for k, (_, agent) in enumerate(agent_cols):
        ws.write(AGENT_ROW, first_agent + k, agent, f_agent)
    ws.merge_range(CAT_ROW, count_col, AGENT_ROW, count_col, '# Active', f_hdr_c)

    for ri, aid in enumerate(order):
        row = DATA + ri
        alt = ri % 2 == 1
        meta = accounts[aid]
        ws.write(row, 0, aid, id_fmt(alt))
        ws.write(row, 1, meta['name'], acct_fmt(alt))
        ws.write(row, 2, meta['segment'], meta_fmt(alt))
        ws.write(row, 3, meta['package'], meta_fmt(alt))
        ws.write(row, 4, '', meta_fmt(alt))
        ws.write(row, 5, '', meta_fmt(alt))
        ws.write(row, 6, 'true' if account_active_today(aid, agent_cols, status) else 'false', meta_fmt(alt))
        cnt = 0
        for k, (_, agent) in enumerate(agent_cols):
            st = status.get((aid, agent))
            c = first_agent + k
            if st == 'active':
                ws.write(row, c, 'V', f_v); cnt += 1
            elif st == 'inactive':
                ws.write(row, c, 'OFF', f_off)
            else:
                ws.write_blank(row, c, None, blank_fmt(alt))
        ws.write(row, count_col, cnt, f_count)

    ws.set_column(0, 0, 20); ws.set_column(1, 1, 26); ws.set_column(2, 3, 9)
    ws.set_column(4, 4, 13); ws.set_column(5, 5, 12); ws.set_column(6, 6, 9)
    ws.set_column(first_agent, last_agent, 4.2); ws.set_column(count_col, count_col, 8)
    ws.set_row(AGENT_ROW, 150)
    ws.freeze_panes(DATA, 2)
    ws.set_zoom(90)

    # ----- Raw Data sheet -----
    ws2 = wb.add_worksheet('Raw Data')
    headers = list(rows[0].keys())
    h_fmt = wb.add_format({'bold': True, 'bg_color': '#232A3C', 'font_color': 'white', 'border': 1})
    for c, h in enumerate(headers):
        ws2.write(0, c, h, h_fmt)
    for ri, r in enumerate(rows, 1):
        for c, h in enumerate(headers):
            ws2.write(ri, c, r[h])
    ws2.set_column(0, 1, 26); ws2.set_column(7, 7, 30); ws2.set_column(9, 10, 22)
    ws2.freeze_panes(1, 0)

    # ----- Legend sheet -----
    ws3 = wb.add_worksheet('Legend & Notes')
    ws3.write(0, 0, 'Legend & Notes', wb.add_format({'bold': True, 'font_size': 13}))
    ws3.write(2, 0, 'V', f_v); ws3.write(2, 1, 'Agent is activated for the account (Agent Active = true)')
    ws3.write(3, 0, 'OFF', f_off); ws3.write(3, 1, 'Agent was added but is currently deactivated (Agent Active = false)')
    ws3.write(4, 0, '(blank)', blank_fmt(False)); ws3.write(4, 1, 'Agent has not been added for this account')
    ws3.write(6, 0, 'Snapshot', wb.add_format({'bold': True})); ws3.write(6, 1, label)
    ws3.write(7, 0, 'Source', wb.add_format({'bold': True})); ws3.write(7, 1, src_name)
    ws3.write(9, 1, 'Regenerate any day: python3 scripts/build_activation_matrix.py <that-days-export>.csv')
    ws3.set_column(0, 0, 12); ws3.set_column(1, 1, 95)

    wb.close()


if __name__ == '__main__':
    main()
