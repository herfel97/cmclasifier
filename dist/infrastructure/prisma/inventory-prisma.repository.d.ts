import { InventoryRepository } from '../../application/ports/inventory.repository';
import { InventoryItem } from '../../domain/inventory-item';
import { PrismaService } from './prisma.service';
export declare class InventoryPrismaRepository implements InventoryRepository {
    private readonly prisma;
    private readonly logger;
    constructor(prisma: PrismaService);
    create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem>;
    findAll(): Promise<InventoryItem[]>;
    findById(id: string): Promise<InventoryItem | null>;
    update(id: string, changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>): Promise<InventoryItem | null>;
    delete(id: string): Promise<void>;
    private mapToDomain;
}
