"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var InventoryPgRepository_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryPgRepository = void 0;
const common_1 = require("@nestjs/common");
const inventory_item_1 = require("../../domain/inventory-item");
const db_service_1 = require("./db.service");
const crypto_1 = require("crypto");
let InventoryPgRepository = InventoryPgRepository_1 = class InventoryPgRepository {
    db;
    logger = new common_1.Logger(InventoryPgRepository_1.name);
    constructor(db) {
        this.db = db;
    }
    mapToDomain(row) {
        const createdAt = row.createdAt ?? row.created_at ?? row.created_at;
        const updatedAt = row.updatedAt ?? row.updated_at ?? row.updated_at;
        return new inventory_item_1.InventoryItem(row.id, row.name, row.description, row.quantity, parseFloat(row.price), createdAt, updatedAt);
    }
    async create(item) {
        this.logger.debug(`[DB_CREATE] Inserting inventory item into database: ${item.name}`);
        const pool = this.db.getPool();
        const id = (0, crypto_1.randomUUID)();
        const res = await pool.query(`INSERT INTO "InventoryItem" (id, name, description, quantity, price, "createdAt", "updatedAt")
       VALUES ($1, $2, $3, $4, $5, now(), now()) RETURNING *`, [id, item.name, item.description, item.quantity, item.price]);
        return this.mapToDomain(res.rows[0]);
    }
    async findAll() {
        this.logger.debug('[DB_FIND_ALL] Querying all inventory items from database');
        const pool = this.db.getPool();
        const res = await pool.query('SELECT * FROM "InventoryItem"');
        return res.rows.map((r) => this.mapToDomain(r));
    }
    async findById(id) {
        this.logger.debug(`[DB_FIND_BY_ID] Querying inventory item from database: ${id}`);
        const pool = this.db.getPool();
        const res = await pool.query('SELECT * FROM "InventoryItem" WHERE id = $1', [id]);
        if (res.rows.length === 0)
            return null;
        return this.mapToDomain(res.rows[0]);
    }
    async update(id, changes) {
        this.logger.debug(`[DB_UPDATE] Updating inventory item in database: ${id}`);
        const pool = this.db.getPool();
        const fields = [];
        const values = [];
        let idx = 1;
        if (changes.name !== undefined) {
            fields.push(`name = $${idx++}`);
            values.push(changes.name);
        }
        if (changes.description !== undefined) {
            fields.push(`description = $${idx++}`);
            values.push(changes.description);
        }
        if (changes.quantity !== undefined) {
            fields.push(`quantity = $${idx++}`);
            values.push(changes.quantity);
        }
        if (changes.price !== undefined) {
            fields.push(`price = $${idx++}`);
            values.push(changes.price);
        }
        if (fields.length === 0)
            return this.findById(id);
        values.push(id);
        const query = `UPDATE "InventoryItem" SET ${fields.join(', ')}, "updatedAt" = now() WHERE id = $${idx} RETURNING *`;
        const res = await pool.query(query, values);
        if (res.rows.length === 0)
            return null;
        return this.mapToDomain(res.rows[0]);
    }
    async delete(id) {
        this.logger.debug(`[DB_DELETE] Deleting inventory item from database: ${id}`);
        const pool = this.db.getPool();
        await pool.query('DELETE FROM "InventoryItem" WHERE id = $1', [id]);
    }
};
exports.InventoryPgRepository = InventoryPgRepository;
exports.InventoryPgRepository = InventoryPgRepository = InventoryPgRepository_1 = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [db_service_1.DbService])
], InventoryPgRepository);
//# sourceMappingURL=inventory-pg.repository.js.map