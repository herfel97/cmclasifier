"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.InventoryItem = void 0;
class InventoryItem {
    id;
    name;
    description;
    quantity;
    price;
    createdAt;
    updatedAt;
    constructor(id, name, description, quantity, price, createdAt, updatedAt) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.quantity = quantity;
        this.price = price;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }
}
exports.InventoryItem = InventoryItem;
//# sourceMappingURL=inventory-item.js.map