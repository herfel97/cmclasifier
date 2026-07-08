import type { InventoryRepository } from './ports/inventory.repository';
import { InventoryItem } from '../domain/inventory-item';
export declare class InventoryService {
    private readonly repository;
    private readonly logger;
    constructor(repository: InventoryRepository);
    create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem>;
    findAll(): Promise<InventoryItem[]>;
    findById(id: string): Promise<InventoryItem>;
    update(id: string, changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>): Promise<InventoryItem>;
    delete(id: string): Promise<void>;
}
