# Overview

This document describes the database setup and SQL validation queries used for testing the Back Billing process in the development environment.

---

## Repositories

### Application

- **rft-billing-watcher**: [GitLab](https://gitlab.six-group.net/six/rftemir/rft/components/backend/rft-billing/rft-billing-watcher)
- **rft-report-writer**: [GitLab](https://gitlab.six-group.net/six/rftemir/rft/components/backend/rft-billing/rft-billing-report-writer)

### QA Environment

- **rft-qa-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-qa-environment/-/tree/main/billing)
- **ukrefit-qa-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-qa-environment)

### INT Environment

- **rft-int-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-int-environment/-/tree/main/billing)
- **ukrefit-int-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-int-environment)

### DEV Environment

- **rft-dev-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-dev-environment/-/tree/main/billing)
- **ukrefit-dev-environment**: [GitLab](https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-dev-environment)

> ⚠️ Revisar la regex de filerouter (`rft-filerouter-router-bp-out`)

### Work Repository Endpoints

- `/work-repository/write`
- `/work-repository/read`
- Output format: `.zip` compressed

---

## Diagram

The following diagram shows the complete flow through Watcher, Writers, File Router, and FTP.

Supported channels: **WEB** | **SFTP**

```mermaid
---
title: Flujo completo - Watcher, Writers, File Router y FTP (versión final)
---
flowchart TD
    A([Start]) --> B[Cliente realiza petición POST /billing/commands/M00X]
    B --> C[Watcher recibe la solicitud]
    C --> D{commandId}
    D -->|M001| E1[Ejecutar flujo 1]
    E1 --> F1["Publicar en tópicos 'client' y 'data1'"]
    F1 --> G1["writer-m001 consume 'data1'"]
    G1 --> H1[writer-m001 genera el fichero de salida .zip]
    H1 --> I1["writer-m001 envía a tópico 'filerouter-outcoming'"]
    I1 --> J1["writer-m001 envía a tópico 'filerouterevents'"]
    D -->|M002| E2[Ejecutar flujo 2]
    E2 --> F2["Publicar en tópicos 'client' y 'data2'"]
    F2 --> G2["writer-m002 consume 'data2'"]
    G2 --> H2[writer-m002 genera el fichero de salida .zip]
    H2 --> I2["writer-m002 envía a tópico 'filerouter-outcoming'"]
    I2 --> J2["writer-m002 envía a tópico 'filerouterevents'"]
    D -->|M003| E3[Ejecutar flujo 3]
    E3 --> F3["Publicar en tópicos 'client' y 'data3'"]
    F3 --> G3["writer-m003 consume 'data3'"]
    G3 --> H3[writer-m003 genera el fichero de salida .zip]
    H3 --> I3["writer-m003 envía a tópico 'filerouter-outcoming'"]
    I3 --> J3["writer-m003 envía a tópico 'filerouterevents'"]
    D -->|M004| E4[Ejecutar flujo 4]
    E4 --> F4["Publicar en tópicos 'client' y 'data4'"]
    F4 --> G4["writer-m004 consume 'data4'"]
    G4 --> H4[writer-m004 genera el fichero de salida .zip]
    H4 --> I4["writer-m004 envía a tópico 'filerouter-outcoming'"]
    I4 --> J4["writer-m004 envía a tópico 'filerouterevents'"]
    J1 & J2 & J3 & J4 --> K["File Router consume 'filerouterevents'"]
    K --> L[File Router envía el fichero comprimido al servidor FTP]
    L --> Z([Stop])
```

---

## Curl Petition

```bash
curl -k -v --location \
  'https://rft-billing-watcher.rft-dev-bec.svc.cluster.local:8443/billing/commands/M004' \
  --header 'Content-Type: application/json' \
  --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...' \
  --data '{
    "commandParams": {
      "commandId": "M004",
      "parameters": {
        "movFecha": "2025-05"
      }
    }
  }'
```

---

## Database Preparation

The following tables have been defined in the development environment to support Back Billing tests.

### 1. Table `BILLING_REPORTS`

**Location:** `[dev-billing].dbo.BILLING_REPORTS`

Stores the configuration and activation status of billing report types.

| Field | Description |
|---|---|
| `CTA_ID` | Account identifier |
| `TYPE` | Report type (M001–M004) |
| `ACTIVATION` | Active/inactive indicator |
| `CHANNEL` | Associated communication channel |

### 2. Table `BRMCTAS`

**Location:** `[dev-billing].dbo.BRMCTAS`

Contains the master data of BRM accounts used for billing associations.

| Field | Description |
|---|---|
| `CTA_CODCTA` | Account permission code |
| `CTA_IDENT2` | Identifier linked to the billing report |
| `CTA_TIP_CTA` | Account parent |

### 3. Table `MOVFACTU_MANT`

**Location:** `[dev-billing-work].dbo.MOVFACTU_MANT`

Stores maintenance-related billing movements associated with process type M001.
Indexes have been added to optimize queries by date, account, and trade ID.

### 4. Table `MOLFACTU`

**Location:** `[dev-billing-work].dbo.MOLFACTU`

Contains information for process type M004, mainly related to error tracking or adjustments.
Indexes are included to optimize searches by account and date.

### 5. Table `MOVFACTU`

**Location:** `[dev-billing-work].dbo.MOVFACTU`

Stores billing movement records for M002 and M003 processes.
Indexes `IXMOV1–IXMOV4` enhance performance for lookups by date, account, and trade ID.

---

## DDL Scripts

### `[dev-billing].dbo.BILLING_REPORTS`

```sql
CREATE TABLE [dev-billing].dbo.BILLING_REPORTS (
    CTA_ID    varchar(20) COLLATE Latin1_General_CS_AS NOT NULL,
    [TYPE]    char(4)     COLLATE Latin1_General_CS_AS NOT NULL,
    FEC_ALTA  char(8)     COLLATE Latin1_General_CS_AS NOT NULL,
    FEC_BAJA  char(8)     COLLATE Latin1_General_CS_AS NULL,
    ACTIVATION bit        NOT NULL,
    CHANNEL   char(4)     COLLATE Latin1_General_CS_AS NOT NULL,
    CONSTRAINT PK_BILLING_REPORTS PRIMARY KEY (CTA_ID, [TYPE])
);
```

### `[dev-billing].dbo.BRMCTAS`

```sql
CREATE TABLE [dev-billing].dbo.BRMCTAS (
    CTA_CODCTA               char(6)      COLLATE Latin1_General_CS_AS NOT NULL,
    CTA_TIP_ID               char(3)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IDENT                varchar(50)  COLLATE Latin1_General_CS_AS NULL,
    CTA_FEC_ALTA             char(10)     COLLATE Latin1_General_CS_AS NULL,
    CTA_FEC_BAJA             char(10)     COLLATE Latin1_General_CS_AS NOT NULL,
    CTA_TIP_ID2              char(3)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IDENT2               varchar(50)  COLLATE Latin1_General_CS_AS NULL,
    CTA_TIP_ID3              char(3)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IDENT3               varchar(50)  COLLATE Latin1_General_CS_AS NULL,
    CTA_TIP_CTA              char(1)      COLLATE Latin1_General_CS_AS NOT NULL,
    CTA_NOMBREC              varchar(15)  COLLATE Latin1_General_CS_AS NULL,
    CTA_NOMBREL              varchar(50)  COLLATE Latin1_General_CS_AS NULL,
    CTA_NIV_SUS              char(2)      COLLATE Latin1_General_CS_AS NULL,
    CTA_TIP_ENT              char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_CTAMASTER            char(6)      COLLATE Latin1_General_CS_AS NULL,
    CTA_CTARTGS              varchar(11)  COLLATE Latin1_General_CS_AS NULL,
    CTA_USUMAX               decimal(3,0) NULL,
    CTA_PAIS                 char(2)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND_ELCOM            char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND_REMIT            char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND1                 char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND2                 char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND3                 char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND4                 char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_IND5                 char(1)      COLLATE Latin1_General_CS_AS NULL,
    CTA_USUARIO              char(10)     COLLATE Latin1_General_CS_AS NULL,
    CTA_FEC_MOD              char(10)     COLLATE Latin1_General_CS_AS NULL,
    CTA_HOR_MOD              char(8)      COLLATE Latin1_General_CS_AS NULL,
    CTA_PAR_VAT              varchar(15)  COLLATE Latin1_General_CS_AS NULL,
    CTA_PAR_FEC_ALTA         char(10)     COLLATE Latin1_General_CS_AS NULL,
    CTA_GRUPO                char(4)      COLLATE Latin1_General_CS_AS NULL,
    CTA_EMAILFACT            varchar(100) COLLATE Latin1_General_CS_AS NULL,
    CTA_INSTITUTIONID        varchar(9)   COLLATE Latin1_General_CS_AS NULL,
    CTA_ACC_TOBE_CHARGE      char(1)      COLLATE Latin1_General_CS_AS DEFAULT 'S' NULL,
    CTA_EXCEPTION_START_DATE varchar(10)  COLLATE Latin1_General_CS_AS NULL,
    CTA_REASON               varchar(10)  COLLATE Latin1_General_CS_AS NULL,
    CTA_REASON_DETAILS       varchar(150) COLLATE Latin1_General_CS_AS NULL,
    CTA_BP_CODE              varchar(10)  COLLATE Latin1_General_CS_AS NULL,
    CONSTRAINT PK_BRMCTAS PRIMARY KEY (CTA_CODCTA)
);
```

### `[dev-billing-work].dbo.MOVFACTU_MANT`

```sql
CREATE TABLE [dev-billing-work].dbo.MOVFACTU_MANT (
    MOM_FECHA           char(8)        NOT NULL,
    MOM_DATE_START      char(10)       NOT NULL,
    MOM_FICHERO         char(8)        DEFAULT '' NULL,
    MOM_ACCOUNT_FACTU   char(6)        NOT NULL,
    MOM_CANON           char(3)        NULL,
    MOM_IDT_1           char(3)        NOT NULL,
    MOM_ID_1            varchar(50)    NOT NULL,
    MOM_IDT_2           char(3)        NOT NULL,
    MOM_ID_2            varchar(50)    NOT NULL,
    MOM_TRADEID         varchar(52)    NOT NULL,
    MOM_REPORTING_IDT1  char(3)        DEFAULT '' NULL,
    MOM_REPORTING_ID1   varchar(50)    DEFAULT '' NULL,
    MOM_ACCOUNT_REP     char(6)        NOT NULL,
    MOM_IMPORTE         decimal(9,5)   NULL,
    MOV_CONTRACT_TYPE   varchar(2)     NULL,
    MOV_ASSET           varchar(2)     NULL,
    temp_id             bigint         IDENTITY(1,1) NOT NULL
);
```

Includes indexes `IXMOM1U`, `IXMOM2`, `IXMOM3` to optimize searches by date, account, and trade ID.

### `[dev-billing-work].dbo.MOLFACTU`

```sql
CREATE TABLE [dev-billing-work].dbo.MOLFACTU (
    MOL_FECHA         char(8)     NOT NULL,
    MOL_ACCOUNT_FACTU char(6)     NOT NULL,
    MOL_CANON         char(3)     NULL,
    MOL_RSE           varchar(50) NOT NULL,
    MOL_ID_1          varchar(50) NOT NULL,
    MOL_ERR           varchar(50) NULL,
    MOL_QTY           varchar(50) NOT NULL
);
```

Includes indexes `IXMOL` and `IXMOL1` to optimize searches by account and date.

### `[dev-billing-work].dbo.MOVFACTU`

```sql
CREATE TABLE [dev-billing-work].dbo.MOVFACTU (
    MOV_FECHA           char(10)     NOT NULL,
    MOV_FICHERO         char(8)      DEFAULT '' NULL,
    MOV_ACCOUNT_FACTU   char(6)      NOT NULL,
    MOV_CANON           char(3)      NOT NULL,
    MOV_IDT_1           char(3)      NOT NULL,
    MOV_ID_1            varchar(50)  NOT NULL,
    MOV_IDT_2           char(3)      NOT NULL,
    MOV_ID_2            varchar(50)  NOT NULL,
    MOV_TRADEID         varchar(52)  NOT NULL,
    MOV_TIPO            char(4)      DEFAULT '' NULL,
    MOV_REPORTING_IDT1  char(3)      DEFAULT '' NULL,
    MOV_REPORTING_ID1   varchar(50)  DEFAULT '' NULL,
    MOV_ACCOUNT_REP     char(6)      NOT NULL,
    MOV_MESSAGE_REF     varchar(40)  DEFAULT '' NULL,
    MOV_IMPORTE         decimal(9,5) NULL,
    MOV_CONTRACT_TYPE   varchar(2)   NULL,
    MOV_ASSET           varchar(2)   NULL,
    MOV_FECHA_INSERT    datetime2    NOT NULL
);
```

Includes indexes `IXMOV1` to `IXMOV4` for searches by date, account, and trade ID.

---

## Data Consistency Summary

| Code | Main Table | Special Condition |
|---|---|---|
| M001 | `MOVFACTU_MANT` | None |
| M002 | `MOVFACTU` | `MOV_TIPO = 'OTCS'` |
| M003 | `MOVFACTU` | `MOV_TIPO = 'ETDS'` |
| M004 | `MOLFACTU` | None |

---

## SQL Validation Queries

Each process type includes specific SQL queries to validate consistency and count records per account (`CTA_ID`).

- **M001**: Maintenance movements (`MOVFACTU_MANT`)
- **M002**: OTC operations (`MOVFACTU` where `MOV_TIPO = 'OTCS'`)
- **M003**: ETD operations (`MOVFACTU` where `MOV_TIPO = 'ETDS'`)
- **M004**: Log and control operations (`MOLFACTU`)

Each query retrieves the total number of records per account, along with key details such as Trade ID, report type, channel, and related account information.

> ⚠️ *En las queries falta el filtro de las fechas.*

---

## Database Connection Pool Properties

The following HikariCP settings have been applied to ensure stability during the generation of heavy reports (M001–M004) and to prevent timeouts during peak loads.

### Configuration Strategy: Balanced & Resilient

```yaml
hikari:
  pool-name: ConnPool
  maximum-pool-size: 6       # 4 connections for active reports + 2 buffer for auxiliary tasks
  minimum-idle: 2            # Keeps 2 connections ready to reduce initial latency
  connection-timeout: 30000  # 30s max wait time to avoid indefinite blocking
  idle-timeout: 300000       # 5 min before releasing unused connections to save resources
  max-lifetime: 1200000      # 20 min max life (Critical: exceeds the ~3 min report duration)
```

### Key Justification

- **Concurrency**: Capped at 6 to support the 4 simultaneous report requirements while allowing a safety margin for internal health checks.
- **Stability**: The `max-lifetime` is set to 20 minutes, ensuring that connections do not expire mid-process during long-running billing queries.
- **Fail-fast**: A 30-second `connection-timeout` prevents threads from hanging indefinitely if the pool is exhausted.

---

## Queries by Message Type

The following SQL queries extract and summarize Back Billing data per message type (M001–M004).
Each query uses consistent joins between `dev-billing-work`, `dev-billing.BRMCTAS`, and `dev-billing.BILLING_REPORTS`.

### 🔹 M001

#### Summary by Account

```sql
SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS
FROM [dev-billing-work].dbo.MOVFACTU_MANT AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOM_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M001'
    AND b.ACTIVATION = 1
WHERE m.MOM_FECHA BETWEEN '20250501' AND '20250531'
GROUP BY b.CTA_ID
ORDER BY TOTAL_ROWS DESC;
```

#### Detailed Data Extraction

```sql
SELECT
    m.MOM_FECHA          AS MOM_FECHA,
    m.MOM_TRADEID        AS MOM_TRADEID,
    m.MOM_ACCOUNT_FACTU  AS ACCOUNT_FACTU,
    b.CTA_ID             AS CTA_ID,
    b.[TYPE]             AS TYPE,
    b.CHANNEL            AS CHANNEL,
    c.CTA_CODCTA         AS CTA_CODCTA,
    c.CTA_IDENT2         AS CTA_IDENT2,
    c.CTA_TIP_CTA        AS CTA_TIP_CTA,
    m.MOM_CANON          AS MOM_CANON,
    m.MOM_ID_1           AS MOM_ID_1,
    m.MOM_ID_2           AS MOM_ID_2,
    m.MOM_IMPORTE        AS MOM_IMPORTE
FROM [dev-billing-work].dbo.MOVFACTU_MANT AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOM_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M001'
    AND b.ACTIVATION = 1
WHERE m.MOM_FECHA BETWEEN '20250501' AND '20250531'
ORDER BY b.CTA_ID, m.MOM_ACCOUNT_FACTU, m.MOM_TRADEID;
```

### 🔹 M002

#### Summary by Account

```sql
SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS
FROM [dev-billing-work].dbo.MOVFACTU AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
WHERE m.MOV_TIPO = 'OTDS'
GROUP BY b.CTA_ID
ORDER BY TOTAL_ROWS DESC;
```

#### Detailed Data Extraction

```sql
SELECT
    m.MOV_ACCOUNT_FACTU   AS ACCOUNT_TO_BE_CHARGED,
    m.MOV_CANON           AS MATERIAL,
    m.MOV_ID_1            AS REPORTING_COUNTER_PARTY,
    m.MOV_ID_2            AS OTHER_COUNTER_PARTY,
    m.MOV_TRADEID         AS UTI,
    m.MOV_REPORTING_ID1   AS REPORTING_SUBMIT_ENTITY,
    m.MOV_FECHA           AS MOV_FECHA,
    b.CTA_ID              AS CTA_ID,
    b.[TYPE]              AS TYPE,
    b.CHANNEL             AS CHANNEL,
    c.CTA_CODCTA          AS CTA_CODCTA,
    c.CTA_IDENT2          AS CTA_IDENT2,
    c.CTA_TIP_CTA         AS CTA_TIP_CTA
FROM [dev-billing-work].dbo.MOVFACTU AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
WHERE m.MOV_TIPO = 'OTCS'
ORDER BY b.CTA_ID, m.MOV_ACCOUNT_FACTU, m.MOV_TRADEID;
```

### 🔹 M003

#### Summary by Account

```sql
SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS
FROM [dev-billing-work].dbo.MOVFACTU AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
WHERE m.MOV_TIPO = 'ETDS'
GROUP BY b.CTA_ID
ORDER BY TOTAL_ROWS DESC;
```

#### Detailed Data Extraction

```sql
SELECT
    m.MOV_ACCOUNT_FACTU   AS ACCOUNT_TO_BE_CHARGED,
    m.MOV_CANON           AS MATERIAL,
    m.MOV_ID_1            AS REPORTING_COUNTER_PARTY,
    m.MOV_ID_2            AS OTHER_COUNTER_PARTY,
    m.MOV_TRADEID         AS UTI,
    m.MOV_REPORTING_ID1   AS REPORTING_SUBMIT_ENTITY,
    m.MOV_FECHA           AS MOV_FECHA,
    b.CTA_ID              AS CTA_ID,
    b.[TYPE]              AS TYPE,
    b.CHANNEL             AS CHANNEL,
    c.CTA_CODCTA          AS CTA_CODCTA,
    c.CTA_IDENT2          AS CTA_IDENT2,
    c.CTA_TIP_CTA         AS CTA_TIP_CTA
FROM [dev-billing-work].dbo.MOVFACTU AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
WHERE m.MOV_TIPO = 'ETDS'
ORDER BY b.CTA_ID, m.MOV_ACCOUNT_FACTU, m.MOV_TRADEID;
```

### 🔹 M004

#### Summary by Account

```sql
SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS
FROM [dev-billing-work].dbo.MOLFACTU AS m
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON m.MOL_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
GROUP BY b.CTA_ID
ORDER BY TOTAL_ROWS DESC;
```

#### Detailed Data Extraction

```sql
SELECT
    l.MOL_FECHA           AS MOL_FECHA,
    l.MOL_ACCOUNT_FACTU   AS ACCOUNT_TO_BE_CHARGED,
    l.MOL_CANON           AS MATERIAL,
    l.MOL_RSE             AS REPORTING_SUBMIT_ENTITY,
    l.MOL_ID_1            AS REPORTING_COUNTER_PARTY,
    l.MOL_ERR             AS ENTITY_RESPONSIBLE_FOR_REPORTING,
    l.MOL_QTY             AS MOL_QTY,
    b.CTA_ID              AS CTA_ID,
    b.[TYPE]              AS TYPE,
    b.CHANNEL             AS CHANNEL,
    c.CTA_CODCTA          AS CTA_CODCTA,
    c.CTA_IDENT2          AS CTA_IDENT2,
    c.CTA_TIP_CTA         AS CTA_TIP_CTA
FROM [dev-billing-work].dbo.MOLFACTU AS l
INNER JOIN [dev-billing].dbo.BRMCTAS AS c
    ON l.MOL_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS
INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b
    ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS
    AND b.[TYPE] = 'M002'
    AND b.ACTIVATION = 1
ORDER BY b.CTA_ID, l.MOL_ACCOUNT_FACTU;
```

---

## Kafka Topics Overview

### EUREFIT Environment

The following Kafka topics are used for Back Billing reusable message processing.

| Topic Name | Partitions | Replication Factor | Cleanup Policy | Current Size |
|---|---|---|---|---|
| `rft.dev.billing.restricted.clients.reusable.v1` | 1 | 4 | delete | 19.3 MiB |
| `rft.dev.billing.restricted.m001.reusable.v1` | 1 | 4 | delete | 10.2 GiB |
| `rft.dev.billing.restricted.m002.reusable.v1` | 1 | 4 | delete | 8.73 KiB |
| `rft.dev.billing.restricted.m003.reusable.v1` | 1 | 4 | delete | 0 B |
| `rft.dev.billing.restricted.m004.reusable.v1` | 1 | 4 | delete | 15 K |
| `rft.dev.filerouter.file.outcoming.reusable.v1` | — | — | — | — |
| `rft.dev.filerouter.events.private.v1` | — | — | — | — |

### UKREFIT Environment

| Topic Name | Partitions | Replication Factor | Cleanup Policy | Current Size |
|---|---|---|---|---|
| `ukrefit.dev.billing.restricted.clients.reusable.v1` | 1 | 4 | delete | 0 B |
| `ukrefit.dev.billing.restricted.m001.reusable.v1` | 1 | 4 | delete | 0 B |
| `ukrefit.dev.billing.restricted.m002.reusable.v1` | 1 | 4 | delete | 0 B |
| `ukrefit.dev.billing.restricted.m003.reusable.v1` | 1 | 4 | delete | 0 B |
| `ukrefit.dev.billing.restricted.m004.reusable.v1` | 1 | 4 | delete | 0 B |
| `ukrefit.dev.filerouter.file.outcoming.reusable.v1` | — | — | — | — |
| `ukrefit.dev.filerouter.events.private.v1` | — | — | — | — |

---

## Advanced Kafka Configuration

### Kafka Producer

| Parameter | Description | Value |
|---|---|---|
| `linger.ms` | Wait time before sending a batch of messages | 20 ms |
| `batch.size` | Maximum batch size | 900,000 bytes |
| `buffer.memory` | Total memory allocated for buffering | 13,430,000,217,728 bytes |
| `request.timeout.ms` | Maximum broker response time | 30 s |
| `delivery.timeout.ms` | Total timeout before reporting an error | 120 s |
| `max.block.ms` | Maximum blocking time when sending | 90 s |

### Kafka Consumer

| Parameter | Description | Value |
|---|---|---|
| `max.poll.interval.ms` | Maximum interval between polls | 180,000 ms |
| `max.poll.records` | Maximum records per poll | 10,000 |
| `fetch.min.bytes` | Minimum bytes to fetch per request | 900,000 |
| `fetch.max.wait.ms` | Maximum wait time per fetch | 1,000 ms |

---

## Relevant Fields by Message Type

| Type | Field | Description |
|---|---|---|
| M001 | `MOM_ACCOUNT_FACTU` | Account to be charged |
| M001 | `MOM_CANON` | Material |
| M001 | `MOM_ID_1` | Reporting counterparty |
| M001 | `MOM_ID_2` | Other counterparty |
| M001 | `MOM_TRADEID` | UTI |
| M001 | `MOM_REPORTING_ID1` | Reporting submitting entity |
| M002 | `MOV_ACCOUNT_FACTU` | Account to be charged |
| M002 | `MOV_CANON` | Material |
| M002 | `MOV_ID_1` | Reporting counterparty |
| M002 | `MOV_ID_2` | Other counterparty |
| M002 | `MOV_TRADEID` | UTI |
| M002 | `MOV_REPORTING_ID1` | Reporting submitting entity |
| M003 | `MOV_ACCOUNT_FACTU` | Account to be charged |
| M003 | `MOV_CANON` | Material |
| M003 | `MOV_ID_1` | Reporting counterparty |
| M003 | `MOV_ID_2` | Other counterparty |
| M003 | `MOV_TRADEID` | UTI |
| M003 | `MOV_REPORTING_ID1` | Reporting submitting entity |
| M004 | `MOL_ACCOUNT_FACTU` | Account to be charged |
| M004 | `MOL_CANON` | Material |
| M004 | `MOL_RSE` | Reporting submitting entity |
| M004 | `MOL_ID_1` | Reporting counterparty |
| M004 | `MOV_ERR` | Entity responsible for reporting |
| M004 | `MOL_QTY` | Quantity |

---

## Performance Notes

We have been testing different days with different configurations and now have the best performance, generating **32 ZIP files** with **500,000 records** each in CSV format.
