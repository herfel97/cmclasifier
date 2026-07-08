export class InventoryItem {
  constructor(
    public readonly id: string,
    public name: string,
    public description: string | null,
    public quantity: number,
    public price: number,
    public readonly createdAt: Date,
    public readonly updatedAt: Date,
  ) {}
}
