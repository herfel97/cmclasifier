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
var InventoryPrismaRepository_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryPrismaRepository = void 0;
const common_1 = require("@nestjs/common");
const inventory_item_1 = require("../../domain/inventory-item");
const prisma_service_1 = require("./prisma.service");
let InventoryPrismaRepository = InventoryPrismaRepository_1 = class InventoryPrismaRepository {
    prisma;
    logger = new common_1.Logger(InventoryPrismaRepository_1.name);
    constructor(prisma) {
        this.prisma = prisma;
    }
    async create(item) {
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
        }
        catch (error) {
            this.logger.error(`[DB_CREATE] Database error: ${error.message}`);
            throw error;
        }
    }
    async findAll() {
        this.logger.debug('[DB_FIND_ALL] Querying all inventory items from database');
        try {
            const records = await this.prisma.inventoryItem.findMany();
            this.logger.log(`[DB_FIND_ALL] Retrieved ${records.length} items from database`);
            return records.map((record) => this.mapToDomain(record));
        }
        catch (error) {
            this.logger.error(`[DB_FIND_ALL] Database error: ${error.message}`);
            throw error;
        }
    }
    async findById(id) {
        this.logger.debug(`[DB_FIND_BY_ID] Querying inventory item from database: ${id}`);
        try {
            const record = await this.prisma.inventoryItem.findUnique({
                where: { id },
            });
            if (record) {
                this.logger.log(`[DB_FIND_BY_ID] Found item: ${record.name}`);
            }
            else {
                this.logger.warn(`[DB_FIND_BY_ID] Item not found in database: ${id}`);
            }
            return record ? this.mapToDomain(record) : null;
        }
        catch (error) {
            this.logger.error(`[DB_FIND_BY_ID] Database error: ${error.message}`);
            throw error;
        }
    }
    async update(id, changes) {
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
        }
        catch (error) {
            this.logger.error(`[DB_UPDATE] Database error: ${error.message}`);
            throw error;
        }
    }
    async delete(id) {
        this.logger.debug(`[DB_DELETE] Deleting inventory item from database: ${id}`);
        try {
            await this.prisma.inventoryItem.delete({
                where: { id },
            });
            this.logger.log(`[DB_DELETE] Successfully deleted item: ${id}`);
        }
        catch (error) {
            this.logger.error(`[DB_DELETE] Database error: ${error.message}`);
            throw error;
        }
    }
    mapToDomain(record) {
        return new inventory_item_1.InventoryItem(record.id, record.name, record.description, record.quantity, record.price, record.createdAt, record.updatedAt);
    }
};
exports.InventoryPrismaRepository = InventoryPrismaRepository;
exports.InventoryPrismaRepository = InventoryPrismaRepository = InventoryPrismaRepository_1 = __decorate([
    (0, common_1.Injectable)(),
    __metadata("design:paramtypes", [prisma_service_1.PrismaService])
], InventoryPrismaRepository);
//# sourceMappingURL=inventory-prisma.repository.js.map