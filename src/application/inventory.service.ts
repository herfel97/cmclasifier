import { Inject, Injectable, Logger, NotFoundException } from '@nestjs/common';
import type { InventoryRepository } from './ports/inventory.repository';
import { InventoryItem } from '../domain/inventory-item';
import { INVENTORY_REPOSITORY } from './inventory.constants';

@Injectable()
export class InventoryService {
  private readonly logger = new Logger(InventoryService.name);

  constructor(
    @Inject(INVENTORY_REPOSITORY)
    private readonly repository: InventoryRepository,
  ) {}

  async create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem> {
    this.logger.debug(`[CREATE] Processing inventory item creation: ${item.name}`);
    try {
      const createdItem = await this.repository.create(item);
      this.logger.log(`[CREATE] Successfully created inventory item with id: ${createdItem.id}`);
      return createdItem;
    } catch (error) {
      this.logger.error(`[CREATE] Error creating inventory item: ${error.message}`);
      throw error;
    }
  }

  async findAll(): Promise<InventoryItem[]> {
    this.logger.debug('[FIND_ALL] Fetching all inventory items');
    try {
      const items = await this.repository.findAll();
      this.logger.log(`[FIND_ALL] Found ${items.length} inventory items`);
      return items;
    } catch (error) {
      this.logger.error(`[FIND_ALL] Error fetching inventory items: ${error.message}`);
      throw error;
    }
  }

  async findById(id: string): Promise<InventoryItem> {
    this.logger.debug(`[FIND_BY_ID] Searching for inventory item with id: ${id}`);
    try {
      const item = await this.repository.findById(id);
      if (!item) {
        this.logger.warn(`[FIND_BY_ID] Inventory item not found: ${id}`);
        throw new NotFoundException(`Inventory item not found: ${id}`);
      }
      this.logger.log(`[FIND_BY_ID] Found inventory item: ${item.name}`);
      return item;
    } catch (error) {
      this.logger.error(`[FIND_BY_ID] Error finding inventory item: ${error.message}`);
      throw error;
    }
  }

  async update(
    id: string,
    changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>,
  ): Promise<InventoryItem> {
    this.logger.debug(`[UPDATE] Updating inventory item with id: ${id}. Changes: ${JSON.stringify(changes)}`);
    try {
      const item = await this.repository.update(id, changes);
      if (!item) {
        this.logger.warn(`[UPDATE] Inventory item not found for update: ${id}`);
        throw new NotFoundException(`Inventory item not found: ${id}`);
      }
      this.logger.log(`[UPDATE] Successfully updated inventory item: ${id}`);
      return item;
    } catch (error) {
      this.logger.error(`[UPDATE] Error updating inventory item: ${error.message}`);
      throw error;
    }
  }

  async delete(id: string): Promise<void> {
    this.logger.debug(`[DELETE] Deleting inventory item with id: ${id}`);
    try {
      await this.findById(id);
      await this.repository.delete(id);
      this.logger.log(`[DELETE] Successfully deleted inventory item: ${id}`);
    } catch (error) {
      this.logger.error(`[DELETE] Error deleting inventory item: ${error.message}`);
      throw error;
    }
  }
}
