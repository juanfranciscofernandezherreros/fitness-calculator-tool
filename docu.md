Overview

This document describes the database setup and SQL validation queries used for testing the Back Billing process in the development environment.

Repositories

rft-billing-watcher : https://gitlab.six-group.net/six/rftemir/rft/components/backend/rft-billing/rft-billing-watcher

rft-eport-writer : https://gitlab.six-group.net/six/rftemir/rft/components/backend/rft-billing/rft-billing-report-writer




rft-qa-environment : https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-qa-environment/-/tree/main/billing

ukrefit-qa-enviornment : https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-qa-environment 




rft-int-environment : https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-int-environment/-/tree/main/billing

ukrefit-int-enviornment : https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-int-environment 




rft-dev-environment : https://gitlab.six-group.net/six/rftemir/eu/derivatives/infra/ocp/argocd/non-prod/rft-dev-environment/-/tree/main/billing

ukrefit-dev-enviornment : https://gitlab.six-group.net/six/rftemir/uk/derivatives/infra/ocp/argocd/non-prod/ukrefit-dev-environment rft-filerouter-router-bp-out




Revisar la regex de filerouter (rft-filerouter-router-bp-out)




/work-repository/write

/work-repository/read

.zip comprimido




WEB

SFTP

Diagram

---
title: Flujo completo - Watcher, Writers, File Router y FTP (versión final)
---
activityDiagram-v2
    start
    :Cliente realiza petición POST /billing/commands/M00X;
    :Watcher recibe la solicitud;
    decision commandId
        case "M001"
            :Ejecutar flujo 1;
            :Publicar en tópicos "client" y "data1";
            :Microservicio writer-m001 consume "data1";
            :writer-m001 genera el fichero de salida (.zip);
            :writer-m001 envía a tópico "filerouter-outcoming";


            :writer-m001 envía a tópico "filerouterevents";
        case "M002"
            :Ejecutar flujo 2;
            :Publicar en tópicos "client" y "data2";
            :Microservicio writer-m002 consume "data2";
            :writer-m002 genera el fichero de salida (.zip);
            :writer-m002 envía a tópico "filerouter-outcoming";
            :writer-m002 envía a tópico "filerouterevents";
        case "M003"
            :Ejecutar flujo 3;
            :Publicar en tópicos "client" y "data3";
            :Microservicio writer-m003 consume "data3";
            :writer-m003 genera el fichero de salida (.zip);
            :writer-m003 envía a tópico "filerouter-outcoming";
            :writer-m003 envía a tópico "filerouterevents";
        case "M004"
            :Ejecutar flujo 4;
            :Publicar en tópicos "client" y "data4";
            :Microservicio writer-m004 consume "data4";
            :writer-m004 genera el fichero de salida (.zip);
            :writer-m004 envía a tópico "filerouter-outcoming";
            :writer-m004 envía a tópico "filerouterevents";
    end
    :File Router consume "filerouterevents";
    :File Router envía el fichero comprimido al servidor FTP;
    stop

Curl petition

curl -k -v --location 'https://rft-billing-watcher.rft-dev-bec.svc.cluster.local:8443/billing/commands/M004' --header 'Content-Type: application/json' --header 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0azF2Yy1CQVNFIiwiaWF0IjoxNzMwMDk3NjAwLCJleHAiOjMxNTM2MDAwMDAwLCJzaXguYnBJZCI6IlwibG9jYWxcIiIsInNpeC51c2VySWQiOiJcInRrMXZjLUJBU0VcIiIsInNpeC5lbWFpbElkIjoiXCJjYW1pbG9hbmRyZXMudmFsZW5jaWExQHNpeC1ncm91cC5jb21cIiIsInNpeC5yb2xlcyI6IltcIk5PUk1BTF9VU0VSXCJdIn0.RULOcoYU_mGkNBS6UgwrbEJxrCYG982dYSOdvBtGQN8' --data ' {
   "commandParams": {
       "commandId": "M004",
       "parameters": {
           "movFecha": "2025-05"
       }
   }
}'




Database Preparation

The following tables have been defined in the development environment to support Back Billing tests:

1. Table BILLING_REPORTS

Location: [dev-billing].dbo.BILLING_REPORTS
Stores the configuration and activation status of billing report types.

Key fields:

CTA_ID: Account identifier

TYPE: Report type (M001–M004)

ACTIVATION: Active/inactive indicator

CHANNEL: Associated communication channel

2. Table BRMCTAS

Location: [dev-billing].dbo.BRMCTAS
Contains the master data of BRM accounts used for billing associations.

Key fields:




CTA_CODCTA:  Account permsision

CTA_IDENT2: Identifier linked to the billing report

CTA_TIP_CTA: Account parent

3. Table MOVFACTU_MANT

Location: [dev-billing-work].dbo.MOVFACTU_MANT
Stores maintenance-related billing movements associated with process type M001.
Indexes have been added to optimize queries by date, account, and trade ID.

4. Table MOLFACTU

Location: [dev-billing-work].dbo.MOLFACTU
Contains information for process type M004, mainly related to error tracking or adjustments.
Indexes are included to optimize searches by account and date.

5. Table MOVFACTU

Location: [dev-billing-work].dbo.MOVFACTU
Stores billing movement records for M002 and M003 processes.
Indexes IXMOV1–IXMOV4 enhance performance for lookups by date, account, and trade ID.




Tabla: [dev-billing].dbo.BILLING_REPORTS




CREATE TABLE [dev-billing].dbo.BILLING_REPORTS ( CTA_ID varchar(20) COLLATE Latin1_General_CS_AS NOT NULL, [TYPE] char(4) COLLATE Latin1_General_CS_AS NOT NULL, FEC_ALTA char(8) COLLATE Latin1_General_CS_AS NOT NULL, FEC_BAJA char(8) COLLATE Latin1_General_CS_AS NULL, ACTIVATION bit NOT NULL, CHANNEL char(4) COLLATE Latin1_General_CS_AS NOT NULL, CONSTRAINT PK_BILLING_REPORTS PRIMARY KEY (CTA_ID,[TYPE]) );




Tabla: [dev-billing].dbo.BRM_CTAS




CREATE TABLE [dev-billing].dbo.BRMCTAS ( CTA_CODCTA char(6) COLLATE Latin1_General_CS_AS NOT NULL, CTA_TIP_ID char(3) COLLATE Latin1_General_CS_AS NULL, CTA_IDENT varchar(50) COLLATE Latin1_General_CS_AS NULL, CTA_FEC_ALTA char(10) COLLATE Latin1_General_CS_AS NULL, CTA_FEC_BAJA char(10) COLLATE Latin1_General_CS_AS NOT NULL, CTA_TIP_ID2 char(3) COLLATE Latin1_General_CS_AS NULL, CTA_IDENT2 varchar(50) COLLATE Latin1_General_CS_AS NULL, CTA_TIP_ID3 char(3) COLLATE Latin1_General_CS_AS NULL, CTA_IDENT3 varchar(50) COLLATE Latin1_General_CS_AS NULL, CTA_TIP_CTA char(1) COLLATE Latin1_General_CS_AS NOT NULL, CTA_NOMBREC varchar(15) COLLATE Latin1_General_CS_AS NULL, CTA_NOMBREL varchar(50) COLLATE Latin1_General_CS_AS NULL, CTA_NIV_SUS char(2) COLLATE Latin1_General_CS_AS NULL, CTA_TIP_ENT char(1) COLLATE Latin1_General_CS_AS NULL, CTA_CTAMASTER char(6) COLLATE Latin1_General_CS_AS NULL, CTA_CTARTGS varchar(11) COLLATE Latin1_General_CS_AS NULL, CTA_USUMAX decimal(3,0) NULL, CTA_PAIS char(2) COLLATE Latin1_General_CS_AS NULL, CTA_IND_ELCOM char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND_REMIT char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND1 char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND2 char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND3 char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND4 char(1) COLLATE Latin1_General_CS_AS NULL, CTA_IND5 char(1) COLLATE Latin1_General_CS_AS NULL, CTA_USUARIO char(10) COLLATE Latin1_General_CS_AS NULL, CTA_FEC_MOD char(10) COLLATE Latin1_General_CS_AS NULL, CTA_HOR_MOD char(8) COLLATE Latin1_General_CS_AS NULL, CTA_PAR_VAT varchar(15) COLLATE Latin1_General_CS_AS NULL, CTA_PAR_FEC_ALTA char(10) COLLATE Latin1_General_CS_AS NULL, CTA_GRUPO char(4) COLLATE Latin1_General_CS_AS NULL, CTA_EMAILFACT varchar(100) COLLATE Latin1_General_CS_AS NULL, CTA_INSTITUTIONID varchar(9) COLLATE Latin1_General_CS_AS NULL, CTA_ACC_TOBE_CHARGE char(1) COLLATE Latin1_General_CS_AS DEFAULT 'S' NULL, CTA_EXCEPTION_START_DATE varchar(10) COLLATE Latin1_General_CS_AS NULL, CTA_REASON varchar(10) COLLATE Latin1_General_CS_AS NULL, CTA_REASON_DETAILS varchar(150) COLLATE Latin1_General_CS_AS NULL, CTA_BP_CODE varchar(10) COLLATE Latin1_General_CS_AS NULL, CONSTRAINT PK_BRMCTAS PRIMARY KEY (CTA_CODCTA) );







Tabla: [dev-billing-work].dbo.MOVFACTU_MANT

CREATE TABLE [dev-billing-work].dbo.MOVFACTU_MANT ( MOM_FECHA char(8) NOT NULL, MOM_DATE_START char(10) NOT NULL, MOM_FICHERO char(8) DEFAULT '' NULL, MOM_ACCOUNT_FACTU char(6) NOT NULL, MOM_CANON char(3) NULL, MOM_IDT_1 char(3) NOT NULL, MOM_ID_1 varchar(50) NOT NULL, MOM_IDT_2 char(3) NOT NULL, MOM_ID_2 varchar(50) NOT NULL, MOM_TRADEID varchar(52) NOT NULL, MOM_REPORTING_IDT1 char(3) DEFAULT '' NULL, MOM_REPORTING_ID1 varchar(50) DEFAULT '' NULL, MOM_ACCOUNT_REP char(6) NOT NULL, MOM_IMPORTE decimal(9,5) NULL, MOV_CONTRACT_TYPE varchar(2) NULL, MOV_ASSET varchar(2) NULL, temp_id bigint IDENTITY(1,1) NOT NULL );

Incluye índices IXMOM1U, IXMOM2, IXMOM3 para optimizar búsquedas por fecha, cuenta y trade ID.

Tabla: [dev-billing-work].dbo.MOLFACTU

CREATE TABLE [dev-billing-work].dbo.MOLFACTU ( MOL_FECHA char(8) NOT NULL, MOL_ACCOUNT_FACTU char(6) NOT NULL, MOL_CANON char(3) NULL, MOL_RSE varchar(50) NOT NULL, MOL_ID_1 varchar(50) NOT NULL, MOL_ERR varchar(50) NULL, MOL_QTY varchar(50) NOT NULL );

Incluye índices IXMOL y IXMOL1 para optimizar búsquedas por cuenta y fecha.

Tabla: [dev-billing-work].dbo.MOVFACTU

CREATE TABLE [dev-billing-work].dbo.MOVFACTU ( MOV_FECHA char(10) NOT NULL, MOV_FICHERO char(8) DEFAULT '' NULL, MOV_ACCOUNT_FACTU char(6) NOT NULL, MOV_CANON char(3) NOT NULL, MOV_IDT_1 char(3) NOT NULL, MOV_ID_1 varchar(50) NOT NULL, MOV_IDT_2 char(3) NOT NULL, MOV_ID_2 varchar(50) NOT NULL, MOV_TRADEID varchar(52) NOT NULL, MOV_TIPO char(4) DEFAULT '' NULL, MOV_REPORTING_IDT1 char(3) DEFAULT '' NULL, MOV_REPORTING_ID1 varchar(50) DEFAULT '' NULL, MOV_ACCOUNT_REP char(6) NOT NULL, MOV_MESSAGE_REF varchar(40) DEFAULT '' NULL, MOV_IMPORTE decimal(9,5) NULL, MOV_CONTRACT_TYPE varchar(2) NULL, MOV_ASSET varchar(2) NULL, MOV_FECHA_INSERT datetime2 NOT NULL );

Incluye índices IXMOV1 a IXMOV4 para búsquedas por fecha, cuenta y trade ID.

 Data Consistency Summary




Code	Main Table	Special Condition
M001	MOVFACTU_MANT	None
M002	MOVFACTU	MOV_TIPO = 'OTCS'
M003	MOVFACTU	MOV_TIPO = 'ETDS'
M004	MOLFACTU	None
 SQL Validation Queries

Each process type includes specific SQL queries to validate consistency and count records per account (CTA_ID).

M001: Maintenance movements (MOVFACTU_MANT)

M002: OTC operations (MOVFACTU where MOV_TIPO = 'OTCS')

M003: ETD operations (MOVFACTU where MOV_TIPO = 'ETDS')

M004: Log and control operations (MOLFACTU)

Each query retrieves the total number of records per account, along with key details such as Trade ID, report type, channel, and related account information.

Database Connection Pool Properties

The following HikariCP settings have been applied to ensure stability during the generation of heavy reports (M001–M004) and to prevent timeouts during peak loads.

Configuration Strategy: Balanced & Resilient

YAML

hikari:
  pool-name: ConnPool
  maximum-pool-size: 6       # 4 connections for active reports + 2 buffer for auxiliary tasks
  minimum-idle: 2            # Keeps 2 connections ready to reduce initial latency
  connection-timeout: 30000  # 30s max wait time to avoid indefinite blocking
  idle-timeout: 300000       # 5 min before releasing unused connections to save resources
  max-lifetime: 1200000      # 20 min max life (Critical: exceeds the ~3 min report duration)





Key Justification:

Concurrency: Capped at 6 to support the 4 simultaneous report requirements while allowing a safety margin for internal health checks.

Stability: The max-lifetime is set to 20 minutes, ensuring that connections do not expire mid-process during long-running billing queries.

Fail-fast: A 30-second connection-timeout prevents threads from hanging indefinitely if the pool is exhausted.

Queries by Message Type

The following SQL queries extract and summarize Back Billing data per message type (M001–M004).
Each query uses consistent joins between dev-billing-work, dev-billing.BRMCTAS, and dev-billing.BILLING_REPORTS.

🔹 M001 
Summary by Account

SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS FROM [dev-billing-work].dbo.MOVFACTU_MANT AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOM_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M001' AND b.ACTIVATION = 1 WHERE m.MOM_FECHA BETWEEN '20250501' AND '20250531' GROUP BY b.CTA_ID ORDER BY TOTAL_ROWS DESC;

Detailed Data Extraction

SELECT m.MOM_FECHA AS MOM_FECHA, m.MOM_TRADEID AS MOM_TRADEID, m.MOM_ACCOUNT_FACTU AS ACCOUNT_FACTU, b.CTA_ID AS CTA_ID, b.[TYPE] AS TYPE, b.CHANNEL AS CHANNEL, c.CTA_CODCTA AS CTA_CODCTA, c.CTA_IDENT2 AS CTA_IDENT2, c.CTA_TIP_CTA AS CTA_TIP_CTA, m.MOM_CANON AS MOM_CANON, m.MOM_ID_1 AS MOM_ID_1, m.MOM_ID_2 AS MOM_ID_2, m.MOM_IMPORTE AS MOM_IMPORTE FROM [dev-billing-work].dbo.MOVFACTU_MANT AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOM_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M001' AND b.ACTIVATION = 1 WHERE m.MOM_FECHA BETWEEN '20250501' AND '20250531' ORDER BY b.CTA_ID, m.MOM_ACCOUNT_FACTU, m.MOM_TRADEID;

🔹 M002 
Summary by Account

SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS FROM [dev-billing-work].dbo.MOVFACTU AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 WHERE m.MOV_TIPO = 'OTDS' GROUP BY b.CTA_ID ORDER BY TOTAL_ROWS DESC;

Detailed Data Extraction

SELECT m.MOV_ACCOUNT_FACTU AS ACCOUNT_TO_BE_CHARGED, m.MOV_CANON AS MATERIAL, m.MOV_ID_1 AS REPORTING_COUNTER_PARTY, m.MOV_ID_2 AS OTHER_COUNTER_PARTY, m.MOV_TRADEID AS UTI, m.MOV_REPORTING_ID1 AS REPORTING_SUBMIT_ENTITY, m.MOV_FECHA AS MOV_FECHA, b.CTA_ID AS CTA_ID, b.[TYPE] AS TYPE, b.CHANNEL AS CHANNEL, c.CTA_CODCTA AS CTA_CODCTA, c.CTA_IDENT2 AS CTA_IDENT2, c.CTA_TIP_CTA AS CTA_TIP_CTA FROM [dev-billing-work].dbo.MOVFACTU AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 WHERE m.MOV_TIPO = 'OTCS' ORDER BY b.CTA_ID, m.MOV_ACCOUNT_FACTU, m.MOV_TRADEID;

🔹 M003 
Summary by Account

SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS FROM [dev-billing-work].dbo.MOVFACTU AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 WHERE m.MOV_TIPO = 'ETDS' GROUP BY b.CTA_ID ORDER BY TOTAL_ROWS DESC;

Detailed Data Extraction

SELECT m.MOV_ACCOUNT_FACTU AS ACCOUNT_TO_BE_CHARGED, m.MOV_CANON AS MATERIAL, m.MOV_ID_1 AS REPORTING_COUNTER_PARTY, m.MOV_ID_2 AS OTHER_COUNTER_PARTY, m.MOV_TRADEID AS UTI, m.MOV_REPORTING_ID1 AS REPORTING_SUBMIT_ENTITY, m.MOV_FECHA AS MOV_FECHA, b.CTA_ID AS CTA_ID, b.[TYPE] AS TYPE, b.CHANNEL AS CHANNEL, c.CTA_CODCTA AS CTA_CODCTA, c.CTA_IDENT2 AS CTA_IDENT2, c.CTA_TIP_CTA AS CTA_TIP_CTA FROM [dev-billing-work].dbo.MOVFACTU AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOV_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 WHERE m.MOV_TIPO = 'ETDS' ORDER BY b.CTA_ID, m.MOV_ACCOUNT_FACTU, m.MOV_TRADEID;

🔹 M004 
Summary by Account

SELECT b.CTA_ID, COUNT(*) AS TOTAL_ROWS FROM [dev-billing-work].dbo.MOLFACTU AS m INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON m.MOL_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 GROUP BY b.CTA_ID ORDER BY TOTAL_ROWS DESC;

Detailed Data Extraction

SELECT l.MOL_FECHA AS MOL_FECHA, l.MOL_ACCOUNT_FACTU AS ACCOUNT_TO_BE_CHARGED, l.MOL_CANON AS MATERIAL, l.MOL_RSE AS REPORTING_SUBMIT_ENTITY, l.MOL_ID_1 AS REPORTING_COUNTER_PARTY, l.MOL_ERR AS ENTITY_RESPONSIBLE_FOR_REPORTING, l.MOL_QTY AS MOL_QTY, b.CTA_ID AS CTA_ID, b.[TYPE] AS TYPE, b.CHANNEL AS CHANNEL, c.CTA_CODCTA AS CTA_CODCTA, c.CTA_IDENT2 AS CTA_IDENT2, c.CTA_TIP_CTA AS CTA_TIP_CTA FROM [dev-billing-work].dbo.MOLFACTU AS l INNER JOIN [dev-billing].dbo.BRMCTAS AS c ON l.MOL_ACCOUNT_FACTU COLLATE Latin1_General_CI_AS = c.CTA_CODCTA COLLATE Latin1_General_CI_AS INNER JOIN [dev-billing].dbo.BILLING_REPORTS AS b ON b.CTA_ID COLLATE Latin1_General_CI_AS = c.CTA_IDENT2 COLLATE Latin1_General_CI_AS AND b.[TYPE] = 'M002' AND b.ACTIVATION = 1 ORDER BY b.CTA_ID, l.MOL_ACCOUNT_FACTU;




*En las queries falt el filtro de las fechas 

Kafka Topics Overview
EUREFIT Environment

The following Kafka topics are used for Back Billing reusable message processing.
Each topic corresponds to a specific message type or billing process.

Topic Name	Partitions	Replication Factor	Cleanup Policy	Current Size
rft.dev.billing.restricted.clients.reusable.v1	1	4	delete	19.3 MiB
rft.dev.billing.restricted.m001.reusable.v1	1	4	delete	10.2 GiB
rft.dev.billing.restricted.m002.reusable.v1	1	4	delete	8.73 KiB
rft.dev.billing.restricted.m003.reusable.v1	1	4	delete	0 B
rft.dev.billing.restricted.m004.reusable.v1	1	4	delete	15K
rft.dev.filerouter.file.outcoming.reusable.v1	
	
	
	

rft.dev.filerouter.events.private.v1	
	
	
	

UKREFIT Environment




Topic Name	Partitions	Replication Factor	Cleanup Policy	Current Size
ukrefit.dev.billing.restricted.clients.reusable.v1	1	4	delete	0 B
ukrefit.dev.billing.restricted.m001.reusable.v1	1	4	delete	0 B
ukrefit.dev.billing.restricted.m002.reusable.v1	1	4	delete	0 B
ukrefit.dev.billing.restricted.m003.reusable.v1	1	4	delete	0 B
ukrefit.dev.billing.restricted.m004.reusable.v1	1	4	delete	0 B
ukrefit.dev.filerouter.file.outcoming.reusable.v1	
	
	
	

ukrefit.dev.filerouter.events.private.v1	
	
	
	

Advanced Kafka Configuration

Below are the advanced configuration parameters used for Kafka Producers and Consumers in the test environment.

Kafka Producer




Parameter	Description	Value
linger.ms	Wait time before sending a batch of messages	20 ms
batch.size	Maximum batch size	900,000 bytes
buffer.memory	Total memory allocated for buffering	13,430,000,217,728 bytes
request.timeout.ms	Maximum broker response time	30 s
delivery.timeout.ms	Total timeout before reporting an error	120 s
max.block.ms	Maximum blocking time when sending	90 s
Kafka Consumer




Parameter	Description	Value
max.poll.interval.ms	Maximum interval between polls	180,000 ms
max.poll.records	Maximum records per poll	10,000
fetch.min.bytes	Minimum bytes to fetch per request	900,000
fetch.max.wait.ms	Maximum wait time per fetch	1,000 ms
Relevant Fields by Message Type




Tipo	Campo	Descripción
M001	MOM_ACCOUNT_FACTU	Account to be charged

	MOM_CANON	Material

	MOM_ID_1	Reporting counterparty

	MOM_ID_2	Other counterparty

	MOM_TRADEID	UTI

	MOM_REPORTING_ID1	Reporting submitting entity
M002	MOV_ACCOUNT_FACTU	Account to be charged

	MOV_CANON	Material

	MOV_ID_1	Reporting counterparty

	MOV_ID_2	Other counterparty

	MOV_TRADEID	UTI

	MOV_REPORTING_ID1	Reporting submitting entity
M003	MOV_ACCOUNT_FACTU	Account to be charged

	MOV_CANON	Material

	MOV_ID_1	Reporting counterparty

	MOV_ID_2	Other counterparty

	MOV_TRADEID	UTI

	MOV_REPORTING_ID1	Reporting submitting entity
M004	MOL_ACCOUNT_FACTU	Account to be charged

	MOL_CANON	Material

	MOL_RSE	Reporting submitting entity

	MOL_ID_1	Reporting counterparty

	MOV_ERR	Entity responsible for reporting

	MOL_QTY	Quantity




Relevant Fields by Message Type

We have been test differnt days with differnet configuracion and now we have the best performance createing 32.zips with 500.00 files in a csv














