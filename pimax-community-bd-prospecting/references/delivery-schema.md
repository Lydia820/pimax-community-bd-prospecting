# Workbook Delivery Schema

Default to one `.xlsx` workbook with three sheets.

## Sheet 1: `第N批BD名单`

Top summary metrics:

- accepted total;
- A and B counts;
- rows containing email;
- rows containing Discord;
- duplicates versus prior accepted batches;
- CRM pending count;
- category counts;
- verification date.

Columns:

1. 状态
2. 评分
3. 等级
4. 类型
5. 名称
6. 公开直接联系方式
7. 联系方式类型
8. 平台/网站
9. 国家/地区
10. 国家置信度
11. 语言
12. 官网/主页
13. 受众/主题
14. 近期活跃证据
15. 活跃证据日期
16. 联系方式来源
17. Pimax匹配理由
18. 合作信号
19. 全部来源
20. 核验日期
21. 证据置信度
22. 历史批次去重状态
23. CRM状态
24. 邮箱/Discord历史检查
25. 建议下一步
26. 备注

Use `business_email`, `admin_dm`, or `business_email+admin_dm` for contact type. Accepted rows use `unique_vs_prior_batches` and, without actual CRM clearance, `unchecked`.

## Sheet 2: `待复核未入主表`

Columns: 状态、类型、名称、公开联系方式、未入主表原因、来源、复核动作.

Include form-only, weak-recency, unverified-invite, placeholder-contact, possible duplicate, and known-relationship cases here. Make clear that these rows are not part of the usable accepted count.

## Sheet 3: `去重说明`

Record:

- prior workbook names and accepted counts;
- current accepted count;
- duplicate count;
- CRM/mailbox scope and caveat;
- known-relationship exclusions;
- every prior accepted name with its current-batch treatment.

## Presentation and validation

- Use a readable table with filters, frozen header rows, wrapped text, restrained color, and visible A/B distinctions.
- Keep formulas for summary metrics rather than manually typed totals.
- Render all sheets and visually inspect clipping, blank regions, and unreadable widths.
- Recalculate, inspect summary cells and sample rows, scan for formula errors, and test the exported XLSX archive.
- Include source URLs in the workbook. The chat handoff should summarize counts and CRM caveats, not repeat the full table.

