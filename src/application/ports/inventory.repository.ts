import { InventoryItem } from '../../domain/inventory-item';

export interface InventoryRepository {
  create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem>;
  findAll(): Promise<InventoryItem[]>;
  findById(id: string): Promise<InventoryItem | null>;
  update(id: string, changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>): Promise<InventoryItem | null>;
  delete(id: string): Promise<void>;
}
