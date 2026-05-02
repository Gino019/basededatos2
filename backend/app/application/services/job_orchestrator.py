from datetime import datetime
from typing import List

from app.application.schemas import JobCreate, JobResponse
from app.core.exceptions import ResourceNotFoundError
from app.domain.entities.connection import ConnectionConfig
from app.domain.entities.masking_job import MaskingJob, JobStatus
from app.domain.entities.masking_rule import MaskingRule
from app.domain.value_objects.masking_algorithm import MaskingAlgorithm
from app.domain.interfaces.repository import ConnectionRepository, JobRepository, RuleRepository
from app.domain.value_objects.database_type import DatabaseType
from app.infrastructure.db.postgres_client import PostgresClient
from app.infrastructure.db.mongodb_client import MongoClient
from app.infrastructure.masking.strategies import (
    HashingStrategy,
    NullificationStrategy,
    RedactionStrategy,
    SubstitutionStrategy,
)


class JobOrchestrator:
    def __init__(
        self,
        connection_repository: ConnectionRepository,
        rule_repository: RuleRepository,
        job_repository: JobRepository,
    ):
        self._connection_repository = connection_repository
        self._rule_repository = rule_repository
        self._job_repository = job_repository
        self._strategies = {
            MaskingAlgorithm.SUBSTITUTION: SubstitutionStrategy(),
            MaskingAlgorithm.HASHING: HashingStrategy(),
            MaskingAlgorithm.REDACTION: RedactionStrategy(),
            MaskingAlgorithm.NULLIFICATION: NullificationStrategy(),
        }

    async def create_job(self, data: JobCreate, owner_id: str) -> JobResponse:
        connection = await self._connection_repository.get_by_id(data.connection_id)
        if not connection or getattr(connection, "owner_id", None) != owner_id:
            raise ResourceNotFoundError("Connection", data.connection_id)

        for rule_id in data.rule_ids:
            rule = await self._rule_repository.get_by_id(rule_id)
            if not rule or getattr(rule, "owner_id", None) != owner_id:
                raise ResourceNotFoundError("Rule", rule_id)

        job = MaskingJob(connection_id=data.connection_id, rule_ids=data.rule_ids, owner_id=owner_id)
        created = await self._job_repository.create(job)
        return JobResponse.model_validate(created.model_dump())

    async def get_all_jobs(self, owner_id: str) -> List[JobResponse]:
        jobs = await self._job_repository.get_all()
        owned_jobs = [j for j in jobs if getattr(j, "owner_id", None) == owner_id]
        return [JobResponse.model_validate(j.model_dump()) for j in owned_jobs]

    async def get_job(self, id: str, owner_id: str) -> JobResponse:
        job = await self._job_repository.get_by_id(id)
        if not job or getattr(job, "owner_id", None) != owner_id:
            raise ResourceNotFoundError("Job", id)
        return JobResponse.model_validate(job.model_dump())

    async def run_job(self, job_id: str, owner_id: str) -> None:
        job = await self._job_repository.get_by_id(job_id)
        if not job or getattr(job, "owner_id", None) != owner_id:
            raise ResourceNotFoundError("Job", job_id)

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        await self._job_repository.update(job_id, job)

        try:
            connection = await self._connection_repository.get_by_id(job.connection_id)
            if not connection or getattr(connection, "owner_id", None) != owner_id:
                raise ResourceNotFoundError("Connection", job.connection_id)

            rules: List[MaskingRule] = []
            for rule_id in job.rule_ids:
                rule = await self._rule_repository.get_by_id(rule_id)
                if rule and getattr(rule, "owner_id", None) == owner_id:
                    rules.append(rule)

            records_processed = 0
            if connection.type == DatabaseType.POSTGRES:
                dsn = (
                    f"postgresql+asyncpg://{connection.username}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
                )
                client = PostgresClient(dsn)
                records_processed = await self._process_postgres(client, rules)
            else:
                import urllib.parse
                enc_user = urllib.parse.quote_plus(connection.username)
                enc_pass = urllib.parse.quote_plus(connection.password)
                uri = f"mongodb+srv://{enc_user}:{enc_pass}@{connection.host}/"
                client = MongoClient(uri, connection.database)
                records_processed = await self._process_mongodb(client, rules)

            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.records_processed = records_processed
            await self._job_repository.update(job_id, job)
        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.utcnow()
            await self._job_repository.update(job_id, job)

    async def _process_postgres(self, client: PostgresClient, rules: List[MaskingRule]) -> int:
        tables = {rule.target_table for rule in rules}
        processed = 0
        for table in tables:
            table_rules = [rule for rule in rules if rule.target_table == table]
            records = await client.fetch_all(f"SELECT * FROM {table}")
            if not records:
                continue
            pk = "id" if "id" in records[0] else list(records[0].keys())[0]
            for record in records:
                updates = self._build_updates(record, table_rules)
                if updates and pk in record:
                    await client.update_record(table, pk, record[pk], updates)
                    processed += 1
        return processed

    async def _process_mongodb(self, client: MongoClient, rules: List[MaskingRule]) -> int:
        collections = {rule.target_table for rule in rules}
        processed = 0
        for collection in collections:
            records = await client.fetch_all(collection)
            for record in records:
                updates = self._build_updates(record, [rule for rule in rules if rule.target_table == collection])
                if updates:
                    await client.update_record(collection, record["_id"], updates)
                    processed += 1
        return processed

    def _build_updates(self, record: dict, rules: List[MaskingRule]) -> dict:
        updates = {}
        for rule in rules:
            if rule.target_column in record:
                strategy = self._strategies[rule.strategy]
                updates[rule.target_column] = strategy.mask(record[rule.target_column], **(rule.strategy_options or {}))
        return updates


from app.infrastructure.repositories.memory_repository import (
    connection_repository,
    job_repository,
    rule_repository,
)

job_orchestrator = JobOrchestrator(
    connection_repository=connection_repository,
    rule_repository=rule_repository,
    job_repository=job_repository,
)
