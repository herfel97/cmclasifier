import { InventoryRepository } from '../../application/ports/inventory.repository';
import { InventoryItem } from '../../domain/inventory-item';
import { DbService } from './db.service';
export declare class InventoryPgRepository implements InventoryRepository {
    private readonly db;
    private readonly logger;
    constructor(db: DbService);
    private mapToDomain;
    create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem>;
    findAll(): Promise<InventoryItem[]>;
    findById(id: string): Promise<InventoryItem | null>;
    update(id: string, changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>): Promise<InventoryItem | null>;
    delete(id: string): Promise<void>;
}
