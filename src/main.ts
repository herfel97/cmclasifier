import * as dotenv from 'dotenv';
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { LoggingInterceptor } from './common/interceptors/logging.interceptor';

// Load environment variables from .env file
if (process.env.NODE_ENV !== 'production') {
  dotenv.config();
}

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  
  // Apply global logging interceptor
  app.useGlobalInterceptors(new LoggingInterceptor());
  
  const port = process.env.PORT ?? 3000;
  await app.listen(port);
  console.log(`✅ Application is running on http://localhost:${port}`);
}
bootstrap();
