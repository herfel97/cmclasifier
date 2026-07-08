import { Injectable, Logger } from '@nestjs/common';
import { InventoryRepository } from '../../application/ports/inventory.repository';
import { InventoryItem } from '../../domain/inventory-item';
import { PrismaService } from './prisma.service';

@Injectable()
export class InventoryPrismaRepository implements InventoryRepository {
  private readonly logger = new Logger(InventoryPrismaRepository.name);

  constructor(private readonly prisma: PrismaService) {}

  async create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem> {
    this.logger.debug(`[DB_CREATE] Inserting inventory item into database: ${item.name}`);
    try {
      const record = await this.prisma.inventoryItem.create({
        data: {
          name: item.name,
          description: item.description,
          quantity: item.quantity,
          price: item.price,
        },
      });
      this.logger.log(`[DB_CREATE] Successfully inserted item with id: ${record.id}`);
      return this.mapToDomain(record);
    } catch (error) {
      this.logger.error(`[DB_CREATE] Database error: ${error.message}`);
      throw error;
    }
  }

  async findAll(): Promise<InventoryItem[]> {
    this.logger.debug('[DB_FIND_ALL] Querying all inventory items from database');
    try {
      const records = await this.prisma.inventoryItem.findMany();
      this.logger.log(`[DB_FIND_ALL] Retrieved ${records.length} items from database`);
      return records.map((record) => this.mapToDomain(record));
    } catch (error) {
      this.logger.error(`[DB_FIND_ALL] Database error: ${error.message}`);
      throw error;
    }
  }

  async findById(id: string): Promise<InventoryItem | null> {
    this.logger.debug(`[DB_FIND_BY_ID] Querying inventory item from database: ${id}`);
    try {
      const record = await this.prisma.inventoryItem.findUnique({
        where: { id },
      });
      if (record) {
        this.logger.log(`[DB_FIND_BY_ID] Found item: ${record.name}`);
      } else {
        this.logger.warn(`[DB_FIND_BY_ID] Item not found in database: ${id}`);
      }
      return record ? this.mapToDomain(record) : null;
    } catch (error) {
      this.logger.error(`[DB_FIND_BY_ID] Database error: ${error.message}`);
      throw error;
    }
  }

  async update(
    id: string,
    changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>,
  ): Promise<InventoryItem | null> {
    this.logger.debug(`[DB_UPDATE] Updating inventory item in database: ${id}`);
    try {
      const record = await this.prisma.inventoryItem.update({
        where: { id },
        data: {
          name: changes.name,
          description: changes.description,
          quantity: changes.quantity,
          price: changes.price,
        },
      });
      this.logger.log(`[DB_UPDATE] Successfully updated item: ${id}`);
      return this.mapToDomain(record);
    } catch (error) {
      this.logger.error(`[DB_UPDATE] Database error: ${error.message}`);
      throw error;
    }
  }

  async delete(id: string): Promise<void> {
    this.logger.debug(`[DB_DELETE] Deleting inventory item from database: ${id}`);
    try {
      await this.prisma.inventoryItem.delete({
        where: { id },
      });
      this.logger.log(`[DB_DELETE] Successfully deleted item: ${id}`);
    } catch (error) {
      this.logger.error(`[DB_DELETE] Database error: ${error.message}`);
      throw error;
    }
  }

  private mapToDomain(
    record: {
      id: string;
      name: string;
      description: string | null;
      quantity: number;
      price: number;
      createdAt: Date;
      updatedAt: Date;
    },
  ): InventoryItem {
    return new InventoryItem(
      record.id,
      record.name,
      record.description,
      record.quantity,
      record.price,
      record.createdAt,
      record.updatedAt,
    );
  }
}
