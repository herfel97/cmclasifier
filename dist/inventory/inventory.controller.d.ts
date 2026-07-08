import { InventoryService } from '../application/inventory.service';
import { CreateInventoryItemDto, UpdateInventoryItemDto } from './dto';
export declare class InventoryController {
    private readonly inventoryService;
    private readonly logger;
    constructor(inventoryService: InventoryService);
    create(dto: CreateInventoryItemDto): Promise<import("../domain/inventory-item").InventoryItem>;
    findAll(): Promise<import("../domain/inventory-item").InventoryItem[]>;
    findOne(id: string): Promise<import("../domain/inventory-item").InventoryItem>;
    update(id: string, dto: UpdateInventoryItemDto): Promise<import("../domain/inventory-item").InventoryItem>;
    remove(id: string): Promise<void>;
}
