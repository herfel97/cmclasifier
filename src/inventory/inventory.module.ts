import { Module } from '@nestjs/common';
import { InventoryController } from './inventory.controller';
import { InventoryService } from '../application/inventory.service';
import { DbModule } from '../infrastructure/db/db.module';
import { INVENTORY_REPOSITORY } from '../application/inventory.constants';
import { InventoryPgRepository } from '../infrastructure/db/inventory-pg.repository';

@Module({
  imports: [DbModule],
  controllers: [InventoryController],
  providers: [
    InventoryService,
    {
      provide: INVENTORY_REPOSITORY,
      useClass: InventoryPgRepository,
    },
  ],
})
export class InventoryModule {}
