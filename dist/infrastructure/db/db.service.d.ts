import { OnModuleDestroy, OnModuleInit } from '@nestjs/common';
import { Pool } from 'pg';
export declare class DbService implements OnModuleInit, OnModuleDestroy {
    private pool;
    constructor();
    onModuleInit(): Promise<void>;
    onModuleDestroy(): Promise<void>;
    getPool(): Pool;
}
