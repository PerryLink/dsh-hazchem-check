/**
 * dsh-hazchem-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'hazchem_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  itemNo: ['序号', '编号', '项号', 'itemNo'],
  chemicalName: ['化学品名称', '危险化学品名称', '品名', 'chemicalName'],
  casNo: ['CAS 号', 'CAS号', 'CAS', 'casNo'],
  cnNo: ['危险货物编号', 'CN 号', '危规号', 'cnNo'],
  hazardClass: ['危险性类别', '危险类别', '类别', 'hazardClass'],
  state: ['状态', '形态', '物态', 'state'],
  storageLocation: ['储存位置', '存放地点', '库房', 'storageLocation'],
  maxStorage: ['最大储存量', '储存量', '库存量', 'maxStorage'],
  unit: ['计量单位', '单位', 'unit'],
  threshold: ['临界量', '临界量吨位', '构成重大危险源临界量', 'threshold'],
  majorSource: ['是否重大危险源', '重大危险源', '是否构成', 'majorSource'],
  sdsNo: ['安全技术说明书编号', 'SDS 编号', '技术说明书', 'sdsNo'],
  permitNo: ['许可证号', '经营许可证号', '使用许可证号', 'permitNo'],
  keeper: ['保管人', '责任人', '库管员', 'keeper'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'chemicals', '危化品'],
  columns: COLUMNS,
  header: {
  company: ['company', '企业名称', '单位名称'],
  site: ['site', '厂区', '场所'],
  assessmentAt: ['assessmentAt', '辨识日期', '评估日期'],
  basis: ['basis', '辨识依据', '适用名录'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '化学品名称',
  'chemicalName',
  '临界量',
  'threshold',
  '最大储存量',
  'maxStorage',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
