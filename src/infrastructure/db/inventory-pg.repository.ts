import { Injectable, Logger } from '@nestjs/common';
import { InventoryRepository } from '../../application/ports/inventory.repository';
import { InventoryItem } from '../../domain/inventory-item';
import { DbService } from './db.service';
import { randomUUID } from 'crypto';

@Injectable()
export class InventoryPgRepository implements InventoryRepository {
  private readonly logger = new Logger(InventoryPgRepository.name);

  constructor(private readonly db: DbService) {}

  private mapToDomain(row: any): InventoryItem {
    const createdAt = row.createdAt ?? row.created_at ?? row.created_at;
    const updatedAt = row.updatedAt ?? row.updated_at ?? row.updated_at;
    return new InventoryItem(
      row.id,
      row.name,
      row.description,
      row.quantity,
      parseFloat(row.price),
      createdAt,
      updatedAt,
    );
  }

  async create(item: Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>): Promise<InventoryItem> {
    this.logger.debug(`[DB_CREATE] Inserting inventory item into database: ${item.name}`);
    const pool = this.db.getPool();
    const id = randomUUID();
    const res = await pool.query(
      `INSERT INTO "InventoryItem" (id, name, description, quantity, price, "createdAt", "updatedAt")
       VALUES ($1, $2, $3, $4, $5, now(), now()) RETURNING *`,
      [id, item.name, item.description, item.quantity, item.price],
    );
    return this.mapToDomain(res.rows[0]);
  }

  async findAll(): Promise<InventoryItem[]> {
    this.logger.debug('[DB_FIND_ALL] Querying all inventory items from database');
    const pool = this.db.getPool();
    const res = await pool.query('SELECT * FROM "InventoryItem"');
    return res.rows.map((r) => this.mapToDomain(r));
  }

  async findById(id: string): Promise<InventoryItem | null> {
    this.logger.debug(`[DB_FIND_BY_ID] Querying inventory item from database: ${id}`);
    const pool = this.db.getPool();
    const res = await pool.query('SELECT * FROM "InventoryItem" WHERE id = $1', [id]);
    if (res.rows.length === 0) return null;
    return this.mapToDomain(res.rows[0]);
  }

  async update(
    id: string,
    changes: Partial<Omit<InventoryItem, 'id' | 'createdAt' | 'updatedAt'>>,
  ): Promise<InventoryItem | null> {
    this.logger.debug(`[DB_UPDATE] Updating inventory item in database: ${id}`);
    const pool = this.db.getPool();
    const fields = [] as string[];
    const values = [] as any[];
    let idx = 1;
    if (changes.name !== undefined) { fields.push(`name = $${idx++}`); values.push(changes.name); }
    if (changes.description !== undefined) { fields.push(`description = $${idx++}`); values.push(changes.description); }
    if (changes.quantity !== undefined) { fields.push(`quantity = $${idx++}`); values.push(changes.quantity); }
    if (changes.price !== undefined) { fields.push(`price = $${idx++}`); values.push(changes.price); }
    if (fields.length === 0) return this.findById(id);
    values.push(id);
    const query = `UPDATE "InventoryItem" SET ${fields.join(', ')}, "updatedAt" = now() WHERE id = $${idx} RETURNING *`;
    const res = await pool.query(query, values);
    if (res.rows.length === 0) return null;
    return this.mapToDomain(res.rows[0]);
  }

  async delete(id: string): Promise<void> {
    this.logger.debug(`[DB_DELETE] Deleting inventory item from database: ${id}`);
    const pool = this.db.getPool();
    await pool.query('DELETE FROM "InventoryItem" WHERE id = $1', [id]);
  }
}
