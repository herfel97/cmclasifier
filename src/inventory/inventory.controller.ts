import { Body, Controller, Delete, Get, Logger, Param, Post, Put } from '@nestjs/common';
import { InventoryService } from '../application/inventory.service';
import { CreateInventoryItemDto, UpdateInventoryItemDto } from './dto';

@Controller('inventory')
export class InventoryController {
  private readonly logger = new Logger(InventoryController.name);

  constructor(private readonly inventoryService: InventoryService) {}

  @Post()
  create(@Body() dto: CreateInventoryItemDto) {
    this.logger.log(`Creating new inventory item: ${JSON.stringify(dto)}`);
    return this.inventoryService.create({
      name: dto.name,
      description: dto.description ?? null,
      quantity: dto.quantity,
      price: dto.price,
    });
  }

  @Get()
  findAll() {
    this.logger.log('Fetching all inventory items');
    return this.inventoryService.findAll();
  }

  @Get(':id')
  findOne(@Param('id') id: string) {
    this.logger.log(`Fetching inventory item with id: ${id}`);
    return this.inventoryService.findById(id);
  }

  @Put(':id')
  update(@Param('id') id: string, @Body() dto: UpdateInventoryItemDto) {
    this.logger.log(`Updating inventory item with id: ${id}. Changes: ${JSON.stringify(dto)}`);
    return this.inventoryService.update(id, {
      name: dto.name,
      description: dto.description,
      quantity: dto.quantity,
      price: dto.price,
    });
  }

  @Delete(':id')
  remove(@Param('id') id: string) {
    this.logger.log(`Deleting inventory item with id: ${id}`);
    return this.inventoryService.delete(id);
  }
}
