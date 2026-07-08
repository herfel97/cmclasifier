export declare class InventoryItem {
    readonly id: string;
    name: string;
    description: string | null;
    quantity: number;
    price: number;
    readonly createdAt: Date;
    readonly updatedAt: Date;
    constructor(id: string, name: string, description: string | null, quantity: number, price: number, createdAt: Date, updatedAt: Date);
}
