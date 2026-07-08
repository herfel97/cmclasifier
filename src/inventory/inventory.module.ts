import { Module } from '@nestjs/common';
import { InventoryController } from './inventory.controller';
import { InventoryService } from '../application/inventory.service';
import { PrismaModule } from '../infrastructure/prisma/prisma.module';
import { INVENTORY_REPOSITORY } from '../application/inventory.constants';
import { InventoryPrismaRepository } from '../infrastructure/prisma/inventory-prisma.repository';

@Module({
  imports: [PrismaModule],
  controllers: [InventoryController],
  providers: [
    InventoryService,
    {
      provide: INVENTORY_REPOSITORY,
      useClass: InventoryPrismaRepository,
    },
  ],
})
export class InventoryModule {}
