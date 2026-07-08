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
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
var InventoryService_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryService = void 0;
const common_1 = require("@nestjs/common");
const inventory_constants_1 = require("./inventory.constants");
let InventoryService = InventoryService_1 = class InventoryService {
    repository;
    logger = new common_1.Logger(InventoryService_1.name);
    constructor(repository) {
        this.repository = repository;
    }
    async create(item) {
        this.logger.debug(`[CREATE] Processing inventory item creation: ${item.name}`);
        try {
            const createdItem = await this.repository.create(item);
            this.logger.log(`[CREATE] Successfully created inventory item with id: ${createdItem.id}`);
            return createdItem;
        }
        catch (error) {
            this.logger.error(`[CREATE] Error creating inventory item: ${error.message}`);
            throw error;
        }
    }
    async findAll() {
        this.logger.debug('[FIND_ALL] Fetching all inventory items');
        try {
            const items = await this.repository.findAll();
            this.logger.log(`[FIND_ALL] Found ${items.length} inventory items`);
            return items;
        }
        catch (error) {
            this.logger.error(`[FIND_ALL] Error fetching inventory items: ${error.message}`);
            throw error;
        }
    }
    async findById(id) {
        this.logger.debug(`[FIND_BY_ID] Searching for inventory item with id: ${id}`);
        try {
            const item = await this.repository.findById(id);
            if (!item) {
                this.logger.warn(`[FIND_BY_ID] Inventory item not found: ${id}`);
                throw new common_1.NotFoundException(`Inventory item not found: ${id}`);
            }
            this.logger.log(`[FIND_BY_ID] Found inventory item: ${item.name}`);
            return item;
        }
        catch (error) {
            this.logger.error(`[FIND_BY_ID] Error finding inventory item: ${error.message}`);
            throw error;
        }
    }
    async update(id, changes) {
        this.logger.debug(`[UPDATE] Updating inventory item with id: ${id}. Changes: ${JSON.stringify(changes)}`);
        try {
            const item = await this.repository.update(id, changes);
            if (!item) {
                this.logger.warn(`[UPDATE] Inventory item not found for update: ${id}`);
                throw new common_1.NotFoundException(`Inventory item not found: ${id}`);
            }
            this.logger.log(`[UPDATE] Successfully updated inventory item: ${id}`);
            return item;
        }
        catch (error) {
            this.logger.error(`[UPDATE] Error updating inventory item: ${error.message}`);
            throw error;
        }
    }
    async delete(id) {
        this.logger.debug(`[DELETE] Deleting inventory item with id: ${id}`);
        try {
            await this.findById(id);
            await this.repository.delete(id);
            this.logger.log(`[DELETE] Successfully deleted inventory item: ${id}`);
        }
        catch (error) {
            this.logger.error(`[DELETE] Error deleting inventory item: ${error.message}`);
            throw error;
        }
    }
};
exports.InventoryService = InventoryService;
exports.InventoryService = InventoryService = InventoryService_1 = __decorate([
    (0, common_1.Injectable)(),
    __param(0, (0, common_1.Inject)(inventory_constants_1.INVENTORY_REPOSITORY)),
    __metadata("design:paramtypes", [Object])
], InventoryService);
//# sourceMappingURL=inventory.service.js.map