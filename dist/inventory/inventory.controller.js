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
var InventoryController_1;
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryController = void 0;
const common_1 = require("@nestjs/common");
const inventory_service_1 = require("../application/inventory.service");
const dto_1 = require("./dto");
let InventoryController = InventoryController_1 = class InventoryController {
    inventoryService;
    logger = new common_1.Logger(InventoryController_1.name);
    constructor(inventoryService) {
        this.inventoryService = inventoryService;
    }
    create(dto) {
        this.logger.log(`Creating new inventory item: ${JSON.stringify(dto)}`);
        return this.inventoryService.create({
            name: dto.name,
            description: dto.description ?? null,
            quantity: dto.quantity,
            price: dto.price,
        });
    }
    findAll() {
        this.logger.log('Fetching all inventory items');
        return this.inventoryService.findAll();
    }
    findOne(id) {
        this.logger.log(`Fetching inventory item with id: ${id}`);
        return this.inventoryService.findById(id);
    }
    update(id, dto) {
        this.logger.log(`Updating inventory item with id: ${id}. Changes: ${JSON.stringify(dto)}`);
        return this.inventoryService.update(id, {
            name: dto.name,
            description: dto.description,
            quantity: dto.quantity,
            price: dto.price,
        });
    }
    remove(id) {
        this.logger.log(`Deleting inventory item with id: ${id}`);
        return this.inventoryService.delete(id);
    }
};
exports.InventoryController = InventoryController;
__decorate([
    (0, common_1.Post)(),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [dto_1.CreateInventoryItemDto]),
    __metadata("design:returntype", void 0)
], InventoryController.prototype, "create", null);
__decorate([
    (0, common_1.Get)(),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", []),
    __metadata("design:returntype", void 0)
], InventoryController.prototype, "findAll", null);
__decorate([
    (0, common_1.Get)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], InventoryController.prototype, "findOne", null);
__decorate([
    (0, common_1.Put)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __param(1, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String, dto_1.UpdateInventoryItemDto]),
    __metadata("design:returntype", void 0)
], InventoryController.prototype, "update", null);
__decorate([
    (0, common_1.Delete)(':id'),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", void 0)
], InventoryController.prototype, "remove", null);
exports.InventoryController = InventoryController = InventoryController_1 = __decorate([
    (0, common_1.Controller)('inventory'),
    __metadata("design:paramtypes", [inventory_service_1.InventoryService])
], InventoryController);
//# sourceMappingURL=inventory.controller.js.map